import streamlit as st
import pdfplumber
import sqlite3
import json
import os
from google import genai

# ==============================
# PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ==============================
# CUSTOM CSS
# ==============================

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 18px;
    margin-bottom: 30px;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    text-align: center;
    background-color: #ffffff;
}

.metric-number {
    font-size: 32px;
    font-weight: 700;
}

.metric-label {
    color: #666;
}

.section-title {
    font-size: 25px;
    font-weight: 650;
    margin-top: 25px;
    margin-bottom: 12px;
}

.skill {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 15px;
    background-color: #eee;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================

DB_NAME = "history.db"


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            match_score INTEGER,
            ats_score INTEGER,
            resume_quality_score INTEGER,
            analysis TEXT
        )
    """)

    conn.commit()
    conn.close()


init_database()

# ==============================
# GEMINI CLIENT
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found. "
        "Please set GEMINI_API_KEY in your terminal."
    )
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ==============================
# PDF TEXT EXTRACTION
# ==============================


def extract_text_from_pdf(uploaded_file):

    text = ""

    try:
        with pdfplumber.open(uploaded_file) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        st.error(f"Error reading PDF: {e}")

    return text


# ==============================
# GEMINI ANALYSIS
# ==============================


def analyze_resume(resume_text, job_title, job_description):

    prompt = f"""
You are an expert ATS resume analyzer and career advisor.

Analyze the following resume against the given job.

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Return ONLY valid JSON.

Use this exact structure:

{{
  "match_score": 0,
  "ats_friendliness": "Good",
  "resume_quality_score": 0,
  "ats_score": 0,
  "section_completeness": 0,
  "keyword_optimization": 0,
  "formatting_quality": 0,

  "matched_skills": [],
  "missing_skills": [],

  "recommended_skills_to_learn": [],

  "recommended_job_roles": [
    {{
      "role": "",
      "match_percentage": 0,
      "reason": ""
    }}
  ],

  "ats_issues": [],

  "strengths": [],

  "improvement_suggestions": [],

  "summary": ""
}}

Rules:

1. All scores must be between 0 and 100.
2. match_score represents how well the resume matches the job.
3. ats_score represents ATS compatibility.
4. resume_quality_score represents overall resume quality.
5. section_completeness evaluates important sections such as:
   Summary, Education, Skills, Projects, Experience, Certifications.
6. keyword_optimization evaluates relevant keywords from the job description.
7. formatting_quality evaluates ATS-friendly formatting.
8. matched_skills must contain skills found in both the resume and job requirements.
9. missing_skills must contain important job skills missing from the resume.
10. recommended_skills_to_learn should contain useful skills the candidate should learn.
11. recommended_job_roles should contain 4 to 6 suitable job roles based on the resume.
12. ats_issues should contain actual ATS problems.
13. strengths should contain genuine strengths from the resume.
14. improvement_suggestions should be practical.
15. summary should be a short career assessment.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        result = response.text.strip()

        # Remove accidental Markdown code fences

        if result.startswith("```"):
            result = result.replace("```json", "")
            result = result.replace("```", "")

        result = result.strip()

        return json.loads(result)

    except Exception as e:

        st.error(f"Gemini analysis failed: {e}")

        return None


# ==============================
# SAVE ANALYSIS
# ==============================


def save_analysis(job_title, result):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses
        (
            job_title,
            match_score,
            ats_score,
            resume_quality_score,
            analysis
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        job_title,
        result.get("match_score", 0),
        result.get("ats_score", 0),
        result.get("resume_quality_score", 0),
        json.dumps(result)
    ))

    conn.commit()
    conn.close()


# ==============================
# LOAD HISTORY
# ==============================


def load_history():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            job_title,
            match_score,
            ats_score,
            resume_quality_score
        FROM analyses
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==============================
# HEADER
# ==============================

st.markdown(
    '<div class="title">📄 AI Resume Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume with AI and improve your chances of getting shortlisted.'
    '</div>',
    unsafe_allow_html=True
)

# ==============================
# SIDEBAR
# ==============================

with st.sidebar:

    st.header("⚙️ Resume Analysis")

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

    job_title = st.text_input(
        "Job Title",
        placeholder="Example: Python Developer"
    )

    job_description = st.text_area(
        "Job Description",
        height=220,
        placeholder="Paste the complete job description here..."
    )

    analyze_button = st.button(
        "🚀 Analyze Resume",
        use_container_width=True
    )


# ==============================
# MAIN ANALYSIS
# ==============================

if analyze_button:

    if uploaded_file is None:

        st.warning("Please upload your resume PDF.")

    elif not job_title.strip():

        st.warning("Please enter the job title.")

    elif not job_description.strip():

        st.warning("Please enter the job description.")

    else:

        with st.spinner("Reading and analyzing your resume..."):

            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text.strip():

                st.error(
                    "Could not extract text from the PDF. "
                    "Please upload a text-based PDF."
                )

                st.stop()

            result = analyze_resume(
                resume_text,
                job_title,
                job_description
            )

        if result:

            save_analysis(job_title, result)

            st.success("Resume analysis completed successfully! 🎉")

            # ==============================
            # MAIN METRICS
            # ==============================

            st.markdown(
                '<div class="section-title">📊 Overall Resume Results</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "🎯 Job Match",
                    f"{result.get('match_score', 0)}%"
                )

            with col2:

                st.metric(
                    "🤖 ATS Score",
                    f"{result.get('ats_score', 0)}%"
                )

            with col3:

                st.metric(
                    "⭐ Resume Quality",
                    f"{result.get('resume_quality_score', 0)}%"
                )

            st.progress(
                result.get("match_score", 0) / 100
            )

            # ==============================
            # ATS FRIENDLINESS
            # ==============================

            st.markdown(
                '<div class="section-title">🤖 ATS Compatibility</div>',
                unsafe_allow_html=True
            )

            ats_friendliness = result.get(
                "ats_friendliness",
                "Unknown"
            )

            st.info(
                f"ATS Friendliness: **{ats_friendliness}**"
            )

            # ==============================
            # RESUME QUALITY
            # ==============================

            st.markdown(
                '<div class="section-title">📑 Resume Quality Analysis</div>',
                unsafe_allow_html=True
            )

            q1, q2, q3, q4 = st.columns(4)

            with q1:
                st.metric(
                    "Section Completeness",
                    f"{result.get('section_completeness', 0)}%"
                )

            with q2:
                st.metric(
                    "Keyword Optimization",
                    f"{result.get('keyword_optimization', 0)}%"
                )

            with q3:
                st.metric(
                    "Formatting Quality",
                    f"{result.get('formatting_quality', 0)}%"
                )

            with q4:
                st.metric(
                    "ATS Score",
                    f"{result.get('ats_score', 0)}%"
                )

            # ==============================
            # SKILLS
            # ==============================

            st.markdown(
                '<div class="section-title">🛠️ Skill Analysis</div>',
                unsafe_allow_html=True
            )

            matched = result.get(
                "matched_skills",
                []
            )

            missing = result.get(
                "missing_skills",
                []
            )

            s1, s2 = st.columns(2)

            with s1:

                st.subheader("✅ Matched Skills")

                if matched:

                    for skill in matched:
                        st.markdown(
                            f'<span class="skill">✓ {skill}</span>',
                            unsafe_allow_html=True
                        )

                else:

                    st.write("No matched skills found.")

            with s2:

                st.subheader("❌ Missing Skills")

                if missing:

                    for skill in missing:
                        st.markdown(
                            f'<span class="skill">✗ {skill}</span>',
                            unsafe_allow_html=True
                        )

                else:

                    st.write("No major missing skills found.")

            # ==============================
            # SKILL VISUALIZATION
            # ==============================

            st.markdown(
                '<div class="section-title">📈 Skill Visualization</div>',
                unsafe_allow_html=True
            )

            matched_count = len(matched)
            missing_count = len(missing)

            total_skills = matched_count + missing_count

            if total_skills > 0:

                matched_percentage = (
                    matched_count / total_skills
                ) * 100

                missing_percentage = (
                    missing_count / total_skills
                ) * 100

                v1, v2 = st.columns(2)

                with v1:

                    st.metric(
                        "Skills Matched",
                        matched_count
                    )

                    st.progress(
                        matched_percentage / 100
                    )

                    st.caption(
                        f"{matched_percentage:.1f}% of identified skills"
                    )

                with v2:

                    st.metric(
                        "Skills Missing",
                        missing_count
                    )

                    st.progress(
                        missing_percentage / 100
                    )

                    st.caption(
                        f"{missing_percentage:.1f}% of identified skills"
                    )

            # ==============================
            # RECOMMENDED SKILLS
            # ==============================

            st.markdown(
                '<div class="section-title">'
                '📚 Recommended Skills to Learn'
                '</div>',
                unsafe_allow_html=True
            )

            recommended_skills = result.get(
                "recommended_skills_to_learn",
                []
            )

            if recommended_skills:

                for skill in recommended_skills:

                    st.write(
                        f"📌 **{skill}**"
                    )

            else:

                st.write(
                    "No additional skills recommended."
                )

            # ==============================
            # RECOMMENDED JOB ROLES
            # ==============================

            st.markdown(
                '<div class="section-title">'
                '💼 Recommended Job Roles'
                '</div>',
                unsafe_allow_html=True
            )

            roles = result.get(
                "recommended_job_roles",
                []
            )

            for role_data in roles:

                role = role_data.get(
                    "role",
                    "Unknown Role"
                )

                percentage = role_data.get(
                    "match_percentage",
                    0
                )

                reason = role_data.get(
                    "reason",
                    ""
                )

                with st.expander(
                    f"💼 {role} — {percentage}% Match"
                ):

                    st.write(reason)

                    st.progress(
                        percentage / 100
                    )

            # ==============================
            # ATS ISSUES
            # ==============================

            st.markdown(
                '<div class="section-title">⚠️ ATS Issues</div>',
                unsafe_allow_html=True
            )

            issues = result.get(
                "ats_issues",
                []
            )

            if issues:

                for issue in issues:

                    st.warning(
                        f"⚠️ {issue}"
                    )

            else:

                st.success(
                    "No major ATS issues detected."
                )

            # ==============================
            # STRENGTHS
            # ==============================

            st.markdown(
                '<div class="section-title">💪 Resume Strengths</div>',
                unsafe_allow_html=True
            )

            strengths = result.get(
                "strengths",
                []
            )

            for strength in strengths:

                st.success(
                    f"✓ {strength}"
                )

            # ==============================
            # IMPROVEMENTS
            # ==============================

            st.markdown(
                '<div class="section-title">'
                '🔧 Improvement Suggestions'
                '</div>',
                unsafe_allow_html=True
            )

            suggestions = result.get(
                "improvement_suggestions",
                []
            )

            for suggestion in suggestions:

                st.info(
                    f"💡 {suggestion}"
                )

            # ==============================
            # AI CAREER ASSESSMENT
            # ==============================

            st.markdown(
                '<div class="section-title">'
                '🧠 AI Career Assessment'
                '</div>',
                unsafe_allow_html=True
            )

            st.write(
                result.get(
                    "summary",
                    "No summary available."
                )
            )

            # ==============================
            # DOWNLOAD RESULT
            # ==============================

            st.markdown(
                '<div class="section-title">'
                '📥 Download Analysis'
                '</div>',
                unsafe_allow_html=True
            )

            json_data = json.dumps(
                result,
                indent=4
            )

            st.download_button(
                label="📥 Download Analysis as JSON",
                data=json_data,
                file_name="resume_analysis.json",
                mime="application/json"
            )


# ==============================
# HISTORY
# ==============================

st.markdown(
    '<div class="section-title">🕘 Analysis History</div>',
    unsafe_allow_html=True
)

history = load_history()

if history:

    for row in history:

        analysis_id = row[0]
        title = row[1]
        match_score = row[2]
        ats_score = row[3]
        quality_score = row[4]

        with st.expander(
            f"#{analysis_id} — {title}"
        ):

            h1, h2, h3 = st.columns(3)

            with h1:
                st.metric(
                    "Job Match",
                    f"{match_score}%"
                )

            with h2:
                st.metric(
                    "ATS Score",
                    f"{ats_score}%"
                )

            with h3:
                st.metric(
                    "Resume Quality",
                    f"{quality_score}%"
                )

else:

    st.info(
        "No previous analyses yet. "
        "Analyze your first resume to create history."
    )