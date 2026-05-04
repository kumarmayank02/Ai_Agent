from pypdf import PdfReader
import re

print("🔥 CORRECT resume_agent RUNNING")

# ✅ CORRECT SKILLS DB (tumhare resume ke hisaab se)
SKILLS_DB = [
    "Java","Python","JavaScript","React","Spring Boot",
    "HTML","CSS","SQL","MySQL","PostgreSQL",
    "Git","GitHub","Hibernate","JDBC"
]

def extract_resume_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"

    return text


def extract_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):
            found.append(skill)

    return list(set(found))


def resume_intake(pdf_path):
    print("🔥 resume_intake called")

    text = extract_resume_text(pdf_path)
    skills = extract_skills(text)

    print("🔥 Extracted Skills:", skills)

    return {
        "skills": skills,
        "resume_text": text
    }