from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------- ENV ----------------
load_dotenv()

# Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_gemini = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------- EMBEDDING MODEL ----------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- SKILL DATABASE ----------------
SKILL_CATEGORIES = {

    "Data Science": [
        "Python", "Machine Learning", "Deep Learning",
        "SQL", "Statistics", "Pandas", "NumPy"
    ],

    "Web Development": [
        "HTML", "CSS", "JavaScript", "React", "Node.js", "Angular"
    ],

    "Backend": [
        "Java", "Spring Boot", "FastAPI",
        "SQL", "PostgreSQL", "MySQL"
    ],

    "Cloud / DevOps": [
        "AWS", "Docker", "Kubernetes"
    ]
}


# ---------------- JOB CATEGORY ----------------
def detect_category(job_desc):

    jd = job_desc.lower()

    if any(word in jd for word in ["data", "ml", "machine learning", "ai"]):
        return "Data Science"

    elif any(word in jd for word in ["frontend", "react", "javascript", "web"]):
        return "Web Development"

    elif any(word in jd for word in ["backend", "api", "spring", "fastapi"]):
        return "Backend"

    elif any(word in jd for word in ["cloud", "aws", "docker"]):
        return "Cloud / DevOps"

    return "General"


# ---------------- SKILL EXTRACTOR ----------------
def extract_skills(text, skills_list):

    found = []

    for skill in skills_list:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return list(set(found))


# ---------------- SEMANTIC MATCH ----------------
def semantic_score(resume_text, job_desc):

    emb1 = model.encode([resume_text])
    emb2 = model.encode([job_desc])

    sim = cosine_similarity(emb1, emb2)[0][0]

    return round(float(sim) * 100, 2)


# ---------------- SKILL SCORE ----------------
def skill_score(resume_text, job_desc, category):

    relevant_skills = SKILL_CATEGORIES.get(category, [])

    if not relevant_skills:
        return 0, [], []

    resume_skills = extract_skills(resume_text, relevant_skills)
    jd_skills = extract_skills(job_desc, relevant_skills)

    if not jd_skills:
        return 0, [], []

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2), matched, missing


# ---------------- KEYWORD SCORE ----------------
def keyword_density_score(resume_text, job_desc):

    jd_words = re.findall(r"\b\w+\b", job_desc.lower())

    if not jd_words:
        return 0

    resume_lower = resume_text.lower()

    hits = sum(1 for word in jd_words if word in resume_lower)

    score = (hits / len(jd_words)) * 100

    return round(min(score, 100), 2)


# ---------------- EXPERIENCE SCORE ----------------
def experience_score(resume_text, job_desc):

    resume_exp = re.findall(r"(\d+)\s*(year|yr)", resume_text.lower())
    jd_exp = re.findall(r"(\d+)\s*(year|yr)", job_desc.lower())

    if not jd_exp:
        return 50

    if not resume_exp:
        return 20

    resume_years = int(resume_exp[0][0])
    jd_years = int(jd_exp[0][0])

    if resume_years >= jd_years:
        return 100
    elif resume_years >= jd_years / 2:
        return 60
    else:
        return 30


# ---------------- SCORE INTERPRET ----------------
def interpret(score):

    if score >= 80:
        return "🔥 Excellent Match"

    elif score >= 65:
        return "✅ Strong Match"

    elif score >= 50:
        return "👍 Good Match"

    elif score >= 35:
        return "⚠ Needs Improvement"

    else:
        return "❌ Weak Match"


# ---------------- GEMINI AI ANALYSIS ----------------
def ai_ats_explanation(resume_text, job_desc, score, missing):

    prompt = f"""
You are an ATS resume analyzer.

ATS Score: {score}
Missing Skills: {missing}

Resume:
{resume_text}

Job Description:
{job_desc}

Explain:
1. Why the ATS score is this
2. Which skills are missing
3. How to improve the resume

Keep the answer under 120 words.
"""

    try:

        response = model_gemini.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI explanation unavailable: {str(e)}"


# ---------------- FINAL ATS ENGINE ----------------
def calculate_ats_score(resume_text, job_desc):

    category = detect_category(job_desc)

    sem = semantic_score(resume_text, job_desc)

    skill, matched, missing = skill_score(resume_text, job_desc, category)

    keyword = keyword_density_score(resume_text, job_desc)

    exp = experience_score(resume_text, job_desc)

    final_score = (
        0.40 * sem +
        0.30 * skill +
        0.15 * keyword +
        0.15 * exp
    )

    final_score = round(final_score, 2)

    ai_text = ai_ats_explanation(resume_text, job_desc, final_score, missing)

    return {

        "category": category,
        "semantic_score": sem,
        "skill_score": skill,
        "keyword_score": keyword,
        "experience_score": exp,
        "ats_score": final_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "interpretation": interpret(final_score),
        "ai_explanation": ai_text

    }