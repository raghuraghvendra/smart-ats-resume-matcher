import streamlit as st
from main import (
    parse_text,
    match_resume_to_job,
    extract_text_from_pdf
)

st.title("🚀 Smart ATS Resume Matcher")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
resume_input = st.text_area("OR Paste Resume Text")
job_input = st.text_area("Paste Job Description")

if st.button("Analyze"):

    # -----------------------------
    # HANDLE RESUME INPUT
    # -----------------------------
    resume_text = None

    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)

    elif resume_input.strip():
        resume_text = resume_input

    # DEBUG (temporary)
    st.write("DEBUG resume_text:", resume_text)

    if not resume_text:
        st.warning("Please upload a PDF or paste resume text.")
        st.stop()

    # -----------------------------
    # HANDLE JOB INPUT
    # -----------------------------
    if not job_input.strip():
        st.warning("Please enter job description.")
        st.stop()

    # DEBUG (temporary)
    st.write("DEBUG job_input:", job_input)

    # -----------------------------
    # PROCESS
    # -----------------------------
    resume_data = parse_text(resume_text)
    job_data = parse_text(job_input)

    result = match_resume_to_job(resume_data, job_data)

    # DEBUG result
    st.write("DEBUG result:", result)

    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("📊 Final Score")
    st.success(f"{result['final_score']} %")

    st.subheader("✅ Matched Skills")
    st.write(result["matched_skills"])

    st.subheader("❌ Missing Skills")
    st.write(result["missing_skills"])

    st.subheader("📈 Experience Match")
    st.write(result["experience_match"])