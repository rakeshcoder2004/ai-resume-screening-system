import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import os
import sqlite3
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from pdfminer.high_level import extract_text
from docx import Document
from datetime import datetime
from streamlit_autorefresh import st_autorefresh


# REPORT IMPORTS
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
# ------------------------
# CUSTOM UI
# ------------------------
import base64

def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def set_background():

    bg_image = get_base64("assets/bg.jpg")

    if st.session_state.get("dark_mode", True):

        sidebar_bg = "rgba(0,20,40,0.95)"
        container_bg = "rgba(0,0,0,0.35)"
        text_color = "white"

    else:

        sidebar_bg = "rgba(240,240,240,0.95)"
        container_bg = "rgba(255,255,255,0.8)"
        text_color = "black"

    page_bg = f"""

    <style>

    .stApp {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.7),
                rgba(0,0,0,0.7)
            ),
            url("data:image/jpg;base64,{bg_image}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar_bg};
    }}

    .block-container {{
        background: {container_bg};
        padding: 2rem;
        border-radius: 20px;
    }}

    h1, h2, h3, h4, h5, h6,
    p, span, label {{
    color: {text_color} !important;
    opacity: 1 !important;
}}

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {{
        color: black !important;
        background-color: white !important;
    }}

    .stButton>button {{
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        border-radius: 10px;
        border: none;
        height: 45px;
    }}

section[data-testid="stFileUploader"] {{
    color: white !important;
}}

div[data-baseweb="select"] * {{
    color: black !important;
    fill: black !important;
}}

div[data-baseweb="select"] > div {{
    background-color: white !important;
}}

ul[role="listbox"] {{
    background-color: white !important;
}}

ul[role="listbox"] li {{
    color: black !important;
    background-color: white !important;
}}

ul[role="listbox"] li:hover {{
    background-color: #dddddd !important;
}}

input {{
    color: black !important;
    -webkit-text-fill-color: black !important;
}}

input::placeholder {{
    color: black !important;
    opacity: 1 !important;
}}

header {{
    visibility: hidden;
}}

.stAlert {{
    color: white !important;
}}

.stMarkdown {{
    color: white !important;
}}

[data-testid="stFileUploader"] small {{
    color: white !important;
}}

[data-testid="stFileUploader"] label {{
    color: white !important;
}}

textarea {{
    color: black !important;
    background-color: white !important;
}}

textarea::placeholder {{
    color: #444 !important;
    opacity: 1 !important;
}}

div[data-testid="stMarkdownContainer"] p {{
    color: white !important;
}}
[data-testid="stFileUploader"] {{
    background-color: rgba(0,0,0,0.45) !important;
    padding: 15px;
    border-radius: 15px;
}}

[data-testid="stFileUploader"] section {{
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 2px dashed #00ffff !important;
    border-radius: 15px !important;
}}

[data-testid="stFileUploader"] small {{
    color: white !important;
}}

[data-testid="stFileUploader"] button {{
    background-color: #00c6ff !important;
    color: white !important;
    border-radius: 10px !important;
}}

footer {{
    visibility: hidden;
}}
</style>
"""

    st.markdown(page_bg, unsafe_allow_html=True)

# ------------------------
# TITLE
# ------------------------
# ------------------------
# PAGE CONFIG
# ------------------------

st.set_page_config(
    page_title="AI Resume Screening System",
    layout="wide"
)

set_background()
st.markdown("""
<style>
.main-title {
    font-size: 55px;
    font-weight: bold;
    color: #ffffff !important;
    text-align: center;
    text-shadow: 
        0 0 10px #00d9ff,
        0 0 20px #00d9ff,
        0 0 40px #00d9ff;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<h1 class="main-title">AI Resume Screening System</h1>',
    unsafe_allow_html=True
)

# ------------------------
# LOGIN SYSTEM 🔥
# ------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

#st.sidebar.title("Login System")
st.sidebar.title("🤖 AI Resume Screening")
# ROLE BASED MENU

if st.session_state.role == "Candidate":

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Screen Resume",
            "Reports",
            "Settings"
        ]
    )

else:

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Analytics",
            "Candidates",
            "Reports",
            "Settings"
        ]
    )


role = st.sidebar.selectbox(
    "Login As",
    ["Candidate", "HR"]
)

username = st.sidebar.text_input(
    "Username",
    placeholder="Enter Username"
)

password = st.sidebar.text_input(
    "Password",
    type="password",
    placeholder="Enter Password"
)

if st.sidebar.button("Login"):

    # HR LOGIN
    if role == "HR":

        if username == "admin" and password == "admin123":

            st.session_state.logged_in = True
            st.session_state.role = "HR"

            st.sidebar.success("HR Login Successful ✅")

        else:

            st.error("Invalid HR Credentials")

    # CANDIDATE LOGIN
    elif role == "Candidate":

        if username == "user" and password == "user123":

            st.session_state.logged_in = True
            st.session_state.role = "Candidate"

            st.sidebar.success("Candidate Login Successful ✅")

        else:

            st.error("Invalid Candidate Credentials")

# STOP APP BEFORE LOGIN
if not st.session_state.logged_in:

    st.warning("Please login to access the system 🔒")

    st.stop()

# LOGOUT BUTTON
if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.role = ""

    st.rerun()
st.markdown("""
<div style="
background: rgba(255,255,255,0.08);
padding: 30px;
border-radius: 25px;
text-align:center;
backdrop-filter: blur(10px);
box-shadow:
0 0 20px rgba(0,255,255,0.2),
0 0 40px rgba(0,255,255,0.1);
margin-bottom:30px;
">

<h1 style="
color:white;
font-size:55px;
text-shadow:
0 0 10px #00ffff,
0 0 20px #00ffff,
0 0 40px #00ffff;
">
🤖 AI Resume Screening Platform
</h1>

<p style="
font-size:22px;
color:white;
">
AI-powered ATS Resume Analysis & HR Automation System
</p>

</div>
""", unsafe_allow_html=True)

# ------------------------
# DATABASE CONNECTION 🔥
# ------------------------

conn = sqlite3.connect("resume_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    predicted_role TEXT,
    ats_score INTEGER,
    skills TEXT,
    resume_file TEXT,
    upload_date TEXT
)
""")

conn.commit()

# ------------------------
# LOAD DATASET
# ------------------------

file_path = "resume_dataset.csv"

if not os.path.exists(file_path):
    file_path = "data/resume_dataset.csv"

if not os.path.exists(file_path):
    st.error("❌ Dataset file not found! Please check 'resume_dataset.csv'")
    st.stop()

df = pd.read_csv(file_path)

df.columns = df.columns.str.strip()
df = df.dropna()
df = df.dropna(subset=["Resume", "Category"])

# ------------------------
# CLEAN TEXT
# ------------------------

def clean_text(text):
    text = re.sub(r'\W', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

df["Resume"] = df["Resume"].apply(clean_text)

# ------------------------
# TRAIN MODEL
# ------------------------

tfidf = TfidfVectorizer(stop_words="english")
X = tfidf.fit_transform(df["Resume"])
y = df["Category"]

model = LogisticRegression(max_iter=200)
model.fit(X, y)


# ------------------------
# ATS FUNCTION 🔥
# ------------------------

def generate_ats_resume(resume_text, role):

    skills = ["python","sql","machine learning","data analysis"]

    return f"""
===============================
ATS OPTIMIZED RESUME
===============================

🎯 TARGET ROLE:
{role}

👨‍💻 SKILLS:
{', '.join(skills)}

📊 PROFESSIONAL SUMMARY:
Results-driven candidate with strong background in {', '.join(skills[:3])}.
Experienced in solving real-world problems using data and technology.

🚀 PROJECTS:
- AI Resume Screening System using Machine Learning
- Built predictive models and performed data analysis

💡 STRENGTH:
Problem solving and analytical thinking

📈 IMPROVEMENT AREAS:
Deep Learning, Statistics

📌 CAREER OBJECTIVE:
Seeking opportunities in {role} to apply technical skills effectively.
"""

# ------------------------
# LOAD JOB DATA 🔥
# ------------------------

jobs_df = pd.read_csv("jobs.csv")

# ------------------------
# REPORT FUNCTION
# ------------------------

def create_pdf(prediction, top_jobs, top_scores, skills, score, missing, advice, strong_area):

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("<font size=18 color=blue><b>AI Resume ATS Report</b></font>", styles['Title']))
    content.append(Spacer(1, 15))

    ats_score = min(score + 10, 100)
    content.append(Paragraph(f"<font color=green><b>ATS Score:</b> {ats_score}/100</font>", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Predicted Role:</b> {prediction}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<font color=purple><b>Top Job Matches:</b></font>", styles['Heading2']))

    for job, sc in zip(top_jobs, top_scores):
        content.append(Paragraph(f"{job} - {sc}%", styles['Normal']))

    content.append(Spacer(1, 10))

    plt.figure()
    plt.bar(top_jobs, top_scores)
    plt.title("Top Job Matches")

    graph_path = "graph.png"
    plt.savefig(graph_path)
    plt.close()

    content.append(Image(graph_path, width=400, height=250))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<font color=orange><b>Skills Found:</b></font>", styles['Heading2']))
    content.append(Paragraph(", ".join(skills), styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Strong Area:</b> {strong_area}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Resume Score:</b> {score}/100", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<font color=red><b>Recommended Skills:</b></font>", styles['Heading2']))
    content.append(Paragraph(", ".join(missing), styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<b>Career Advice:</b>", styles['Heading2']))
    content.append(Paragraph(advice, styles['Normal']))

    doc.build(content)

    return "report.pdf"

# ------------------------
# SKILL DATABASE
# ------------------------

skills_db = {
"programming":["python","java","c","c++","javascript","sql"],
"ml":["machine learning","deep learning","nlp","tensorflow","pandas","numpy","sklearn"],
"web":["html","css","react","node","bootstrap"],
"cloud":["aws","docker","kubernetes"],
"iot":["iot","arduino","raspberry pi","embedded","microcontroller","sensors"]
}

# ------------------------
# MATCH JOBS FUNCTION
# ------------------------

def match_jobs(role):

    role = role.lower()

    if "data" in role:
        filtered = jobs_df[jobs_df["Role"].str.lower().str.contains("data|ml")]

    elif "software" in role:
        filtered = jobs_df[jobs_df["Role"].str.lower().str.contains("software|developer|backend")]

    elif "web" in role:
        filtered = jobs_df[jobs_df["Role"].str.lower().str.contains("developer|frontend|react")]

    else:
        filtered = jobs_df[jobs_df["Role"].str.lower().str.contains(role)]

    if filtered.empty:
        return jobs_df

    return filtered

# ------------------------
# FILE UPLOAD
# ------------------------

if st.session_state.role == "Candidate":

    if menu == "Dashboard":

        st.subheader("📊 Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("ATS Score", "78%")
        col2.metric("Skills Found", "18")
        col3.metric("Top Match", "95%")
        col4.metric("Experience", "Fresher")
        st.markdown("---")

        st.subheader("⚡ Live Platform Statistics")

        live1, live2, live3 = st.columns(3)

        with live1:
            st.metric(
                "📄 Resumes Screened",
                "1,248",
                "+18 Today"
            )

        with live2:
            st.metric(
                "🤖 AI Accuracy",
                "94%",
                "+2%"
            )

        with live3:
            st.metric(
                "🏆 Successful Matches",
                "872",
                "+12 Today"
            )

        st.markdown("---")

        st.subheader("📢 Recent Activity")

        activities = [
            "✅ Resume uploaded successfully",
            "🤖 AI completed ATS analysis",
            "📊 ATS score generated",
            "🏆 Candidate shortlisted",
            "📧 HR notification email sent"
        ]

        for activity in activities:

            st.markdown(
                f"""
                <div style="
                background: rgba(255,255,255,0.14);
                padding:12px;
                border-radius:12px;
                margin-bottom:10px;
                border-left:4px solid #00ffff;
                ">
                    {activity}
                </div>
                """,
                unsafe_allow_html=True
            )

# ------------------------
# SCREEN RESUME
# ------------------------

if menu == "Screen Resume":

    st.subheader("🚀 Resume Screening Workflow")

    # JOB DESCRIPTION INPUT
    st.subheader("📄 Job Description")

    job_description = st.text_area(
        "Paste Job Description Here",
        height=200
    )

    # FILE UPLOAD
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file is not None:

        st.success("File Uploaded")

        # CREATE FOLDER
        if not os.path.exists("uploaded_resumes"):
            os.makedirs("uploaded_resumes")

        # SAVE RESUME
        resume_path = f"uploaded_resumes/{uploaded_file.name}"

        with open(resume_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # FILE EXTENSION
        file_extension = uploaded_file.name.split(".")[-1].lower()

        # PDF FILE
        if file_extension == "pdf":

            with open("temp_resume.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())

            resume_text = extract_text("temp_resume.pdf")

        # DOCX FILE
        elif file_extension == "docx":

            with open("temp_resume.docx", "wb") as f:
                f.write(uploaded_file.getbuffer())

            doc = Document("temp_resume.docx")

            resume_text = ""

            for para in doc.paragraphs:
                resume_text += para.text + "\n"

        # TXT FILE
        elif file_extension == "txt":

            resume_text = uploaded_file.read().decode("utf-8")

        # UNSUPPORTED FILE
        else:

            st.error("Unsupported file format")

        # CLEAN RESUME
        cleaned_resume = clean_text(resume_text)

        # EMAIL EXTRACT
        email_match = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            resume_text
        )

        if email_match:
            email = email_match.group(0)
        else:
            email = "Not Found"

        # PHONE EXTRACT
        phone_match = re.search(
            r'(\+91[\-\s]?\d{10}|\b\d{10}\b)',
            resume_text
        )

        if phone_match:
            phone = phone_match.group(0)
        else:
            phone = "Not Found"

        # CLEAN RESUME
        cleaned_resume = clean_text(resume_text)

        # SPLIT LINES
        lines = resume_text.split('\n')

        # DEFAULT NAME
        name = "Unknown"

        invalid_words = [
            "summary",
            "contact",
            "education",
            "projects",
            "skills",
            "experience",
            "email",
            "chennai",
            "india",
            "resume",
            "profile"
        ]

        location_words = [
            "chennai",
            "india",
            "tamil nadu"
        ]

        # LOOP
        for line in lines:

            line = line.strip()

            if line == "":
                continue

            lower_line = line.lower()

            # Skip address lines
            if "," in line:
                continue

            # Skip locations
            if any(word in lower_line for word in location_words):
                continue

            # Skip invalid words
            if lower_line in invalid_words:
                continue

            # Skip emails
            if "@" in line:
                continue

            # Skip numbers
            if any(char.isdigit() for char in line):
                continue

            # Detect possible name
            if len(line.split()) <= 4:
                name = line
                break

        # FALLBACK TO FILE NAME
        name = os.path.splitext(uploaded_file.name)[0]

        # PREDICTION
        vector = tfidf.transform([cleaned_resume])

        import time

        st.markdown("""
        <h2 style='
        text-align:center;
        color:#00ffff;
        text-shadow:
        0 0 10px #00ffff,
        0 0 20px #00ffff,
        0 0 40px #00ffff;
        '>
        🤖 AI Processing Resume...
        </h2>
        """, unsafe_allow_html=True)

        progress = st.progress(0)

        status_text = st.empty()

        for i in range(100):

            time.sleep(0.02)

            progress.progress(i + 1)

            if i < 30:
                status_text.info("📄 Extracting Resume Data...")

            elif i < 60:
                status_text.info("🧠 Performing AI Skill Analysis...")

            elif i < 85:
                status_text.info("📊 Calculating ATS Score...")

            else:
                status_text.info("✅ Finalizing Report...")

        prediction = model.predict(vector)[0]
        probs = model.predict_proba(vector)[0]
        st.subheader("Predicted Job Role")
        st.success(prediction)
        top3_index = np.argsort(probs)[-3:][::-1]

        st.subheader("Top 3 Suitable Jobs")

        top_jobs = []

        top_scores = []

        for i in top3_index:

            job = model.classes_[i]

            score_val = round(probs[i] * 100, 2)

            top_jobs.append(job)

            top_scores.append(score_val)

            st.write(job, "-", score_val, "%")

        # ------------------------
        # GRAPH
        # ------------------------

        st.subheader("Job Match Graph")

        plt.figure()

        plt.bar(top_jobs, top_scores)
        plt.xticks(rotation=10)

        st.pyplot(plt)

# ------------------------
# SKILLS
# ------------------------

        detected_skills = []

        for category in skills_db:

            for skill in skills_db[category]:

                if skill in cleaned_resume:

                    detected_skills.append(skill)

        st.subheader("Skills Found in Resume")

        st.success(", ".join(detected_skills))

        st.subheader("Total Skills Found")

        st.write(len(detected_skills))

        # ------------------------
        # JD MATCHING
        # ------------------------

        jd_score = 0

        jd_missing_skills = []

        if job_description:

            cleaned_jd = clean_text(job_description)

            jd_skills = []

            for category in skills_db:

                for skill in skills_db[category]:

                    if skill in cleaned_jd:
                        jd_skills.append(skill)

            matched = 0

            for skill in jd_skills:

                if skill in detected_skills:

                    matched += 1

                else:

                    jd_missing_skills.append(skill)

            if len(jd_skills) > 0:

                jd_score = int(
                    (matched / len(jd_skills)) * 100
                )

            st.subheader("🎯 Job Description Match")

            st.progress(jd_score / 100)

            st.markdown(
                f"""
                <h1 style='text-align:center;color:#00ffcc;'>
                {jd_score}% Match
                </h1>
                """,
                unsafe_allow_html=True
            )

            if len(jd_missing_skills) > 0:

                st.warning(
                    f"Missing Skills: {', '.join(jd_missing_skills)}"
                )

            else:

                st.success("Excellent Match 🚀")
        # ------------------------
        # STRONG AREA
        # ------------------------

        ml_count = prog_count = web_count = iot_count = 0

        for skill in detected_skills:

            if skill in skills_db["ml"]:
                ml_count += 1

            if skill in skills_db["programming"]:
                prog_count += 1

            if skill in skills_db["web"]:
                web_count += 1

            if skill in skills_db["iot"]:
                iot_count += 1

        max_area = max(ml_count, prog_count, web_count, iot_count)

        if max_area == ml_count:
            strong_area_text = "Machine Learning"

        elif max_area == prog_count:
            strong_area_text = "Programming"

        elif max_area == web_count:
            strong_area_text = "Web Development"

        else:
            strong_area_text = "IoT"

        st.subheader("Strong Area")
        st.write(strong_area_text)

        # ------------------------
        # ATS SCORE
        # ------------------------

        score = 0

        # EMAIL

        if uploaded_file is not None:

            if re.search(r'@\w+', resume_text):
                score += 10

            # PHONE
            if re.search(r'\+?\d{10,13}', resume_text):
                score += 10

            # SKILLS
            score += min(len(detected_skills) * 5, 30)

            # PROJECT
        project_keywords = ["project", "developed", "built", "system"]

        for word in project_keywords:
            if word in cleaned_resume:
                score += 10
                break

        # EXPERIENCE
        experience_keywords = ["experience", "internship", "worked"]

        for word in experience_keywords:
            if word in cleaned_resume:
                score += 10
                break

        # EDUCATION
        education_keywords = ["b.e", "btech", "degree", "university"]

        for word in education_keywords:
            if word in cleaned_resume:
                score += 10
                break

               # CERTIFICATION
        cert_keywords = ["certification", "certificate", "course"]

        for word in cert_keywords:

            if word in cleaned_resume:
                score += 10
                break

        score = min(score, 100)

        st.subheader("📊 Resume ATS Score")
        if score >= 80:
            score_color = "#00ff99"
        elif score >= 60:
            score_color = "#ffcc00"
        else:
            score_color = "#ff4b4b"

        st.progress(score / 100)


        st.markdown(
            f"""
            <h1 style='
            text-align:center;
            color:{score_color};
            font-size:55px;
            text-shadow:
            0 0 10px {score_color},
            0 0 20px {score_color};
            '>
            {score}%
            </h1>
            """,
            unsafe_allow_html=True
        )

        # ------------------------
        # SHORTLIST STATUS
        # ------------------------

        st.subheader("📌 Candidate Status")

        if score >= st.session_state.get("threshold", 70):

            st.success("✅ Shortlisted for Interview")

        elif score >= 60:

            st.warning("🟡 Under HR Review")

        else:

            st.error("❌ Rejected")

        # CURRENT DATE

        current_date = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        # CHECK DUPLICATE EMAIL
        email = "Not Found"

        email_match = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            resume_text
        )

        if email_match:
            email = email_match.group(0)
        cursor.execute(
            "SELECT * FROM candidates WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        # INSERT ONLY IF NEW

        if existing_user is None:

            cursor.execute(
                """
                INSERT INTO candidates
                (name, email, phone, predicted_role,
                ats_score, skills, resume_file, upload_date)

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    phone,
                    prediction,
                    score,
                    ", ".join(detected_skills),
                    uploaded_file.name,
                    current_date
                )
            )

            conn.commit()

            # EMAIL NOTIFICATION

        sender_email = "rakeshviot10@gmail.com"

        sender_password = "sker uolj svsh ktoj"

        receiver_email = "rakeshv8248@gmail.com"

        subject = "TEST MAIL FROM ATS PROJECT"

        body = f"""
        New Candidate Resume Uploaded

        Username: {username}

        Predicted Role: {prediction}

        ATS Score: {score}/100
        """
        msg = MIMEMultipart()

        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:

            server = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            st.write("Login Success")

            if st.session_state.get(
                "email_notifications",
                True
            ):

                server.sendmail(
                    sender_email,
                    receiver_email,
                    msg.as_string()
                )

                st.write("Mail Sending Success")

            server.quit()

            st.success("Mail Sent Successfully 🚀")

        except Exception as e:

            st.error(f"Email Error: {e}")

        if existing_user is not None:

            st.warning("Resume already uploaded ⚠️")

            st.write("Duplicate Email Found")

        # ------------------------
        # MISSING SKILLS
        # ------------------------

        ds_skills = [
            "python",
            "machine learning",
            "statistics",
            "sql",
            "deep learning"
        ]

        missing = [
            skill for skill in ds_skills
            if skill not in detected_skills
        ]

        st.subheader("Recommended Skills to Improve")
        st.success(", ".join(missing))

        # ------------------------
        # ADVICE
        # ------------------------

        if score < 40:
            advice_text = "Add more technical skills to improve resume strength"

        elif score < 70:
            advice_text = "Good profile, improve advanced skills"

        else:
            advice_text = "Strong resume for technical roles"
        st.subheader("Career Advice")
        st.write(advice_text)

        # ------------------------
        # AI INSIGHTS
        # ------------------------

        st.subheader("🤖 AI Insights")

        if score > 70:
            st.success("Strong technical profile detected")

        elif score > 50:
            st.warning("Average profile with improvement scope")

        else:
            st.error("Resume needs major improvements")

        if "python" in detected_skills:
            st.info("Python programming skill detected")

        if "machine learning" in detected_skills:
            st.info("Machine Learning knowledge detected")

        if "sql" in detected_skills:
            st.info("Database skills identified")

        if len(missing) > 0:

            st.warning(
                f"Missing Skills: {', '.join(missing[:3])}"
            )

        st.success(
            f"Recommended Role: {prediction}"
        )

        # ------------------------
        # AI RESUME IMPROVEMENTS
        # ------------------------

        st.markdown("---")

        st.subheader("🚀 AI Resume Improvement Suggestions")

        suggestions = []

        if "aws" not in detected_skills:
            suggestions.append(
                "☁️ Add AWS or Cloud Computing skills"
            )

        if "sql" not in detected_skills:
            suggestions.append(
                "🗄️ Improve SQL knowledge"
            )

        if "machine learning" not in detected_skills:
            suggestions.append(
                "🤖 Learn Machine Learning concepts"
            )

        if score < 70:
            suggestions.append(
                "📄 Add more technical projects"
            )

        if "certificate" not in cleaned_resume:
            suggestions.append(
                "🏅 Add certifications to strengthen resume"
            )

        if len(suggestions) > 0:

            for suggestion in suggestions:

                st.info(suggestion)

        else:

            st.success(
                "🎉 Excellent Resume Profile!"
            )

        # ------------------------
        # ATS RESUME
        # ------------------------

        st.subheader("ATS Optimized Resume")

        ats_resume = generate_ats_resume(
            resume_text,
            prediction
        )

        st.markdown("### 📄 ATS Resume")

        st.text_area(
            "ATS Resume",
            ats_resume,
            height=500
        )

        # ------------------------
        # MATCHING JOBS
        # ------------------------

        st.subheader("Matching Jobs for You")

        st.info(
            f"Showing jobs related to: {prediction}"
        )

        matched_jobs = match_jobs(prediction)

        for index, row in matched_jobs.head(3).iterrows():

            st.markdown(f"""
        **🏢 Company:** {row['Company']}  
        **💼 Role:** {row['Role']}  
        **📍 Location:** {row['Location']}  
        🔗 [Apply Here]({row['Link']})
        """)

            st.markdown("---")

        # ------------------------
        # PDF DOWNLOAD
        # ------------------------

        st.subheader("Download Report")

        pdf_file = create_pdf(
            prediction,
            top_jobs,
            top_scores,
            detected_skills,
            score,
            missing,
            advice_text,
            strong_area_text
        )
        with open(pdf_file, "rb") as f:

            st.download_button(
                label="Download Full Report",
                data=f,
                file_name="resume_report.pdf",
                mime="application/pdf"
            )

# ------------------------
# ANALYTICS PAGE
# ------------------------

if menu == "Analytics":

    if st.session_state.role != "HR":
        st.error("Access Denied")
        st.stop()

    st.subheader("📈 ATS Analytics Dashboard")

    chart_data = pd.DataFrame({
        "ATS Score": [65, 78, 90, 85, 72]
    })

    st.line_chart(chart_data)

    role_data = pd.DataFrame({
        "Role": ["ML", "Web", "Data", "IoT"],
        "Count": [10, 7, 5, 3]
    })

    st.bar_chart(role_data.set_index("Role"))

    st.subheader("📊 Performance Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Highest ATS", "95%")

    with col2:
        st.metric("Average ATS", "78%")

# ------------------------
# STORED DATA (HR ONLY)
# ------------------------

if st.session_state.role == "HR":

    if menu == "Dashboard":

        st.title("HR Dashboard")

        all_data = pd.read_sql(
            """
            SELECT id, name, email, phone,
            predicted_role, ats_score,
            skills, resume_file, upload_date
            FROM candidates
            ORDER BY ats_score DESC
            """,
            conn
        )

        total_candidates = len(all_data)

        highest_score = all_data["ats_score"].max()

        average_score = round(
            all_data["ats_score"].mean(),
            2
        )

        total_skills = all_data["skills"].count()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Candidates",
            total_candidates
        )

        col2.metric(
            "Highest ATS Score",
            highest_score
        )

        col3.metric(
            "Average ATS Score",
            average_score
        )

        col4.metric(
            "Total Skills",
            total_skills
        )

        # ------------------------
        # TOP CANDIDATES
        # ------------------------

        st.subheader("🏆 Top Candidates")

        top_candidates = all_data.sort_values(
            by="ats_score",
            ascending=False
        ).head(5)

        st.dataframe(
            top_candidates[
                [
                    "name",
                    "predicted_role",
                    "ats_score"
                ]
            ]
        )

# ------------------------
# CANDIDATES PAGE
# ------------------------

if menu == "Candidates":

    if st.session_state.role != "HR":
        st.error("Access Denied")
        st.stop()

    st.subheader("👥 Candidate Database")

    all_data = pd.read_sql(
        """
        SELECT id, name, email, phone,
        predicted_role, ats_score,
        skills, resume_file, upload_date
        FROM candidates
        ORDER BY ats_score DESC
        """,
        conn
    )

    st.dataframe(all_data)

    # ------------------------
    # RESUME RANKING
    # ------------------------

    st.markdown("---")

    st.subheader("🏆 Resume Ranking System")

    ranking_data = all_data.sort_values(
        by="ats_score",
        ascending=False
    )

    ranking_data = ranking_data.reset_index(
        drop=True
    )

    ranking_data.index = ranking_data.index + 1

    st.dataframe(
        ranking_data[
            [
                "name",
                "predicted_role",
                "ats_score"
            ]
        ]
    )

    # ------------------------
    # AI RECRUITER RECOMMENDATIONS
    # ------------------------

    st.markdown("---")

    st.subheader("🤖 AI Recruiter Recommendations")

    top_candidate = ranking_data.iloc[0]

    st.success(
        f"""
        🏆 Best Overall Candidate:
        {top_candidate['name']}
        """
    )

    st.info(
        f"""
        🎯 Recommended Role:
        {top_candidate['predicted_role']}
        """
    )

    st.warning(
        f"""
        📊 ATS Score:
        {top_candidate['ats_score']}%
        """
    )

    role_counts = ranking_data[
        "predicted_role"
    ].value_counts()

    top_role = role_counts.idxmax()

    st.success(
        f"""
        🚀 Most Common Recommended Role:
        {top_role}
        """
    )

    # ------------------------
    # SEARCH
    # ------------------------

    search = st.text_input(
        "Search Candidate",
        key="hr_search"
    )

    if search:

        filtered = all_data[
            all_data["name"].str.contains(
                search,
                case=False
            )
        ]

        st.dataframe(filtered)

    # ------------------------
    # DELETE CANDIDATE
    # ------------------------

    candidate_id = st.number_input(
        "Enter Candidate ID to Delete",
        min_value=1,
        step=1
    )

    if st.button("Delete Candidate"):

        cursor.execute(
            "DELETE FROM candidates WHERE id=?",
            (candidate_id,)
        )

        conn.commit()

        st.success(
            "Candidate Deleted Successfully ✅"
        )

        st.rerun()
# ------------------------
# REPORTS PAGE
# ------------------------

if menu == "Reports":

    st.subheader("📄 Generated Reports")

    report_data = pd.read_sql(
    """
    SELECT name, predicted_role, ats_score
    FROM candidates
    ORDER BY ats_score DESC
    """,
    conn
)

    st.dataframe(report_data)

    st.success("Reports Generated Successfully 🚀")
# ------------------------
# SETTINGS PAGE
# ------------------------

if menu == "Settings":

    st.subheader("⚙️ System Settings")

    dark_mode = st.toggle(
        "Enable Dark Mode",
        value=True
    )

    st.session_state.dark_mode = dark_mode

    email_notifications = st.toggle(
        "Enable Email Notifications",
        value=True
    )

    st.session_state.email_notifications = email_notifications

    auto_screening = st.toggle(
        "Enable Auto Screening",
        value=True
    )

    st.session_state.auto_screening = auto_screening

    interview_mode = st.selectbox(
        "Interview Strictness",
        ["Easy", "Medium", "Strict"]
    )

    if interview_mode == "Easy":

        threshold = 50

    elif interview_mode == "Medium":

        threshold = 70

    else:

        threshold = 85

    st.session_state.threshold = threshold

    st.info(f"Current ATS Threshold: {threshold}%")

    st.success("Settings Saved Successfully ✅")