from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

# -----------------------------
# Load Hugging Face model (clean + instruction-based)
# -----------------------------
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)

# -----------------------------
# Extract keywords
# -----------------------------
def extract_keywords(text, top_n=12):

    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])

    features = np.array(vectorizer.get_feature_names_out())
    sorted_idx = np.argsort(X.toarray()).flatten()[::-1]

    return list(features[sorted_idx][:top_n])


# -----------------------------
# Generate CLEAN resume bullets
# -----------------------------
def generate_bullet(skill, job_context, resume_context):

    prompt = f"""
You are a professional resume writer.

Job context: {job_context}

Candidate resume context: {resume_context}

Write ONE professional resume bullet point for skill: {skill}
Make it short, impactful, ATS friendly.
"""

    result = generator(prompt, max_new_tokens=60)[0]["generated_text"]

    return "• " + result.strip()


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_resume_improvements(job_text, resume_text):

    job_keywords = extract_keywords(job_text)

    resume_text_clean = resume_text.lower()

    missing = [k for k in job_keywords if k not in resume_text_clean]

    bullets = []

    for skill in missing[:5]:  # limit to avoid overload
        bullet = generate_bullet(skill, job_text, resume_text)
        bullets.append(bullet)

    return job_keywords, missing, bullets