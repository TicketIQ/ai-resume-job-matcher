import streamlit as st
from job_analyzer import analyze_job_description

st.title("Job Description Analyzer AI")

job_desc = st.text_area("Paste Job Description")

if job_desc:

    skills, others, suggestions = analyze_job_description(job_desc)

    st.subheader(" Key Skills Required")
    st.write(skills)

    st.subheader(" Important Keywords")
    st.write(others)

    st.subheader(" Resume Suggestions")
    st.write(suggestions)