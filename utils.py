
import pdfplumber
from sentence_transformers import SentenceTransformer, util

# Load embedding model (Hugging Face)
model = SentenceTransformer('all-MiniLM-L6-v2')

SKILLS_DB = [
    "python","java","sql","machine learning","deep learning",
    "nlp","aws","docker","kubernetes","tensorflow","pytorch",
    "data analysis","spring boot","react","angular"
]

#  Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

#  Extract skills
def extract_skills(text):
    text = text.lower()
    return list(set([skill for skill in SKILLS_DB if skill in text]))

#  Semantic match score
def calculate_match(resume_text, job_text):
    emb1 = model.encode(resume_text, convert_to_tensor=True)
    emb2 = model.encode(job_text, convert_to_tensor=True)

    score = util.pytorch_cos_sim(emb1, emb2).item()
    return round(score * 100, 2)

#  Missing skills
def missing_skills(resume_skills, job_skills):
    return list(set(job_skills) - set(resume_skills))