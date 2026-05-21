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

def get_base64(file):

    with open(file, "rb") as f:
        data = f.read()

    return base64.b64encode(data).decode()


def set_background():

    bg_image = get_base64("assets/bg.jpg")

    page_bg = f"""
    <style>

    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
    background: linear-gradient(
        to bottom,
        rgba(0,20,40,0.95),
        rgba(0,80,120,0.85)
    );
}}
}}

.block-container {{
    background: rgba(0,0,0,0.15);
    padding: 2rem;s
    border-radius: 20px;
    backdrop-filter: blur(3px);
    text-shadow: 2px 2px 8px black;
}}

    h1, h2, h3, h4, h5, h6 {{
    color: white !important;
    font-weight: bold !important;
}}

    p, label, span {{
    color: white !important;
}}

div[data-baseweb="select"] * {{
    color: black !important;
}}

input {{
    color: black !important;
}}

.stTextInput input {{
    color: black !important;
}}

.stTextInput input::placeholder {{
    color: gray !important;
    opacity: 1 !important;
}}
.stSelectbox div[data-baseweb="select"] > div {{
    background-color: white !important;
    color: black !important;
}}

.stSelectbox div[data-baseweb="select"] span {{
    color: black !important;
}}

.stSelectbox svg {{
    color: black !important;
}}
code {{
    color: black !important;
}}

pre {{.stCode {{
    color: black !important;
    background-color: rgba(255,255,255,0.95) !important;
}}

.stCode * {{
    color: black !important;
}}

code {{
    color: black !important;
}}

pre {{
    color: black !important;
    background-color: rgba(255,255,255,0.95) !important;
}}

pre * {{
    color: black !important;
}}

code {{
    color: black !important;
}}

.stCode {{
    color: black !important;
    background-color: rgba(255,255,255,0.95) !important;
}}

.stCode * {{
    color: black !important;
}}

    color: black !important;
    background-color: rgba(255,255,255,0.9) !important;
    border-radius: 10px;
}}


    .stButton>button {{
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        border-radius: 10px;
        height: 45px;
        border: none;
        font-size: 16px;
    }}
    .stButton>button {{
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    height: 45px;
    border: none;
    font-size: 16px;
}}

.stDownloadButton>button {{
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white !important;
    border-radius: 10px;
    height: 45px;
    border: none;
    font-size: 16px;
    font-weight: bold;
}}

[data-testid="stFileUploader"] button {{
    background: linear-gradient(to right, #00c6ff, #0072ff) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: bold !important;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,0.08) !important;
    border: 2px dashed #00c6ff !important;
    border-radius: 15px !important;
}}

[data-testid="stFileUploaderDropzone"] * {{
    color: white !important;
}}

section[data-testid="stFileUploader"] {{
    color: white !important;
}}

header {{
    visibility: hidden;
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

role = st.sidebar.selectbox(
    "Login As",
    ["Candidate", "HR"]
)

username = st.sidebar.text_input("Username")

password = st.sidebar.text_input(
    "Password",
    type="password"
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
st.write("Upload your resume and find best job role using Machine Learning")

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

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file is not None:

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
        # NAME EXTRACT

        lines = resume_text.split('\n')

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
            


        for line in lines:

            line = line.strip()

            if line == "":
                continue

            lower_line = line.lower()
            # Skip address lines
            if "," in line:
                continue
            # Skip location words

            location_words = [
                "chennai",
                "india",
                "tamil nadu"
            ]

            if any(word in lower_line for word in location_words):
                continue

            if lower_line in invalid_words:
                continue

            if "@" in line:
                continue

            if any(char.isdigit() for char in line):
                continue

            if len(line.split()) <= 4:

                name = line
                break

        # FALLBACK TO FILE NAME 🔥
        if name == "Unknown":

            name = os.path.splitext(uploaded_file.name)[0]


        # PREDICTION
        vector = tfidf.transform([cleaned_resume])

        prediction = model.predict(vector)[0]
        probs = model.predict_proba(vector)[0]

        st.subheader("Predicted Job Role")
        st.success(prediction)

        # ------------------------
        # TOP JOBS
        # ------------------------

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

        st.subheader("Resume ATS Score")
        st.write(f"{score} / 100")

        # CURRENT DATE

        current_date = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        # CHECK DUPLICATE EMAIL

        cursor.execute(
            "SELECT * FROM candidates WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        # INSERT ONLY IF NEW

        if existing_user is None:

            cursor.execute("""
            INSERT INTO candidates
            (name, email, phone, predicted_role,
            ats_score, skills, resume_file, upload_date)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                prediction,
                score,
                ", ".join(detected_skills),
                uploaded_file.name,
                current_date
            ))
            
            conn.commit()
            # ------------------------
            # EMAIL NOTIFICATION
            # ------------------------

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
        else:
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
        # ATS RESUME
        # ------------------------

        st.subheader("ATS Optimized Resume")

        ats_resume = generate_ats_resume(resume_text, prediction)

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

        st.info(f"Showing jobs related to: {prediction}")

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
# STORED DATA (HR ONLY)
# ------------------------


if st.session_state.role == "HR":
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
        st.subheader("Stored Candidate Data")
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
        search = st.text_input(
            "Search Candidate",
            key="hr_search"
        )

        if search:

            filtered = all_data[
                all_data["name"].str.contains(search, case=False)
            ]

            st.dataframe(filtered)
            # DELETE CANDIDATE

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

            st.success("Candidate Deleted Successfully ✅")

            st.rerun()
