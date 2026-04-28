from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import streamlit as st

# -----------------------------
# LOAD MODELS (cached)
# -----------------------------
@st.cache_resource
def load_llm():
    return pipeline("text2text-generation", model="google/flan-t5-small")

@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

generator = load_llm()
embedder = load_embedder()


# -----------------------------
# CLEANING RULES
# -----------------------------
BAD_WORDS = [
    "ability", "experience", "knowledge", "understanding",
    "demonstrable", "working", "familiarity", "skills",
    "summary", "email", "phone", "github", "education"
]


def clean_skills(skills):
    cleaned = []

    for skill in skills:
        skill = skill.strip().lower()

        # remove long phrases
        if len(skill.split()) > 3:
            continue

        # remove noisy words
        if any(bad in skill for bad in BAD_WORDS):
            continue

        cleaned.append(skill)

    return list(set(cleaned))


# -----------------------------
# STEP 1: SKILL EXTRACTION (LLM)
# -----------------------------
def extract_skills(text):

    prompt = f"""
Extract ONLY technical and domain skills from the text.

RULES:
- Return ONLY comma-separated skills
- Each skill must be 1–3 words max
- DO NOT include sentences or explanations
- DO NOT include personal info or summaries

Example:
python, sql, aws, graphql, genai, machine learning

Text:
{text}
"""

    try:
        result = generator(prompt, max_new_tokens=120)[0]["generated_text"]

        skills = [s.strip().lower() for s in result.split(",") if s.strip()]

        return clean_skills(skills)

    except Exception:
        return []


# -----------------------------
# STEP 2: SEMANTIC MATCHING
# -----------------------------
def find_missing_skills(job_skills, resume_text, threshold=0.5):

    resume_embedding = embedder.encode(resume_text, convert_to_tensor=True)

    missing = []

    for skill in job_skills:
        skill_embedding = embedder.encode(skill, convert_to_tensor=True)
        similarity = util.cos_sim(skill_embedding, resume_embedding).item()

        if similarity < threshold:
            missing.append(skill)

    return missing


# -----------------------------
# STEP 3: MATCH SCORE
# -----------------------------
def calculate_match_score(job_skills, resume_text):

    resume_embedding = embedder.encode(resume_text, convert_to_tensor=True)

    scores = []

    for skill in job_skills:
        skill_embedding = embedder.encode(skill, convert_to_tensor=True)
        sim = util.cos_sim(skill_embedding, resume_embedding).item()
        scores.append(sim)

    if not scores:
        return 0

    return round((sum(scores) / len(scores)) * 100, 2)


# -----------------------------
# STEP 4: BULLET GENERATION (FIXED)
# -----------------------------
def generate_bullet(skill, job_context, resume_context):

    prompt = f"""
You are a senior resume optimization expert.

TASK:
Generate ONE improvement suggestion based on JOB and RESUME.

STRICT RULES:
- DO NOT copy resume text
- DO NOT include name, email, education, or summary
- DO NOT summarize resume
- Focus ONLY on missing skill: {skill}
- Max 20 words
- Start with action verb
- Make it ATS-friendly

JOB:
{job_context[:500]}

RESUME:
{resume_context[:500]}

OUTPUT:
• <improvement suggestion>
"""

    try:
        result = generator(prompt, max_new_tokens=60)[0]["generated_text"].strip()

        # HARD FILTER (prevents bad outputs like summary/email)
        if (
            not result
            or "summary" in result.lower()
            or "email" in result.lower()
            or "phone" in result.lower()
            or len(result.split()) > 30
        ):
            return f"• Improve {skill} by applying it in real-world projects aligned with job requirements"

        if not result.startswith("•"):
            result = "• " + result

        return result

    except Exception:
        return f"• Strengthen {skill} through hands-on project implementation"


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_resume_improvements(job_text, resume_text):

    # limit context (IMPORTANT for stability)
    job_text = job_text[:1500]
    resume_text = resume_text[:1500]

    # 1. Extract skills
    job_skills = extract_skills(job_text)

    # 2. Missing skills
    missing_skills = find_missing_skills(job_skills, resume_text)

    # 3. Match score
    match_score = calculate_match_score(job_skills, resume_text)

    # 4. Generate suggestions (no duplicates)
    suggestions = []
    seen = set()

    for skill in missing_skills[:5]:
        bullet = generate_bullet(skill, job_text, resume_text)

        if bullet not in seen:
            suggestions.append(bullet)
            seen.add(bullet)

    return {
        "match_score": match_score,
        "job_skills": job_skills,
        "missing_skills": missing_skills,
        "ai_suggestions": suggestions
    }