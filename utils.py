import pdfplumber
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# -----------------------------
# SKILLS DATABASE
# -----------------------------
SKILLS_DB = [
    "python","java","sql","machine learning","deep learning",
    "nlp","aws","docker","kubernetes","tensorflow","pytorch",
    "data analysis","spring boot","react","angular"
]

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return text


# -----------------------------
# SKILL EXTRACTION
# -----------------------------
def extract_skills(text):
    text = clean_text(text)
    return [skill for skill in SKILLS_DB if skill in text]


# -----------------------------
# MISSING SKILLS
# -----------------------------
def get_missing_skills(resume_text, job_text):

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    return list(set(job_skills) - set(resume_skills))


# -----------------------------
# SIMPLE ATS SCORE (LIGHTWEIGHT AI)
# -----------------------------
def calculate_match_score(resume_text, job_text):

    docs = [resume_text, job_text]

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(docs)

    score = (tfidf_matrix[0] @ tfidf_matrix[1].T).toarray()[0][0]

    return round(score * 100, 2)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def analyze_resume_job(resume_text, job_text):

    resume_text = clean_text(resume_text)
    job_text = clean_text(job_text)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    missing_skills = list(set(job_skills) - set(resume_skills))

    match_score = calculate_match_score(resume_text, job_text)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "missing_skills": missing_skills,
        "match_score": match_score
    }