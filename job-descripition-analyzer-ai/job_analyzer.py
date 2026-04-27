from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

def extract_keywords(job_text, top_n=15):

    job_text = re.sub(r'[^a-zA-Z\s]', '', job_text.lower())

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([job_text])

    feature_array = np.array(vectorizer.get_feature_names_out())
    tfidf_sorting = np.argsort(X.toarray()).flatten()[::-1]

    keywords = feature_array[tfidf_sorting][:top_n]

    return list(set(keywords))


#  THIS is the function you must import
def analyze_job_description(job_text):

    keywords = extract_keywords(job_text)

    skill_keywords = ["python","java","sql","aws","docker","kubernetes","ml","ai","nlp"]

    skills = [k for k in keywords if k in skill_keywords]
    others = [k for k in keywords if k not in skill_keywords]

    suggestions = [f"Add experience/projects involving {k}" for k in keywords]

    return skills, others, suggestions