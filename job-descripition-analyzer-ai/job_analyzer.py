from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from transformers import pipeline

#  Load Hugging Face text generator
generator = pipeline("text-generation", model="gpt2")

def extract_keywords(text, top_n=15):

    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])

    features = np.array(vectorizer.get_feature_names_out())
    sorted_idx = np.argsort(X.toarray()).flatten()[::-1]

    return list(set(features[sorted_idx][:top_n]))


def generate_resume_improvements(job_text, resume_text):

    job_keywords = extract_keywords(job_text)

    resume_text = resume_text.lower()

    missing = [w for w in job_keywords if w not in resume_text]

    bullet_points = []

    for skill in missing:

        prompt = f"Write a professional resume bullet point for experience in {skill}:"

        result = generator(prompt, max_length=60, num_return_sequences=1,pad_token_id=50256)

        bullet_points.append(result[0]["generated_text"])

    return job_keywords, missing, bullet_points