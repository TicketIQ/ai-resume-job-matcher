import streamlit as st
from job_analyzer import generate_resume_improvements
from pdfminer.high_level import extract_text

st.title("📄 AI Resume Optimizer (Hugging Face Powered)")

job_desc = st.text_area("Paste Job Description")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if job_desc and resume_file:

    resume_text = extract_text(resume_file)

    result = generate_resume_improvements(job_desc, resume_text)

    st.subheader("📊 Match Score")
    st.metric(label="ATS Match %", value=f"{result['match_score']}%")

    st.subheader("🔥 Job Keywords")
    st.write(result["job_keywords"])

    st.subheader("⚠️ Missing Skills")
    st.write(result["missing_skills"])

    st.subheader("🚀 AI Generated Resume Points")

    for b in result["ai_suggestions"]:
        if b:   # extra safety
            st.write(b)