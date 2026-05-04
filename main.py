from fastapi import FastAPI
from pydantic import BaseModel
from agents.ats_agent import calculate_ats_score

app = FastAPI()

# 🔥 Request Body Model
class ATSRequest(BaseModel):
    resume_text: str
    job_desc: str

@app.get("/")
def home():
    return {"message": "AI Career Copilot API Running 🚀"}

@app.post("/ats")
def ats(data: ATSRequest):
    return calculate_ats_score(data.resume_text, data.job_desc)