import streamlit as st # pyright: ignore[reportMissingImports]
from utils import *

st.set_page_config(page_title="Resume Matcher", layout="centered")

st.title(" AI Resume Job Matcher")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_desc = st.text_area("Paste Job Description")

if resume_file and job_desc:
    with st.spinner("Analyzing resume..."):

        # Extract text
        resume_text = extract_text_from_pdf(resume_file)

        # Skills
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)

        # Match score
        score = calculate_match(resume_text, job_desc)

        # Missing skills
        missing = missing_skills(resume_skills, job_skills)

    st.success(f" Match Score: {score}%")

    st.subheader(" Resume Skills")
    st.write(resume_skills)

    st.subheader(" Job Skills")
    st.write(job_skills)

    st.subheader(" Missing Skills")
    st.write(missing)