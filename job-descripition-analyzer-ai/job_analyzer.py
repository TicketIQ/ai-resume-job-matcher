from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import streamlit as st

# -----------------------------
# Load Models (cached for speed)
# -----------------------------
@st.cache_resource
def load_llm():
    return pipeline("text2text-generation", model="google/flan-t5-small")

@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

generator = load_llm()
embedder = load_embedder()


# -----------------------------
# STEP 1: Extract skills using LLM
# -----------------------------
def extract_skills(text):

    prompt = f"""
Extract all important technical and domain skills from the text below.
Include both required and optional ("nice to have") skills.
Return ONLY a comma-separated list.

Text:
{text}
"""

    try:
        result = generator(prompt, max_new_tokens=120)[0]["generated_text"]

        skills = [s.strip().lower() for s in result.split(",") if len(s.strip()) > 2]

        return list(set(skills))

    except Exception:
        return []


# -----------------------------
# STEP 2: Semantic skill matching
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
# STEP 3: Match Score (semantic)
# -----------------------------
def calculate_match_score(job_skills, resume_text):

    resume_embedding = embedder.encode(resume_text, convert_to_tensor=True)

    scores = []

    for skill in job_skills:
        skill_embedding = embedder.encode(skill, convert_to_tensor=True)
        sim = util.cos_sim(skill_embedding, resume_embedding).item()
        scores.append(sim)

    if len(scores) == 0:
        return 0

    return round((sum(scores) / len(scores)) * 100, 2)


# -----------------------------
# STEP 4: AI Bullet Generator
# -----------------------------
def generate_bullet(skill, job_context, resume_context):

    prompt = f"""
You are a professional resume writer.

Job context:
{job_context}

Candidate resume:
{resume_context}

Write ONE strong resume bullet for skill: {skill}.
Make it concise, impactful, and ATS-friendly.
"""

    try:
        result = generator(prompt, max_new_tokens=60)[0]["generated_text"].strip()

        if not result:
            return f"• Demonstrated experience in {skill} through relevant projects"

        return "• " + result

    except Exception:
        return f"• Experience working with {skill} in real-world scenarios"


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_resume_improvements(job_text, resume_text):

    # 1. Extract job skills
    job_skills = extract_skills(job_text)

    # 2. Find missing skills (semantic)
    missing_skills = find_missing_skills(job_skills, resume_text)

    # 3. Match score
    match_score = calculate_match_score(job_skills, resume_text)

    # 4. Generate suggestions (limit for performance)
    suggestions = []

    for skill in missing_skills[:5]:
        bullet = generate_bullet(skill, job_text, resume_text)
        suggestions.append(bullet)

    return {
        "match_score": match_score,
        "job_skills": job_skills,
        "missing_skills": missing_skills,
        "ai_suggestions": suggestions
    }