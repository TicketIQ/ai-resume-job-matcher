from sentence_transformers import SentenceTransformer, util
from typing import Optional
import streamlit as st
import re

# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ─────────────────────────────────────────────
# SKILL ALIASES  →  canonical name
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
    "sql": "SQL",
    "bash": "Bash/Shell", "shell scripting": "Bash/Shell",

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
    "langchain": "LangChain",

    # Databases
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
    "nginx": "Nginx",
    "apache": "Apache",
    "mlops": "MLOps",

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
    "causal inference": "Causal Inference",
    "embeddings": "Embeddings",
    "forecasting": "Forecasting",
    "recommendation": "Recommendation Systems", "recommender": "Recommendation Systems",
    "a/b testing": "A/B Testing", "ab testing": "A/B Testing",
    "feature engineering": "Feature Engineering",
    "model deployment": "Model Deployment",
    "llm": "LLMs", "large language model": "LLMs",

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
# EDUCATION LEVELS  (ordered highest → lowest)
# ─────────────────────────────────────────────
EDUCATION_PATTERNS = [
    ("Ph.D.",    [r"ph\.?d", r"doctorate", r"doctoral"]),
    ("Master's", [r"master'?s?", r"m\.s\.?", r"msc", r"m\.eng"]),
    ("Bachelor's",[r"bachelor'?s?", r"b\.s\.?", r"b\.e\.?", r"undergraduate"]),
]

def extract_education_requirement(text: str) -> Optional[str]:
    norm = text.lower()
    for level, patterns in EDUCATION_PATTERNS:
        for p in patterns:
            if re.search(p, norm):
                return level
    return None

def extract_resume_education(text: str) -> Optional[str]:
    norm = text.lower()
    for level, patterns in EDUCATION_PATTERNS:
        for p in patterns:
            if re.search(p, norm):
                return level
    return None

EDUCATION_RANK = {"Ph.D.": 3, "Master's": 2, "Bachelor's": 1, None: 0}

def education_gap(required: Optional[str], candidate: Optional[str]) -> dict:
    req_rank = EDUCATION_RANK.get(required, 0)
    can_rank = EDUCATION_RANK.get(candidate, 0)
    if required is None:
        return {"status": "ok", "message": "No specific degree required."}
    if candidate is None:
        return {"status": "missing", "message": f"JD requires {required}; none detected in resume."}
    if can_rank >= req_rank:
        return {"status": "ok", "message": f"✅ {candidate} meets the {required} requirement."}
    return {"status": "gap", "message": f"⚠️ JD requires {required}; resume shows {candidate}."}

# ─────────────────────────────────────────────
# EXPERIENCE YEARS
# ─────────────────────────────────────────────
def extract_experience_requirements(text: str) -> list[dict]:
    """
    Find all 'X+ years of ...' patterns and return structured list.
    E.g. [{"years": 5, "context": "leading complex, end-to-end ML projects"}]
    """
    pattern = re.compile(
        r'(\d+)\+?\s*years?\s+of\s+([^.\n]{10,80})',
        re.IGNORECASE
    )
    results = []
    for m in pattern.finditer(text):
        years = int(m.group(1))
        context = m.group(2).strip().rstrip(',;')
        results.append({"years": years, "context": context})
    return results

def extract_resume_total_experience(text: str) -> Optional[int]:
    """
    Estimate years of experience from resume by finding date ranges.
    Looks for patterns like '2018 - 2023' or '2020 – present'.
    """
    import datetime
    current_year = datetime.datetime.now().year
    year_pattern = re.compile(r'(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|present|current|now)',
                              re.IGNORECASE)
    matches = year_pattern.findall(text)
    if not matches:
        return None
    total = 0
    for start_str, end_str in matches:
        try:
            start = int(start_str)
            end = current_year if re.search(r'present|current|now', end_str, re.IGNORECASE) else int(end_str)
            if 1990 <= start <= current_year and start <= end:
                total += (end - start)
        except ValueError:
            pass
    return total if total > 0 else None

# ─────────────────────────────────────────────
# SOFT SKILLS
# ─────────────────────────────────────────────
SOFT_SKILL_PATTERNS: dict[str, list[str]] = {
    "Cross-functional collaboration": [
        "cross-functional", "stakeholder", "liaison", "align", "collaborate",
        "bridge", "partner with", "coordination"
    ],
    "Research & prototyping": [
        "research", "prototype", "paper", "experiment", "innovation",
        "proof of concept", "poc"
    ],
    "Leadership & mentorship": [
        "lead", "mentor", "guide", "coach", "manage team", "team lead",
        "technical lead", "architect"
    ],
    "Communication & presentation": [
        "present", "communicate", "documentation", "report", "translate",
        "explain", "written", "verbal"
    ],
    "Business acumen": [
        "business objective", "product need", "revenue", "roi", "roadmap",
        "strategy", "impact", "end-customer"
    ],
    "Ambiguity & zero-to-one": [
        "zero-to-one", "ambiguity", "fast-paced", "startup", "greenfield",
        "define standards", "new domain", "freedom to choose"
    ],
    "Causal & analytical thinking": [
        "causal inference", "hypothesis", "rigorous", "quantitative",
        "statistical", "analytical", "a/b test", "experimentation"
    ],
}

def extract_soft_skills(text: str) -> list[str]:
    norm = text.lower()
    found = []
    for skill, keywords in SOFT_SKILL_PATTERNS.items():
        if any(kw in norm for kw in keywords):
            found.append(skill)
    return found

# ─────────────────────────────────────────────
# NICE-TO-HAVE SECTION DETECTION
# ─────────────────────────────────────────────
def split_nice_to_have(text: str) -> tuple[str, str]:
    """
    Split JD into required and nice-to-have sections.
    Returns (required_text, nice_to_have_text).
    """
    pattern = re.compile(
        r'(nice[\s\-]to[\s\-]have|preferred|bonus|plus|optional|good to have)',
        re.IGNORECASE
    )
    m = pattern.search(text)
    if m:
        return text[:m.start()], text[m.start():]
    return text, ""

# ─────────────────────────────────────────────
# NORMALIZE
# ─────────────────────────────────────────────
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s.#+/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─────────────────────────────────────────────
# EXTRACT TECH SKILLS  (alias-aware, longest-match first)
# ─────────────────────────────────────────────
def extract_skills(text: str) -> dict[str, str]:
    norm = normalize(text)
    found: dict[str, str] = {}
    for alias in sorted(SKILL_ALIASES, key=len, reverse=True):
        canonical = SKILL_ALIASES[alias]
        pattern = r'(?<![a-z0-9])' + re.escape(normalize(alias)) + r'(?![a-z0-9])'
        if re.search(pattern, norm):
            found[canonical] = alias
    return found

# ─────────────────────────────────────────────
# MISSING SKILLS
# ─────────────────────────────────────────────
def find_missing_skills(job_skills: dict, resume_skills: dict) -> list[str]:
    return [s for s in job_skills if s not in resume_skills]

# ─────────────────────────────────────────────
# MATCH SCORE
# ─────────────────────────────────────────────
def calculate_score(job_skills: dict, missing_skills: list) -> float:
    if not job_skills:
        return 0.0
    matched = len(job_skills) - len(missing_skills)
    return round(matched / len(job_skills) * 100, 1)

# ─────────────────────────────────────────────
# SEMANTIC SCORE
# ─────────────────────────────────────────────
def semantic_score(missing: list[str], resume_text: str) -> dict[str, float]:
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
# SUGGESTIONS
# ─────────────────────────────────────────────
CATEGORY_TIPS: list[tuple[list[str], str]] = [
    (["AWS", "GCP", "Azure", "Cloud"],
     "Get certified: AWS Solutions Architect / Google Associate Cloud Engineer / Azure AZ-900"),
    (["Docker", "Kubernetes", "Helm", "Terraform", "CI/CD", "MLOps"],
     "Build a personal project using Docker + Kubernetes locally with minikube"),
    (["Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "LLMs", "LangChain"],
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
    (["Causal Inference"],
     "Read 'The Book of Why' (Pearl) and implement a causal DAG project using DoWhy"),
    (["Embeddings", "Recommendation Systems", "Forecasting"],
     "Build an end-to-end ML project on Kaggle or publish on GitHub using these concepts"),
    (["A/B Testing"],
     "Study Kohavi's 'Trustworthy Online Controlled Experiments' and run a mock experiment"),
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
    # ── Split required vs nice-to-have ───────
    required_text, nice_text = split_nice_to_have(job_text)

    # ── Tech skills ───────────────────────────
    job_skills       = extract_skills(required_text)
    nice_skills      = extract_skills(nice_text) if nice_text else {}
    resume_skills    = extract_skills(resume_text)

    missing          = find_missing_skills(job_skills, resume_skills)
    matched          = [s for s in job_skills if s in resume_skills]
    nice_missing     = [s for s in nice_skills if s not in resume_skills]
    nice_matched     = [s for s in nice_skills if s in resume_skills]

    score            = calculate_score(job_skills, missing)
    sem_scores       = semantic_score(missing, resume_text)

    suggestions = [
        generate_suggestion(s, sem_scores.get(s, 0))
        for s in missing[:10]
    ]

    # ── Education ─────────────────────────────
    edu_required  = extract_education_requirement(required_text)
    edu_candidate = extract_resume_education(resume_text)
    edu_result    = education_gap(edu_required, edu_candidate)

    # ── Experience years ─────────────────────
    exp_requirements = extract_experience_requirements(job_text)
    resume_exp_years = extract_resume_total_experience(resume_text)

    # ── Soft skills ───────────────────────────
    jd_soft_skills     = extract_soft_skills(job_text)
    resume_soft_skills = extract_soft_skills(resume_text)
    missing_soft       = [s for s in jd_soft_skills if s not in resume_soft_skills]
    matched_soft       = [s for s in jd_soft_skills if s in resume_soft_skills]

    return {
        # Tech skills
        "match_score":      score,
        "job_skills":       list(job_skills.keys()),
        "matched":          matched,
        "missing":          missing,
        "sem_scores":       sem_scores,
        "suggestions":      suggestions,
        # Nice-to-have
        "nice_skills":      list(nice_skills.keys()),
        "nice_matched":     nice_matched,
        "nice_missing":     nice_missing,
        # Education
        "edu_required":     edu_required,
        "edu_candidate":    edu_candidate,
        "edu_result":       edu_result,
        # Experience
        "exp_requirements": exp_requirements,
        "resume_exp_years": resume_exp_years,
        # Soft skills
        "jd_soft_skills":   jd_soft_skills,
        "matched_soft":     matched_soft,
        "missing_soft":     missing_soft,
    }