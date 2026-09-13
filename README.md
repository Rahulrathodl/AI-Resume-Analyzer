# 🤖 AI Resume Analyzer

An AI-powered web application that analyzes a resume against a target job description and provides **ATS scoring, job matching, skill-gap analysis, resume quality evaluation, and job-role recommendations**.

## 🚀 Features

* 📄 Upload resume in PDF format
* 🎯 Calculate job match score
* 🤖 Analyze ATS compatibility
* ⭐ Evaluate resume quality
* 📊 Analyze section completeness
* 🔑 Identify matched and missing skills
* 📚 Recommend skills to learn
* 💼 Recommend suitable job roles
* ⚠️ Identify ATS-related issues
* 💡 Provide resume improvement suggestions
* 🧠 Generate an AI career assessment
* 💾 Store analysis history using SQLite
* 📥 Download analysis results as JSON

## 🛠️ Technologies Used

* **Python**
* **Streamlit** – Web application interface
* **Google Gemini AI** – Resume analysis and recommendations
* **pdfplumber** – PDF text extraction
* **SQLite** – Analysis history storage

## 🏗️ System Architecture

```text
User
  │
  ├── Resume PDF
  └── Job Description
          │
          ▼
   Streamlit Web App
          │
          ▼
    PDF Text Extraction
       (pdfplumber)
          │
          ▼
      Gemini AI
          │
          ├── Job Match Analysis
          ├── ATS Analysis
          ├── Skill Analysis
          ├── Resume Quality
          └── Job Role Recommendations
          │
          ▼
    Results Dashboard
          │
          ▼
     SQLite History
```

## ⚙️ How It Works

1. The user uploads a resume in PDF format.
2. The system extracts the resume text using **pdfplumber**.
3. The user enters a target job role and job description.
4. The resume and job requirements are analyzed using **Google Gemini AI**.
5. The system evaluates:

   * Job match
   * ATS compatibility
   * Resume quality
   * Skills
   * ATS issues
   * Career opportunities
6. The results are displayed in an interactive **Streamlit dashboard**.
7. Analysis results can be stored in SQLite and downloaded as JSON.

## 📊 Example Analysis

For a Python Developer job, the system can provide results such as:

* **Job Match:** 78%
* **ATS Score:** 76%
* **Resume Quality:** 75%
* **ATS Friendliness:** Good

It can also identify matched skills, missing skills, recommended skills, ATS issues, and suitable job roles.

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rahulrathodl/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Gemini API Key

Set your Gemini API key as an environment variable.

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

> ⚠️ Never upload your real API key to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
AI-Resume-Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .venv/
└── history.db
```

> `.venv` and `history.db` are excluded from GitHub using `.gitignore`.

## 🎯 Project Objective

The main objective of this project is to help students and job seekers understand how well their resumes match a specific job description and improve their chances of passing ATS-based resume screening.

## 🔮 Future Enhancements

* Resume section-by-section scoring
* More advanced keyword matching
* Resume improvement using AI-generated suggestions
* Multiple resume comparison
* Public cloud deployment
* Support for additional document formats
* Job description analysis from URLs

## 👨‍💻 Author

**Rahul Pathlavath**

B.Tech Computer Science & Engineering Student

## 📌 Project Status

**Completed – Initial Version**
