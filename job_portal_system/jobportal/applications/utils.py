import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(pdf_file):
    """
    Extract text from uploaded PDF resume
    """
    text = ""
    try:
        # If it's a Django FieldFile, we should open it
        if hasattr(pdf_file, "open"):
            pdf_file.open("rb")
            
        # Seek to beginning if it's a file-like object
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)
            
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        
        # Close if we opened it
        if hasattr(pdf_file, "close"):
            pdf_file.close()
            
        print(f"DEBUG: Extracted {len(text)} characters from PDF")
    except Exception as e:
        print(f"ERROR: Failed to extract text from PDF: {str(e)}")
        # Try to close just in case
        try:
            if hasattr(pdf_file, "close"):
                pdf_file.close()
        except:
            pass
        return ""

    return text


def clean_text(text):
    """
    Clean and normalize text
    """
    if not text:
        print("DEBUG: Text is empty")
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    print(f"DEBUG: Cleaned Text: {text}")
    return text.strip()


def calculate_match_score(resume_file, job_description):
    """
    Calculate similarity score between resume and job description
    """
    if not job_description:
        print("DEBUG: Job description is empty")
        return 0

    # Extract resume text
    resume_text = extract_text_from_pdf(resume_file)

    if not resume_text.strip():
        print("DEBUG: Resume text is empty")
        return 0

    # Clean texts
    cleaned_resume = clean_text(resume_text)
    cleaned_job = clean_text(job_description)

    print(f"DEBUG: Cleaned Resume Length: {len(cleaned_resume)}")
    print(f"DEBUG: Cleaned Job Description Length: {len(cleaned_job)}")

    if not cleaned_resume or not cleaned_job:
        return 0

    try:
        documents = [cleaned_resume, cleaned_job]

        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity[0][0]) * 100
        
        print(f"DEBUG: Calculated Match Score: {score}")
        return round(score, 2)
    except Exception as e:
        print(f"ERROR: Failed during TF-IDF calculation: {str(e)}")
        return 0
