import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# CONFIG (Customize this)
# =========================
SKILLS = [
    "python", "django", "flask", "mysql", "postgresql",
    "docker", "kubernetes", "aws", "azure", "rest",
    "api", "javascript", "react", "node", "git"
]


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {str(e)}")
        return ""

    return text.strip()


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================
# KEYWORD MATCH SCORE
# =========================
def keyword_match_score(resume_text, job_text):
    resume_words = set(resume_text.split())
    job_words = set(job_text.split())

    if not job_words:
        return 0

    matched = resume_words.intersection(job_words)
    return (len(matched) / len(job_words)) * 100


# =========================
# SKILL MATCH SCORE
# =========================
def skill_match_score(resume_text, job_text):
    if not SKILLS:
        return 0

    job_skills = [skill for skill in SKILLS if skill in job_text]
    
    if not job_skills:
        return 0

    found_skills = [skill for skill in job_skills if skill in resume_text]

    return (len(found_skills) / len(job_skills)) * 100


# =========================
# EXPERIENCE EXTRACTION
# =========================
def extract_experience(text):
    """
    Extract years of experience (basic regex)
    Example: "3 years", "5+ years"
    """
    matches = re.findall(r"(\d+)\+?\s+years", text)
    if matches:
        return max([int(m) for m in matches])
    return 0


# =========================
# MAIN MATCH FUNCTION
# =========================
def calculate_match_score(resume_file, job_description):
    if not job_description:
        return 0

    # Extract text
    resume_text = extract_text_from_pdf(resume_file)
    if not resume_text:
        return 0

    # Clean text
    cleaned_resume = clean_text(resume_text)
    cleaned_job = clean_text(job_description)

    if not cleaned_resume or not cleaned_job:
        return 0

    try:
        # -------------------------
        # TF-IDF SIMILARITY
        # -------------------------
        documents = [cleaned_resume, cleaned_job]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        tfidf_score = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0] * 100

        # -------------------------
        # KEYWORD SCORE
        # -------------------------
        keyword_score = keyword_match_score(cleaned_resume, cleaned_job)

        # -------------------------
        # SKILL SCORE
        # -------------------------
        skill_score = skill_match_score(cleaned_resume, cleaned_job)

        # -------------------------
        # EXPERIENCE SCORE
        # -------------------------
        resume_exp = extract_experience(cleaned_resume)
        job_exp = extract_experience(cleaned_job)

        if job_exp > 0:
            exp_score = min(resume_exp / job_exp, 1) * 100
        else:
            exp_score = 50  # neutral if not mentioned

        # -------------------------
        # FINAL WEIGHTED SCORE
        # -------------------------
        final_score = (
            0.5 * tfidf_score +
            0.2 * keyword_score +
            0.2 * skill_score +
            0.1 * exp_score
        )

        return round(final_score, 2)

    except Exception as e:
        print(f"[ERROR] Matching failed: {str(e)}")
        return 0


# =========================
# TEST (Optional)
# =========================
if __name__ == "__main__":
    with open("resume.pdf", "rb") as f:
        job_description = """
        Looking for a Python developer with experience in Django,
        REST APIs, Docker, MySQL, and cloud platforms like AWS.
        Minimum 2 years experience required.
        """

        score = calculate_match_score(f, job_description)
        print(f"\n🔥 Final Match Score: {score}%")