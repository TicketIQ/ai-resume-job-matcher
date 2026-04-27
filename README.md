# ai-resume-job-matcher

An AI-powered web application that analyzes resumes against job descriptions to determine job fit score, identify skill gaps, and provide actionable insights using NLP and transformer-based embeddings.

📌 Problem Statement

Recruiters spend significant time manually screening resumes, while candidates struggle to understand how well their resume matches a job description.

This project solves that problem by:

Automatically analyzing resumes
Comparing them with job requirements
Providing a match score and missing skills



🎯 Features
📄 Upload Resume (PDF)
📝 Paste Job Description
🧠 Skill Extraction (NLP-based)
🎯 Semantic Match Score (Sentence Transformers)
⚠️ Missing Skills Detection
⚡ Fast & Interactive UI using Streamlit



🧠 Tech Stack
Frontend/UI: Streamlit
Backend: Python
NLP Models: Hugging Face Transformers
Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
Text Processing: spaCy
PDF Parsing: pdfplumber


🏗️ Architecture
            +----------------------+
            |   User Input         |
            | (Resume + Job Desc)  |
            +----------+-----------+
                       |
                       v
        +-----------------------------+
        |   Text Extraction (PDF)     |
        +-----------------------------+
                       |
                       v
        +-----------------------------+
        |   Skill Extraction (NLP)    |
        +-----------------------------+
                       |
                       v
        +-----------------------------+
        |  Embedding Generation       |
        | (Sentence Transformers)     |
        +-----------------------------+
                       |
                       v
        +-----------------------------+
        |   Cosine Similarity Score   |
        +-----------------------------+
                       |
                       v
        +-----------------------------+
        |   Output Results            |
        | Match Score + Skill Gaps    |
        +-----------------------------+
