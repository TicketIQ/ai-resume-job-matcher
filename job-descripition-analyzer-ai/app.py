import streamlit as st
from job_analyzer import generate_resume_improvements
from pdfminer.high_level import extract_text

st.set_page_config(page_title="AI Resume Optimizer", layout="wide")

st.title("📄 AI Resume Optimizer (AI Powered)")

# -----------------------------
# INPUTS
# -----------------------------
job_desc = st.text_area("📌 Paste Job Description", height=200)

resume_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])


# -----------------------------
# MAIN LOGIC
# -----------------------------
if st.button("Analyze Resume"):

    if not job_desc:
        st.warning("Please paste job description")
        st.stop()

    if not resume_file:
        st.warning("Please upload resume")
        st.stop()

    with st.spinner("Analyzing your resume... ⏳"):

        try:
            resume_text = extract_text(resume_file)

            if not resume_text.strip():
                st.error("Could not extract text from PDF")
                st.stop()

            result = generate_resume_improvements(job_desc, resume_text)

        except Exception as e:
            st.error("Something went wrong while processing the resume")
            st.stop()

    # -----------------------------
    # OUTPUT
    # -----------------------------

    st.success("Analysis Complete ✅")

    # Match Score
    st.subheader("📊 Match Score")
    st.metric(label="ATS Match %", value=f"{result['match_score']}%")

    # Job Skills
    st.subheader("🧠 Extracted Job Skills")
    st.write(", ".join(result["job_skills"]))

    # Missing Skills
    st.subheader("⚠️ Missing Skills")
    if result["missing_skills"]:
        st.write(", ".join(result["missing_skills"]))
    else:
        st.success("No major missing skills 🎉")

    # AI Suggestions
    st.subheader("🚀 AI Resume Suggestions")

    for bullet in result["ai_suggestions"]:
        st.write(bullet)