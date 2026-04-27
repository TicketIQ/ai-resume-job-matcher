from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

# -----------------------------
# Load Hugging Face model
# (recommend upgrading to flan-t5-base later)
# -----------------------------
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)

# -----------------------------
# Extract keywords using TF-IDF
# -----------------------------
def extract_keywords(text, top_n=12):

    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])

    features = np.array(vectorizer.get_feature_names_out())
    sorted_idx = np.argsort(X.toarray()).flatten()[::-1]

    return list(features[sorted_idx][:top_n])


# -----------------------------
# Safe AI bullet generator
# -----------------------------
def generate_bullet(skill, job_context, resume_context):

    prompt = f"""
You are a professional resume writer.

Job context: {job_context}

Candidate resume context: {resume_context}

Write ONE strong, concise resume bullet point for skill: {skill}.
Make it ATS-friendly and impactful.
"""

    try:
        result = generator(prompt, max_new_tokens=60)[0]["generated_text"]

        # -----------------------------
        # CLEAN OUTPUT
        # -----------------------------
        if not result or result.lower().strip() in ["null", "none", ""]:
            return f"• Demonstrated experience in {skill} through relevant projects"

        result = result.strip()

        # Remove prompt leakage or irrelevant text
        if "resume writer" in result.lower():
            result = result.split("\n")[-1]

        return "• " + result

    except Exception:
        return f"• Experience working with {skill} in practical applications"


# -----------------------------
# Match score calculation
# -----------------------------
def calculate_match_score(job_keywords, resume_text):
    resume_text = resume_text.lower()

    matched = sum(1 for k in job_keywords if k in resume_text)

    if len(job_keywords) == 0:
        return 0

    return round((matched / len(job_keywords)) * 100, 2)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_resume_improvements(job_text, resume_text):

    job_keywords = extract_keywords(job_text)

    resume_text_clean = resume_text.lower()

    missing = [k for k in job_keywords if k not in resume_text_clean]

    score = calculate_match_score(job_keywords, resume_text)

    bullets = []

    for skill in missing[:5]:  # limit for stability
        bullet = generate_bullet(skill, job_text, resume_text)
        bullets.append(bullet)

    return {
        "match_score": score,
        "job_keywords": job_keywords,
        "missing_skills": missing,
        "ai_suggestions": bullets
    }