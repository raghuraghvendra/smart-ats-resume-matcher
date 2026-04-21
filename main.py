import spacy
from spacy.matcher import Matcher
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader
import subprocess

# LOAD MODELS

try:
    nlp = spacy.load("en_core_web_sm")
except:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
    
model = SentenceTransformer('all-MiniLM-L6-v2')


# MATCHER SETUP

matcher = Matcher(nlp.vocab)

patterns = [
    [{"LOWER": "python"}],
    [{"LOWER": "sql"}],
    [{"LOWER": "machine"}, {"LOWER": "learning"}],
    [{"LOWER": "deep"}, {"LOWER": "learning"}],
    [{"LOWER": "ml"}],
    [{"LOWER": "dl"}],
    [{"LOWER": "nlp"}]
]

matcher.add("SKILL", patterns)


# NORMALIZATION

normalization_dict = {
    "ml": "machine learning",
    "machine learning": "machine learning",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "nlp": "natural language processing"
}


# EXTRACT SKILLS

def extract_skills(text):
    doc = nlp(text)
    matches = matcher(doc)

    skills = set()

    for match_id, start, end in matches:
        skill = doc[start:end].text.lower()
        skill = normalization_dict.get(skill, skill)
        skills.add(skill)

    return skills

# EXTRACT EXPERIENCE

def extract_experience(text):
    pattern = r"\d+\+?\s*years?"
    matches = re.findall(pattern, text)

    experience = []

    for match in matches:
        number = re.findall(r"\d+\+?", match)
        if number:
            experience.append(number[0])

    return experience


# PARSE TEXT

def parse_text(text):
    return {
        "skills": extract_skills(text),
        "experience": extract_experience(text)
    }


# SEMANTIC MATCH (OPTIMIZED)

def semantic_match(resume_skills, job_skills, threshold=0.7):
    matched = set()
    missing = set()

    # Precompute embeddings
    resume_embeddings = {
        skill: model.encode(skill) for skill in resume_skills
    }
    job_embeddings = {
        skill: model.encode(skill) for skill in job_skills
    }

    for job_skill, job_emb in job_embeddings.items():
        found = False

        for res_skill, res_emb in resume_embeddings.items():
            sim = cosine_similarity([job_emb], [res_emb])[0][0]

            if sim > threshold:
                matched.add(job_skill)
                found = True
                break

        if not found:
            missing.add(job_skill)

    return matched, missing


# SKILL SCORE

def skill_score(matched, job_skills):
    if len(job_skills) == 0:
        return 0
    return round((len(matched) / len(job_skills)) * 100, 2)


# EXPERIENCE SCORE

def experience_score(resume_exp, job_exp):
    if not resume_exp or not job_exp:
        return "Unknown"

    r = int(resume_exp[0].replace('+', ''))
    j = int(job_exp[0].replace('+', ''))

    if r >= j:
        return "Good"
    elif r >= j - 1:
        return "Close"
    else:
        return "Low"


# FINAL SCORE (WEIGHTED)

def final_score(skill_score_val, exp_match):
    exp_weight = {
        "Good": 1.0,
        "Close": 0.7,
        "Low": 0.3,
        "Unknown": 0.5
    }

    exp_score = exp_weight.get(exp_match, 0.5)

    final = (0.7 * skill_score_val) + (0.3 * exp_score * 100)

    return round(final, 2)


# FINAL MATCH FUNCTION

def match_resume_to_job(resume_data, job_data):
    matched, missing = semantic_match(
        resume_data["skills"],
        job_data["skills"]
    )

    score = skill_score(matched, job_data["skills"])

    exp_match = experience_score(
        resume_data["experience"],
        job_data["experience"]
    )

    final = final_score(score, exp_match)

    return {
        "match_percentage": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_match": exp_match,
        "final_score": final   # 🔥 THIS LINE IS CRITICAL
    }

#PDF upload

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# TEST DATA

resume_text = "I have 2 years experience in NLP and Python"
job_text = "We need Natural Language Processing, SQL and 3 years experience"

resume_data = parse_text(resume_text)
job_data = parse_text(job_text)

result = match_resume_to_job(resume_data, job_data)

print("Resume Data:", resume_data)
print("Job Data:", job_data)
print("Final Result:", result)
