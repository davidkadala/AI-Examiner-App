import os
from groq import Groq
import re
import json
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def grade_answer(lesson_note, marking_scheme, student_answer):
    system_prompt = """
    You are an expert examiner. Grade the student's answer using the marking scheme and lesson note below.
    Ensure to follow the mark allocation for each question and the overall marks for the complete answers.
    First, study the marking scheme and divide it to the respective question numbers mentioned there (Ensure not to
    add the grading criteria of one question to another). Then use
    each question and its question criteria (including mark allocation) to grade the respective student answer. 
    Return a JSON object with the following fields:
    - score_awarded
    - max_question_score
    - max_score
    - grading_reason
    - improvement_tip
    """

    user_prompt = f"""
    Lesson Note:
    \"\"\"{lesson_note}\"\"\"

    Marking Scheme:
    \"\"\"{marking_scheme}\"\"\"

    Student Answer:
    \"\"\"{student_answer}\"\"\"
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
    )

    raw_output = response.choices[0].message.content

    # extract JSON from the raw output
    match = re.search(r'\{[\s\S]*?\}', raw_output)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"error": "Invalid JSON structure from model", "raw_output": raw_output}
    else:
        return {"error": "No JSON detected in model output", "raw_output": raw_output}
