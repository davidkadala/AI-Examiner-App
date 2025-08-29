import streamlit as st
from pdf_utils import smart_extract_text
import os
import tempfile
import json
from grade_logic import grade_answer

st.set_page_config(page_title="AI Examiner", layout="wide")

st.title("ExaminAI")
st.subheader("AI-Powered Examiner")
st.sidebar.subheader("About")
st.sidebar.write("""
         Quickly Grade Your Students Using This AI-Powered Examiner.
         Upload your lesson note, marking scheme, and the responses your student supplied
         for each question, and this app will do the rest!"""
                 )

# Upload Lesson Note and Marking Scheme
lesson_pdf = st.file_uploader("Upload Lesson Note PDF", type="pdf")
scheme_pdf = st.file_uploader("Upload Marking Scheme PDF", type="pdf")

if lesson_pdf is None or scheme_pdf is None:
    st.warning("Please upload both the Lesson Note and Marking Scheme PDFs.")
    st.stop()

if lesson_pdf is not None:
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(lesson_pdf.read())
        lesson_path = tmp_file.name

if scheme_pdf is not None:
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(scheme_pdf.read())
        scheme_path = tmp_file.name

if lesson_path and scheme_path:
    with st.spinner("Extracting text from PDFs..."):
        lesson_text = smart_extract_text(lesson_path)
        scheme_text = smart_extract_text(scheme_path)
    
    st.success("Text extraction complete!")

    # Display extracted previews
    with st.expander("Lesson Note Content (Preview)"):
        st.text_area("Lesson Note", lesson_text[:3000], height=300)
    
    with st.expander("Marking Scheme Content (Preview)"):
        st.text_area("Marking Scheme", scheme_text[:3000], height=300)

if st.button("Continue to Grading Logic"):
    st.session_state['lesson_text'] = lesson_text
    st.session_state['scheme_text'] = scheme_text
    st.success("Ready for next phase: Grading Logic!")

st.header("Student Answer Section")

num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=3)

answers = []
for i in range(num_questions):
answer = st.text_area(f"Answer to Question {i+1}", height=150)
answers.append(answer)

if st.button("Grade All Answers"):
results = []
total_awarded = 0
total_possible = 0

with st.spinner("Grading all answers..."):
   for i, answer in enumerate(answers):
       result = grade_answer(
           st.session_state['lesson_text'],
           st.session_state['scheme_text'],
           answer
       )

       if "error" in result:
           st.error(f"Question {i+1} response error")
           st.text(result['raw_output'])
           continue

       results.append(result)
       total_awarded += result['score_awarded']
       total_possible += result['max_question_score']

# Display all results
st.success("Grading Complete!")
for i, result in enumerate(results):
   st.markdown(f"### Question {i+1}")
   st.markdown(f"**Score:** {result['score_awarded']} / {result['max_question_score']}")
   st.markdown(f"**Reason:** {result['grading_reason']}")
   st.markdown(f"**Tip:** {result['improvement_tip']}")
   st.divider()

st.markdown(f"## Total Score: `{total_awarded} / {total_possible}`")
st.progress(total_awarded / total_possible)
