import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
import tempfile
import pandas as pd
import streamlit as st
from serpapi import GoogleSearch
from dotenv import load_dotenv


from agents.interview_agent import generate_questions, evaluate_answer

from agents.job_agent import build_smart_query, rank_jobs
from agents.resume_agent import resume_intake
# ---------------- ENV ----------------
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Career Copilot",
    layout="wide",
    page_icon="🤖"
)

# ---------------- CSS ----------------
def load_css():
    try:
        with open("ui/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

# ---------------- JOB ROLE TEMPLATES ----------------
JOB_ROLES = {
    "Data Scientist": "Python, Machine Learning, SQL, Pandas, NumPy, Statistics",
    "Frontend Developer": "HTML, CSS, JavaScript, React",
    "Backend Developer": "Java, Spring Boot, SQL, APIs",
    "DevOps Engineer": "AWS, Docker, Kubernetes, CI/CD"
}

# ---------------- HELPER FUNCTION ----------------
def build_query(job_title, location, experience, job_types, platform):
    
    query = f"{job_title} jobs in {location} {platform}"
    
    if experience > 0:
        query += f" {experience}+ years experience"
    
    if job_types:
        query += " " + " ".join(job_types)
    
    return query
def normalize_posted(posted):
    if not posted:
        return "N/A"

    posted = posted.lower()

    # 🔥 Portuguese
    if "há" in posted:
        posted = posted.replace("há ", "").replace(" dias", " days ago")

    # 🔥 Spanish
    if "hace" in posted:
        posted = posted.replace("hace ", "").replace(" días", " days ago")

    # 🔥 French
    if "il y a" in posted:
        posted = posted.replace("il y a ", "").replace(" jours", " days ago")

    # 🔥 German
    if "vor" in posted and "tagen" in posted:
        posted = posted.replace("vor ", "").replace(" tagen", " days ago")

    # 🔥 Indonesian / Malay
    if "hari yang lalu" in posted:
        posted = posted.replace(" hari yang lalu", " days ago")

    # 🔥 fallback fix (numbers only)
    import re
    match = re.search(r"\d+", posted)
    if match:
        return f"{match.group()} days ago"

    return posted

# ---------------- SIDEBAR ----------------
st.sidebar.title("🤖 AI Career Copilot")
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📄 Resume Analyzer", "💼 Job Search","🎤 Interview Prep"]
)

# ================= HOME =================
if menu == "🏠 Home":
    st.title("🚀 AI Career Copilot")
    st.info("Smart Resume Analysis + Real Job Recommendations")

# ================= RESUME ANALYZER =================
elif menu == "📄 Resume Analyzer":

    st.title("📄 Resume Analyzer")

    uploaded = st.file_uploader("Upload Resume (PDF)")

    selected_role = st.selectbox(
        "Select Job Role",
        ["-- Select Role --"] + list(JOB_ROLES.keys())
    )

    job_desc = st.text_area("Job Description")

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(uploaded.read())
            result = resume_intake(f.name)
            st.session_state.resume_data = result
         
        st.success("Resume Processed ✅")
        
        tab = st.radio("", ["Summary", "Skills", "Raw Text"], horizontal=True)

        if tab == "Summary":
            st.write(result["resume_text"][:500])

        elif tab == "Skills":
            for skill in result.get("skills", []):
                st.write(f"✅ {skill}")

        elif tab == "Raw Text":
            st.write(result["resume_text"])

        if st.button("Analyze ATS"):
            if job_desc:
                with st.spinner("Analyzing..."):
                    res = requests.post(
                        "http://127.0.0.1:8000/ats",
                        params={
                            "resume_text": result["resume_text"],
                            "job_desc": job_desc
                        }
                    ).json()

                st.metric("ATS Score", f"{res.get('ats_score', 0):.2f}%")
                st.write(res.get("ai_explanation", ""))
            else:
                st.warning("Enter Job Description")
# ================= JOB SEARCH =================
elif menu == "💼 Job Search":

    st.title("💼 Real-Time Job Search")

    # -------- SESSION --------
    if "jobs_data" not in st.session_state:
        st.session_state.jobs_data = []

    if "selected_job_index" not in st.session_state:
        st.session_state.selected_job_index = 0

    search_type = st.radio(
        "Search Mode",
        ["⚙ Custom Search", "📄 Resume-Based"],
        horizontal=True
    )


    col1, col2 = st.columns(2)

    if search_type == "⚙ Custom Search":
        with col1:
            job_title = st.selectbox("Job Role", [
                "AI Engineer","Data Scientist","Backend Developer",
                "Frontend Developer","DevOps Engineer", "Product Manager", 
                "UX Designer", "Mobile Developer", "Cloud Engineer", 
                "Cybersecurity Analyst", "Business Analyst",
                "QA Engineer", "Technical Writer", "Project Manager","journeyer","tech whisperer"
                ,"code ninja", "data wizard", "cloud guru", "security sentinel",
                "product visionary", "ux maestro", "mobile maven", "devops dynamo",
            ])
        with col2:
            location = st.selectbox("Location", [
                "India","USA","Bangladesh","Remote","UK","Germany", 
                "Canada", "Australia",  "France", "Netherlands", "Singapore", 
                "Sweden", "Switzerland", "Japan", "South Korea",
                "Brazil", "Mexico", "Spain", "Italy", "Russia", "Other"
            ])
    else:
       if "resume_data" in st.session_state:

        resume = st.session_state.resume_data
        skills = " ".join(resume.get("skills", [])).lower()

        # 🔥 AUTO ROLE DETECT
        if "machine learning" in skills or "AI" in skills or "deep learning" in skills:
            job_title = "AI Engineer"
        elif "react" in skills or "angular" in skills or "vue" in skills or "html" in skills or "css" in skills:
            job_title = "Frontend Developer"
        elif "java" in skills or "spring boot" in skills or "sql" in skills or "apis" in skills:
            job_title = "Backend Developer"
        else:
            job_title = "Software Engineer"

        st.success(f"🤖 Detected Role: {job_title}")

        with col2:
            location = st.selectbox("Location", [
                "India","Jharkhand","USA","Bangladesh","Remote","UK","Germany", 
                "Canada", "Australia",  "France", "Netherlands", "Singapore", 
                "Sweden", "Switzerland", "Japan", "South Korea",
                "Brazil", "Mexico", "Spain", "Italy", "Russia", "Other"
            ])

    # -------- FILTERS --------
    job_types = st.multiselect(
        "Job Type",
        ["Full-time","Part-time","Internship","Contract", "Remote"]
    )

    experience = st.slider("Experience (Years)", 0, 10, 1)

    platforms = st.multiselect(
        "Platforms",
        ["LinkedIn","Indeed","Glassdoor","Monster","Google Jobs","GitHub Jobs", 
         "AngelList", "StackOverflow Jobs", "Dice", "ZipRecruiter"],
        default=["LinkedIn"]
    )

    jobs_per_platform = st.slider("Jobs per Platform", 1, 10, 5)

    # -------- FETCH JOBS --------
    search_clicked = st.button("🚀 Search Jobs")

# 🔥 AUTO RUN ONLY IF RESUME MODE
    if search_type == "📄 Resume-Based" and "resume_data" in st.session_state:
             search_clicked = True

    if search_clicked:
        
        st.warning("⚠️ Please upload and analyze your resume first for better job matching")
        st.info("❌ No jobs found via SerpAPI. Falling back to standard search.")
        jobs = []

        if SERPAPI_KEY:

            for platform in platforms:

                query = build_smart_query(
                    job_title, location, experience, job_types
                )

                params = {
                    "engine": "google_jobs",
                    "q": query,
                    "location": location,
                    "api_key": SERPAPI_KEY
                }

                try:
                    search = GoogleSearch(params)
                    results = search.get_dict()

                    for job in results.get("jobs_results", [])[:jobs_per_platform]:

                        apply_link = "#"
                        if "apply_options" in job:
                            apply_link = job["apply_options"][0].get("link", "#")
                        posted_raw = job.get("detected_extensions", {}).get("posted_at", "N/A")

                        jobs.append({
                          "Title": job.get("title"),
                          "Company": job.get("company_name"),
                          "Location": job.get("location"),
                          "Platform": platform,
                          "Posted": normalize_posted(posted_raw),
                          "Apply Link": apply_link,
                        "Description": job.get("description", "No description available")
                        })

                except Exception as e:
                    st.error(f"Error fetching {platform}: {str(e)}")

        else:
            st.error("❌ SERPAPI_KEY missing")
        jobs = rank_jobs(jobs, job_title)
        st.session_state.jobs_data = jobs
        st.session_state.selected_job_index = 0  # reset selection

        if jobs:
          best_job = jobs[0]
          st.success(f"⭐ Recommended: {best_job['Title']} at {best_job['Company']}")

    # -------- DISPLAY --------
    if st.session_state.jobs_data:

        df = pd.DataFrame(st.session_state.jobs_data)

        st.subheader(f"📊 Job Results ({len(df)})")

        # 🔥 Add Select column
        df_display = df.copy()
        df_display["Select"] = False

        # Preserve selection
        df_display.loc[st.session_state.selected_job_index, "Select"] = True

        edited_df = st.data_editor(
           df_display,
           width="stretch",
           key="job_table"
        )

        # 🔥 Detect selected row
        selected_rows = edited_df[edited_df["Select"] == True]

        if not selected_rows.empty:
            selected_index = selected_rows.index[0]
            st.session_state.selected_job_index = selected_index

        # -------- JOB DETAILS --------
        job = df.loc[st.session_state.selected_job_index]

        st.subheader("📄 Job Details")
        st.markdown(f"### {job['Title']}")
        
        st.write("🏢", job["Company"])
        
        col1, col2, col3= st.columns(3)

        with col1:
            st.metric("Location", job["Location"])
        with col2:
            st.metric("Platform", job["Platform"])
        with col3:
            st.metric("Posted", job["Posted"])
    
            st.link_button("🔗 Apply Now", job["Apply Link"])
        import json

        job_data = {
           "Title": job["Title"],
            "Company": job["Company"],
            "Location": job["Location"],
            "Platform": job["Platform"],
            "Posted": job["Posted"],
            "Apply Link": job["Apply Link"],
            "Description": job["Description"]
         }

        st.download_button(
             "📥 Download Job",
              data=json.dumps(job_data, indent=2),
              file_name="job_details.json",
              mime="application/json"
             )
        with st.expander("📖 View Job Description"):
             st.text_area(
        "Job Description",
        job.get("Description", ""),
        height=600,
        label_visibility="collapsed"

    )

    else:
        st.info("👉 Click  to load jobs")

 # ================= INTERVIEW PREP =================
elif menu == "🎤 Interview Prep":

    st.title("🎤 AI Interview Preparation (Local AI)")

    role = st.selectbox("Select Role", [
        "Backend Developer",
        "Frontend Developer",
        "Data Scientist",
        "DevOps Engineer"
    ])

    # Resume data
    if "resume_data" in st.session_state:
        resume = st.session_state.resume_data
        resume_text = resume.get("resume_text", "")
    else:
        resume_text = ""
        st.warning("⚠️ Please upload resume first")

    # -------- GENERATE QUESTIONS --------
    if "questions" not in st.session_state:
        st.session_state.questions = None

    if st.button("🧠 Generate Questions"):

        if st.session_state.questions is None:

            with st.spinner("Generating questions..."):
                questions = generate_questions(role, resume_text)

            st.session_state.questions = questions

        else:
            st.info("Questions already generated ✅")

    # -------- SHOW QUESTIONS --------
    if st.session_state.questions:

        st.subheader("📋 Interview Questions")
        st.write(st.session_state.questions)

        # -------- ANSWER --------
        answer = st.text_area("✍️ Your Answer")

        # -------- EVALUATE --------
        if st.button("🤖 Evaluate Answer"):

            with st.spinner("Evaluating..."):
                feedback = evaluate_answer(
                    st.session_state.questions,
                    answer
                )

            st.subheader("📊 Feedback")
            st.write(feedback)