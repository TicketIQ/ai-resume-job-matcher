import streamlit as st
from job_analyzer import analyse                    # ← renamed from generate_resume_improvements
from pdfminer.high_level import extract_text

st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="🎯",
    layout="wide",
)

# ── Custom chip styles ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .skill-chip {
        display: inline-block; padding: 3px 10px;
        border-radius: 20px; font-size: 0.78rem;
        font-weight: 600; margin: 3px;
    }
    .chip-missing { background:#ffe4e4; color:#b91c1c; border:1px solid #fca5a5; }
    .chip-matched { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
    .chip-job     { background:#eff6ff; color:#1d4ed8; border:1px solid #93c5fd; }
</style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Optimizer")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    job_desc = st.text_area("📌 Paste Job Description", height=250)
with col2:
    resume_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

# ── Run analysis ──────────────────────────────────────────────────────────────
if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):

    if not job_desc.strip():
        st.warning("Please paste the job description.")
        st.stop()
    if not resume_file:
        st.warning("Please upload your resume PDF.")
        st.stop()

    with st.spinner("Analyzing your resume… ⏳"):
        try:
            resume_text = extract_text(resume_file)
            if not resume_text.strip():
                st.error("Could not extract text from the PDF. Try a text-based PDF.")
                st.stop()

            result = analyse(job_desc, resume_text)   # ← new function name

        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    # ── Score banner ──────────────────────────────────────────────────────────
    st.success("Analysis complete ✅")

    score = result["match_score"]
    color = "#16a34a" if score >= 75 else "#d97706" if score >= 50 else "#dc2626"

    st.markdown(f"""
    <div style="text-align:center; padding:1.5rem; background:#f8fafc;
                border-radius:12px; margin:1rem 0; border:1px solid #e2e8f0;">
        <div style="font-size:3rem; font-weight:800; color:{color};">{score}%</div>
        <div style="color:#64748b; font-size:0.9rem;">Keyword Match Score</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics row ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Skills in JD",  len(result["job_skills"]))
    c2.metric("Matched",       len(result["matched"]),
              delta=f"+{len(result['matched'])}")
    c3.metric("Missing",       len(result["missing"]),          # ← was "missing_skills"
              delta=f"-{len(result['missing'])}", delta_color="inverse")

    st.divider()

    # ── Missing skills ────────────────────────────────────────────────────────
    st.subheader("⚠️ Missing Skills")
    if result["missing"]:                                        # ← was "missing_skills"
        chips_html = " ".join(
            f'<span class="skill-chip chip-missing">{s}</span>'
            for s in result["missing"]
        )
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.success("No major missing skills 🎉")

    # ── Suggestions ───────────────────────────────────────────────────────────
    st.subheader("🚀 How to Close the Gap")
    for tip in result["suggestions"]:                            # ← was "ai_suggestions"
        st.markdown(f"- {tip}")

    # ── Matched skills ────────────────────────────────────────────────────────
    if result["matched"]:
        with st.expander("✅ Matched Skills", expanded=False):
            chips_html = " ".join(
                f'<span class="skill-chip chip-matched">{s}</span>'
                for s in result["matched"]
            )
            st.markdown(chips_html, unsafe_allow_html=True)

    # ── All JD skills ─────────────────────────────────────────────────────────
    with st.expander("🧠 All Skills Detected in JD", expanded=False):
        chips_html = " ".join(
            f'<span class="skill-chip chip-job">{s}</span>'
            for s in result["job_skills"]
        )
        st.markdown(chips_html, unsafe_allow_html=True)

    # ── Semantic proximity bars ───────────────────────────────────────────────
    if result.get("sem_scores"):
        with st.expander("🔬 Semantic Proximity of Missing Skills", expanded=False):
            st.caption(
                "High % = the concept is already in your resume — just rephrase to use the exact keyword."
            )
            for skill, pct in sorted(
                result["sem_scores"].items(), key=lambda x: x[1], reverse=True
            ):
                bar_color = (
                    "#16a34a" if pct >= 60 else
                    "#d97706" if pct >= 40 else
                    "#dc2626"
                )
                st.markdown(
                    f"""<div style="display:flex;align-items:center;gap:10px;margin:4px 0">
                        <span style="width:130px;font-size:0.82rem">{skill}</span>
                        <div style="flex:1;background:#e2e8f0;border-radius:4px;height:12px">
                          <div style="width:{pct}%;background:{bar_color};
                                      height:12px;border-radius:4px"></div>
                        </div>
                        <span style="font-size:0.8rem;color:#64748b">{pct}%</span>
                    </div>""",
                    unsafe_allow_html=True,
                )