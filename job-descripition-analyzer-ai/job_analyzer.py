from sentence_transformers import SentenceTransformer, util
import streamlit as st
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Skill Matcher",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stTextArea textarea { font-size: 0.85rem; }
    .skill-chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 3px;
    }
    .chip-missing  { background: #ffe4e4; color: #b91c1c; border: 1px solid #fca5a5; }
    .chip-matched  { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .chip-job      { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ─────────────────────────────────────────────
# SKILL ALIASES  →  canonical name
# Handles node.js / nodejs / node js → "node.js"
# ─────────────────────────────────────────────
SKILL_ALIASES: dict[str, str] = {
    # Cloud
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "GCP", "google cloud": "GCP", "google cloud platform": "GCP",
    "azure": "Azure", "microsoft azure": "Azure",
    "cloud": "Cloud", "cloud computing": "Cloud",

    # Languages
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript", "js": "JavaScript",
    "typescript": "TypeScript", "ts": "TypeScript",
    "go": "Go", "golang": "Go",
    "rust": "Rust",
    "c++": "C++", "cpp": "C++",
    "c#": "C#", "csharp": "C#",
    "scala": "Scala",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "php": "PHP",
    "r": "R",

    # Frontend
    "react": "React", "react.js": "React", "reactjs": "React",
    "angular": "Angular", "angularjs": "Angular",
    "vue": "Vue.js", "vue.js": "Vue.js", "vuejs": "Vue.js",
    "next.js": "Next.js", "nextjs": "Next.js",
    "html": "HTML", "html5": "HTML",
    "css": "CSS", "css3": "CSS",
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "webpack": "Webpack",
    "redux": "Redux",

    # Backend / Frameworks
    "node": "Node.js", "node.js": "Node.js", "nodejs": "Node.js", "node js": "Node.js",
    "express": "Express.js", "express.js": "Express.js",
    "spring": "Spring Boot", "spring boot": "Spring Boot", "springboot": "Spring Boot",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "graphql": "GraphQL",
    "rest": "REST API", "rest api": "REST API", "restful": "REST API",
    "grpc": "gRPC",
    "microservices": "Microservices",

    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mongodb": "MongoDB", "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch", "elastic search": "Elasticsearch",
    "nosql": "NoSQL",
    "dynamodb": "DynamoDB",
    "oracle": "Oracle DB",
    "sqlite": "SQLite",

    # DevOps / Infrastructure
    "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "helm": "Helm",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "ci/cd": "CI/CD", "cicd": "CI/CD",
    "linux": "Linux", "unix": "Linux",
    "bash": "Bash/Shell", "shell scripting": "Bash/Shell",
    "nginx": "Nginx",
    "apache": "Apache",

    # Data / ML
    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "nlp": "NLP", "natural language processing": "NLP",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn", "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spark": "Apache Spark", "apache spark": "Apache Spark",
    "kafka": "Kafka", "apache kafka": "Kafka",
    "airflow": "Airflow", "apache airflow": "Airflow",
    "data pipeline": "Data Pipelines",
    "etl": "ETL",
    "data engineering": "Data Engineering",

    # Architecture / Process
    "system design": "System Design",
    "api design": "API Design",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",

    # Security / Other
    "oauth": "OAuth",
    "jwt": "JWT",
    "ssl": "SSL/TLS", "tls": "SSL/TLS",
    "cybersecurity": "Cybersecurity",
    "sso": "SSO",
}

# ─────────────────────────────────────────────
# NORMALIZE
# ─────────────────────────────────────────────
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s.#+/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─────────────────────────────────────────────
# EXTRACT SKILLS  (alias-aware, longest-match first)
# ─────────────────────────────────────────────
def extract_skills(text: str) -> dict[str, str]:
    """Return {canonical_name: matched_alias} for every skill found in text."""
    norm = normalize(text)
    found: dict[str, str] = {}

    # Sort aliases longest-first so "spring boot" matches before "spring"
    for alias in sorted(SKILL_ALIASES, key=len, reverse=True):
        canonical = SKILL_ALIASES[alias]
        # word-boundary-aware search
        pattern = r'(?<![a-z0-9])' + re.escape(alias) + r'(?![a-z0-9])'
        if re.search(pattern, norm):
            found[canonical] = alias  # store canonical → alias

    return found   # {canonical: alias}

# ─────────────────────────────────────────────
# MISSING SKILLS
# ─────────────────────────────────────────────
def find_missing_skills(
    job_skills: dict[str, str],
    resume_skills: dict[str, str]
) -> list[str]:
    """Return canonical names present in JD but absent in resume."""
    return [s for s in job_skills if s not in resume_skills]

# ─────────────────────────────────────────────
# MATCH SCORE  (% of JD skills covered)
# ─────────────────────────────────────────────
def calculate_score(job_skills: dict, missing_skills: list) -> float:
    if not job_skills:
        return 0.0
    matched = len(job_skills) - len(missing_skills)
    return round(matched / len(job_skills) * 100, 1)

# ─────────────────────────────────────────────
# SEMANTIC SCORE  (embedding similarity)
# ─────────────────────────────────────────────
def semantic_score(missing: list[str], resume_text: str) -> dict[str, float]:
    """
    For each missing skill, compute cosine similarity against resume.
    A high score means the concept is present even if the exact keyword wasn't.
    """
    if not missing or not resume_text.strip():
        return {}
    resume_emb = model.encode(normalize(resume_text), convert_to_tensor=True)
    scores = {}
    for skill in missing:
        skill_emb = model.encode(skill, convert_to_tensor=True)
        sim = util.cos_sim(skill_emb, resume_emb).item()
        scores[skill] = round(sim * 100, 1)
    return scores

# ─────────────────────────────────────────────
# SUGGESTION  (context-aware templates)
# ─────────────────────────────────────────────
CATEGORY_TIPS: list[tuple[list[str], str]] = [
    (["AWS", "GCP", "Azure", "Cloud"],
     "Get certified: AWS Solutions Architect / Google Associate Cloud Engineer / Azure AZ-900"),
    (["Docker", "Kubernetes", "Helm", "Terraform", "CI/CD"],
     "Build a personal project using Docker + Kubernetes locally with minikube"),
    (["Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch"],
     "Complete fast.ai or Hugging Face NLP course and publish a Kaggle notebook"),
    (["React", "Vue.js", "Next.js", "Angular"],
     "Build and deploy a full front-end project to Vercel with this framework"),
    (["GraphQL", "REST API", "gRPC"],
     "Add a GraphQL or REST API layer to an existing side project"),
    (["SQL", "PostgreSQL", "MySQL", "MongoDB", "NoSQL"],
     "Practice on LeetCode's database track and design a schema for a real use-case"),
    (["Kafka", "Apache Spark", "Airflow", "ETL", "Data Pipelines"],
     "Set up a mini data pipeline locally: ingest → transform → load with Airflow"),
    (["System Design"],
     "Study 'Designing Data-Intensive Applications' and practice on system-design primer"),
    (["Agile", "Scrum", "Jira"],
     "Pursue a PSM I (Professional Scrum Master) certification — free practice exams exist online"),
]

def generate_suggestion(skill: str, sem_score: float) -> str:
    hint = ""
    if sem_score >= 60:
        hint = f" *(semantically close — update your resume wording to include '{skill}')*"

    for keywords, tip in CATEGORY_TIPS:
        if skill in keywords:
            return f"**{skill}**{hint}: {tip}"

    return (
        f"**{skill}**{hint}: Build a small project using {skill}, "
        f"then add it to your resume and GitHub portfolio."
    )

# ─────────────────────────────────────────────
# MAIN ANALYSIS
# ─────────────────────────────────────────────
def analyse(job_text: str, resume_text: str) -> dict:
    job_skills    = extract_skills(job_text)
    resume_skills = extract_skills(resume_text)
    missing       = find_missing_skills(job_skills, resume_skills)
    matched       = [s for s in job_skills if s in resume_skills]
    score         = calculate_score(job_skills, missing)
    sem_scores    = semantic_score(missing, resume_text)

    suggestions = [
        generate_suggestion(s, sem_scores.get(s, 0))
        for s in missing[:10]
    ]

    return {
        "match_score":   score,
        "job_skills":    list(job_skills.keys()),
        "matched":       matched,
        "missing":       missing,
        "sem_scores":    sem_scores,
        "suggestions":   suggestions,
    }

# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────
def chips(skills: list[str], cls: str) -> str:
    return " ".join(
        f'<span class="skill-chip {cls}">{s}</span>' for s in skills
    )

st.title("🎯 Resume Skill Matcher")
st.caption("Paste a job description and your resume below to see exactly which skills are missing.")

col1, col2 = st.columns(2)
with col1:
    job_text = st.text_area("📋 Job Description", height=300,
                            placeholder="Paste the full job posting here…")
with col2:
    resume_text = st.text_area("📄 Your Resume", height=300,
                               placeholder="Paste your resume text here…")

run = st.button("🔍 Analyse", type="primary", use_container_width=True)

if run:
    if not job_text.strip() or not resume_text.strip():
        st.warning("Please paste both a job description and your resume.")
    else:
        with st.spinner("Analysing skills…"):
            result = analyse(job_text, resume_text)

        score = result["match_score"]
        color = "#16a34a" if score >= 75 else "#d97706" if score >= 50 else "#dc2626"

        # ── Score banner ──────────────────────────
        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; background:#f8fafc;
                    border-radius:12px; margin:1rem 0; border:1px solid #e2e8f0;">
            <div style="font-size:3rem; font-weight:800; color:{color};">{score}%</div>
            <div style="color:#64748b; font-size:0.9rem;">Keyword Match Score</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Three-column breakdown ────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Skills in JD",    len(result["job_skills"]))
        c2.metric("Matched",         len(result["matched"]),  delta=f"+{len(result['matched'])}")
        c3.metric("Missing",         len(result["missing"]),  delta=f"-{len(result['missing'])}", delta_color="inverse")

        st.divider()

        # ── Missing skills ────────────────────────
        if result["missing"]:
            st.subheader("❌ Missing Skills")
            st.markdown(chips(result["missing"], "chip-missing"), unsafe_allow_html=True)

            st.subheader("💡 How to Close the Gap")
            for tip in result["suggestions"]:
                st.markdown(f"- {tip}")
        else:
            st.success("✅ Your resume covers all detected skills in the JD!")

        # ── Matched skills ────────────────────────
        if result["matched"]:
            with st.expander("✅ Matched Skills", expanded=False):
                st.markdown(chips(result["matched"], "chip-matched"), unsafe_allow_html=True)

        # ── All JD skills ─────────────────────────
        with st.expander("📋 All Skills Detected in JD", expanded=False):
            st.markdown(chips(result["job_skills"], "chip-job"), unsafe_allow_html=True)

        # ── Semantic proximity table ───────────────
        if result["sem_scores"]:
            with st.expander("🔬 Semantic Proximity of Missing Skills", expanded=False):
                st.caption(
                    "High score = the concept appears in your resume even if the keyword doesn't. "
                    "Consider rewording your resume to use the exact term."
                )
                for skill, pct in sorted(
                    result["sem_scores"].items(), key=lambda x: x[1], reverse=True
                ):
                    bar_color = "#16a34a" if pct >= 60 else "#d97706" if pct >= 40 else "#dc2626"
                    st.markdown(
                        f"""<div style="display:flex;align-items:center;gap:10px;margin:4px 0">
                            <span style="width:130px;font-size:0.82rem">{skill}</span>
                            <div style="flex:1;background:#e2e8f0;border-radius:4px;height:12px">
                              <div style="width:{pct}%;background:{bar_color};height:12px;border-radius:4px"></div>
                            </div>
                            <span style="font-size:0.8rem;color:#64748b">{pct}%</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )