import streamlit as st
from job_analyzer import generate_resume_improvements
from pdfminer.high_level import extract_text

st.title("📄 AI Resume Improvement Generator")

job_desc = st.text_area("Paste Job Description")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if job_desc and resume_file:

    resume_text = extract_text(resume_file)

    job_keywords, missing, bullets = generate_resume_improvements(job_desc, resume_text)

    st.subheader("🔥 Important Job Keywords")
    st.write(job_keywords)

    st.subheader("⚠️ Missing Skills in Resume")
    st.write(missing)

    st.subheader("🚀 Suggested Resume Bullet Points")

    for b in bullets:
        st.write("•", b)