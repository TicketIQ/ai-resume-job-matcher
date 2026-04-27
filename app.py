import streamlit as st
from utils import (
    extract_text_from_pdf,
    analyze_resume_job
)

st.set_page_config(page_title="AI Resume System", layout="centered")

st.title("📄 Lightweight AI Resume Matcher")

st.write("Upload your resume and paste job description to get ATS score.")

job_text = st.text_area("📌 Job Description")

resume_file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"])

if job_text and resume_file:

    resume_text = extract_text_from_pdf(resume_file)

    result = analyze_resume_job(resume_text, job_text)

    st.subheader("📊 ATS Match Score")
    st.success(f"{result['match_score']} / 100")

    st.subheader("🧠 Resume Skills")
    st.write(result["resume_skills"])

    st.subheader("📌 Job Skills")
    st.write(result["job_skills"])

    st.subheader("⚠️ Missing Skills")
    st.write(result["missing_skills"])