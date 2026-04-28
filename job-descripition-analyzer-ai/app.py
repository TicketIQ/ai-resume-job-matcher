import streamlit as st
from job_analyzer import analyse
from pdfminer.high_level import extract_text
import anthropic

st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
    .skill-chip {
        display: inline-block; padding: 3px 10px;
        border-radius: 20px; font-size: 0.78rem;
        font-weight: 600; margin: 3px;
    }
    .chip-missing  { background:#ffe4e4; color:#b91c1c; border:1px solid #fca5a5; }
    .chip-matched  { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
    .chip-job      { background:#eff6ff; color:#1d4ed8; border:1px solid #93c5fd; }
    .chip-nice     { background:#fef9c3; color:#854d0e; border:1px solid #fde047; }
    .chip-soft-ok  { background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; }
    .chip-soft-gap { background:#fff7ed; color:#9a3412; border:1px solid #fed7aa; }
    .section-card {
        background:#f8fafc; border-radius:10px;
        padding:1rem 1.25rem; margin-bottom:0.5rem;
        border:1px solid #e2e8f0;
    }
    .tailor-box {
        background:#f0f9ff; border-radius:10px;
        padding:1.25rem; border:1px solid #bae6fd;
        white-space: pre-wrap; font-size: 0.88rem;
        line-height: 1.7; color: #0c4a6e;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 AI Resume Optimizer")
st.caption("Full resume analysis: tech skills, education, experience, soft skills & nice-to-haves.")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    job_desc = st.text_area("📌 Paste Job Description", height=280)
with col2:
    resume_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

run = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

if run:
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
            result = analyse(job_desc, resume_text)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    # Store results and resume text in session state for the tailor section
    st.session_state["result"]      = result
    st.session_state["resume_text"] = resume_text
    st.session_state["job_desc"]    = job_desc

# ── Only render results if analysis has been run ──────────────────────────────
if "result" not in st.session_state:
    st.stop()

result      = st.session_state["result"]
resume_text = st.session_state["resume_text"]
job_desc    = st.session_state["job_desc"]

st.success("Analysis complete ✅")

def chips(skills, cls):
    return " ".join(
        f'<span class="skill-chip {cls}">{s}</span>' for s in skills
    )

# ════════════════════════════════════════════════════════════════════════
# SECTION 1 — MATCH SCORE
# ════════════════════════════════════════════════════════════════════════
score = result["match_score"]
color = "#16a34a" if score >= 75 else "#d97706" if score >= 50 else "#dc2626"

st.markdown(f"""
<div style="text-align:center; padding:1.5rem; background:#f8fafc;
            border-radius:12px; margin:1rem 0; border:1px solid #e2e8f0;">
    <div style="font-size:3rem; font-weight:800; color:{color};">{score}%</div>
    <div style="color:#64748b; font-size:0.9rem;">Technical Keyword Match Score</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Required Skills in JD", len(result["job_skills"]))
c2.metric("Matched",               len(result["matched"]),
          delta=f"+{len(result['matched'])}")
c3.metric("Missing",               len(result["missing"]),
          delta=f"-{len(result['missing'])}", delta_color="inverse")

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 2 — EDUCATION
# ════════════════════════════════════════════════════════════════════════
st.subheader("🎓 Education Requirement")

edu           = result["edu_result"]
edu_required  = result["edu_required"]  or "Not specified"
edu_candidate = result["edu_candidate"] or "Not detected in resume"

ecol1, ecol2 = st.columns(2)
ecol1.info(f"**JD Requires:** {edu_required}")
ecol2.info(f"**Your Resume:** {edu_candidate}")

if edu["status"] == "ok":
    st.success(edu["message"])
elif edu["status"] == "gap":
    st.warning(edu["message"])
else:
    st.error(edu["message"])

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 3 — EXPERIENCE YEARS
# ════════════════════════════════════════════════════════════════════════
st.subheader("🗓️ Experience Requirements")

exp_reqs     = result["exp_requirements"]
resume_years = result["resume_exp_years"]

if resume_years is not None:
    st.info(
        f"**Estimated experience in your resume:** ~{resume_years} years "
        f"(calculated from date ranges found in the resume)"
    )
else:
    st.warning("Could not detect date ranges in your resume to estimate total experience.")

if exp_reqs:
    for req in exp_reqs:
        yr   = req["years"]
        ctx  = req["context"]
        icon = "✅" if (resume_years and resume_years >= yr) else "⚠️"
        st.markdown(
            f'<div class="section-card">'
            f'{icon} <b>{yr}+ years</b> of {ctx}'
            f'</div>',
            unsafe_allow_html=True
        )
else:
    st.caption("No specific 'X+ years' requirements found in the JD.")

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 4 — MISSING TECH SKILLS
# ════════════════════════════════════════════════════════════════════════
st.subheader("⚠️ Missing Required Tech Skills")

if result["missing"]:
    st.markdown(chips(result["missing"], "chip-missing"), unsafe_allow_html=True)
    st.subheader("💡 How to Close the Gap")
    for tip in result["suggestions"]:
        st.markdown(f"- {tip}")
else:
    st.success("✅ Your resume covers all detected required tech skills!")

if result["matched"]:
    with st.expander("✅ Matched Required Tech Skills", expanded=False):
        st.markdown(chips(result["matched"], "chip-matched"), unsafe_allow_html=True)

with st.expander("🧠 All Required Tech Skills in JD", expanded=False):
    st.markdown(chips(result["job_skills"], "chip-job"), unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 5 — NICE-TO-HAVE SKILLS
# ════════════════════════════════════════════════════════════════════════
if result["nice_skills"]:
    st.subheader("⭐ Nice-to-Have Skills")

    nc1, nc2 = st.columns(2)
    nc1.metric("Nice-to-Have in JD", len(result["nice_skills"]))
    nc2.metric("You Already Have",   len(result["nice_matched"]),
               delta=f"+{len(result['nice_matched'])}")

    if result["nice_missing"]:
        st.markdown("**Missing nice-to-haves:**")
        st.markdown(chips(result["nice_missing"], "chip-nice"), unsafe_allow_html=True)

    if result["nice_matched"]:
        with st.expander("⭐ Nice-to-Haves You Already Have", expanded=False):
            st.markdown(chips(result["nice_matched"], "chip-matched"), unsafe_allow_html=True)

    st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 6 — SOFT SKILLS
# ════════════════════════════════════════════════════════════════════════
st.subheader("🤝 Soft Skills & Traits")

if result["jd_soft_skills"]:
    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("**Mentioned in JD:**")
        st.markdown(chips(result["jd_soft_skills"], "chip-job"), unsafe_allow_html=True)
    with scol2:
        if result["matched_soft"]:
            st.markdown("**Detected in your resume:**")
            st.markdown(chips(result["matched_soft"], "chip-soft-ok"), unsafe_allow_html=True)

    if result["missing_soft"]:
        st.markdown("**Not detected — consider adding to your resume:**")
        st.markdown(chips(result["missing_soft"], "chip-soft-gap"), unsafe_allow_html=True)
        st.caption(
            "Tip: Soft skills surface through action words — "
            "'led', 'collaborated', 'presented', 'aligned stakeholders', 'drove strategy'."
        )
    else:
        st.success("✅ Your resume reflects all soft skills mentioned in the JD.")
else:
    st.caption("No specific soft skills detected in this JD.")

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 7 — SEMANTIC PROXIMITY
# ════════════════════════════════════════════════════════════════════════
if result.get("sem_scores"):
    with st.expander("🔬 Semantic Proximity of Missing Tech Skills", expanded=False):
        st.caption(
            "High % = concept is already in your resume — "
            "just rephrase to use the exact keyword."
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
                    <span style="width:160px;font-size:0.82rem">{skill}</span>
                    <div style="flex:1;background:#e2e8f0;border-radius:4px;height:12px">
                      <div style="width:{pct}%;background:{bar_color};
                                  height:12px;border-radius:4px"></div>
                    </div>
                    <span style="font-size:0.8rem;color:#64748b">{pct}%</span>
                </div>""",
                unsafe_allow_html=True,
            )

st.divider()

# ════════════════════════════════════════════════════════════════════════
# SECTION 8 — TAILOR MY RESUME  (Claude API)
# ════════════════════════════════════════════════════════════════════════
st.subheader("✍️ Tailor My Resume with AI")
st.caption(
    "Claude will rewrite your resume bullet points and suggest new ones "
    "to address every gap found above."
)

# API key input — reads from st.secrets first, falls back to manual entry
try:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    api_key = ""

if not api_key:
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com → API Keys. "
             "On Hugging Face, add it in Space Settings → Repository secrets as ANTHROPIC_API_KEY.",
    )

tailor_mode = st.radio(
    "What would you like to tailor?",
    ["Full resume rewrite", "Only missing skill bullets", "Summary / objective statement"],
    horizontal=True,
)

if st.button("✨ Generate Tailored Resume", type="primary", use_container_width=True):
    if not api_key:
        st.warning("Please enter your Anthropic API key.")
        st.stop()

    # Build gap summary for the prompt
    missing_tech  = ", ".join(result["missing"])        or "None"
    missing_soft  = ", ".join(result["missing_soft"])   or "None"
    missing_nice  = ", ".join(result["nice_missing"])   or "None"
    edu_gap_msg   = result["edu_result"]["message"]
    exp_gaps      = "\n".join(
        f"- {r['years']}+ years of {r['context']}"
        for r in result["exp_requirements"]
    ) or "None specified"

    mode_instruction = {
        "Full resume rewrite": (
            "Rewrite the ENTIRE resume — summary, skills section, and ALL work experience "
            "bullet points — to be strongly tailored for this job."
        ),
        "Only missing skill bullets": (
            "Only add or rewrite bullet points that address the missing skills. "
            "Keep everything else unchanged."
        ),
        "Summary / objective statement": (
            "Write ONLY a new professional summary / objective statement (4–6 sentences) "
            "tailored for this specific role."
        ),
    }[tailor_mode]

    prompt = f"""You are an expert resume writer and career coach.

JOB DESCRIPTION:
{job_desc[:3000]}

CANDIDATE'S CURRENT RESUME:
{resume_text[:3000]}

GAP ANALYSIS:
- Missing tech skills: {missing_tech}
- Missing soft skills / traits: {missing_soft}
- Missing nice-to-have skills: {missing_nice}
- Education gap: {edu_gap_msg}
- Experience requirements:
{exp_gaps}

TASK:
{mode_instruction}

RULES:
1. Use strong action verbs (built, led, designed, deployed, optimised, collaborated).
2. Quantify achievements wherever possible (%, $, users, latency, etc.).
3. Naturally incorporate the missing skills where the candidate's background makes it plausible.
4. For skills the candidate clearly does not have, add a dedicated "Currently Learning" or
   "In Progress" section instead of fabricating experience.
5. Keep the tone professional and ATS-friendly.
6. Output clean plain text, ready to paste into a document.
7. Use this structure:
   ## PROFESSIONAL SUMMARY
   ## SKILLS
   ## WORK EXPERIENCE
   ## EDUCATION
   ## CURRENTLY LEARNING  (only if there are genuinely missing skills)
"""

    with st.spinner("Claude is tailoring your resume… ✍️"):
        try:
            client   = anthropic.Anthropic(api_key=api_key)
            message  = client.messages.create(
                model      = "claude-opus-4-5",
                max_tokens = 2000,
                messages   = [{"role": "user", "content": prompt}],
            )
            tailored = message.content[0].text
            st.session_state["tailored_resume"] = tailored
        except anthropic.AuthenticationError:
            st.error("Invalid API key. Check your key at console.anthropic.com.")
            st.stop()
        except Exception as e:
            st.error(f"Claude API error: {e}")
            st.stop()

# Show output if it exists in session state
if "tailored_resume" in st.session_state:
    tailored = st.session_state["tailored_resume"]

    st.markdown("### 📄 Your Tailored Resume")
    st.markdown(
        f'<div class="tailor-box">{tailored}</div>',
        unsafe_allow_html=True
    )

    # Download button
    st.download_button(
        label      = "⬇️ Download as .txt",
        data       = tailored,
        file_name  = "tailored_resume.txt",
        mime       = "text/plain",
        use_container_width=True,
    )

    st.caption(
        "💡 Tip: Paste this into Google Docs or Word, then format it. "
        "The 'Currently Learning' section shows honest upskilling intent — "
        "many hiring managers appreciate transparency."
    )