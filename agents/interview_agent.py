import requests

def ask_ollama(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def generate_questions(role, resume_text):

    prompt = f"""
Generate 5 interview questions for {role}
Based on this resume:
{resume_text}
"""

    return ask_ollama(prompt)


def evaluate_answer(question, answer):

    prompt = f"""
Question: {question}
Answer: {answer}

Give score out of 10 and feedback
"""

    return ask_ollama(prompt)