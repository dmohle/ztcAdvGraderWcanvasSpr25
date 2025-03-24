# grade_one_stu_with_simple_contextual_prompting.py
# Dennis & Omni · 3/23/2025 · Fresno, CA
# grade_one_stu_with_live_points.py
# Dennis & Omni · 3/23/2025 · Fresno, CA

import os
import json
import fitz  # PyMuPDF
import requests
import re
from openai import OpenAI


STUDENT_ID = "138524"
INPUT_FILE = r"C:\2025_Spring\python_canvas_api_master\jsonReview\studentAnswers\student_138524_answers.json"
OUTPUT_FILE = rf"C:\2025_Spring\python_canvas_api_master\jsonReview\graded\{STUDENT_ID}_graded.json"
AP_GUIDE_PATH = r"C:\2025_Spring\python_canvas_api_master\gradingRubrics\apstyle02.pdf"
RUBRIC_PATH = r"C:\2025_Spring\python_canvas_api_master\gradingRubrics\CSBWritingRubric.pdf"

BASE_URL = "https://fresnostate.instructure.com/api/v1"
HEADERS = {"Authorization": f"Bearer {canvas_token}"}
client = OpenAI(api_key=OPENAI_API_KEY)


# ✅ Get actual point values for each question
def fetch_quiz_question_points():
    url = f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/questions"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    questions = response.json()
    return {q["id"]: q["points_possible"] for q in questions}


# ✅ Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# ✅ Load JSON input
def load_student_answers(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ✅ Save JSON output
def save_graded_results(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ✅ Grade a single answer
def grade_with_openai(question_text, student_answer, max_points, grading_guide):
    prompt = f"""
You are a college-level English professor. Grade the student's response fairly using the criteria below.
Limit feedback to 35 words MAX.
Avoid repeating phrases like "Great job!" or "Keep up the good work." If the grammar correction was tricky, say something like "Nice job correcting the tricky X..." 

Grading Reference:
{grading_guide}

-----------------------------
Question (max points = {max_points}):
{question_text}

Student's Answer:
{student_answer}

Return the final grade and brief feedback.
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fair, efficient grader with a helpful, concise style."},
                {"role": "user", "content": prompt}
            ]
        )
        feedback = completion.choices[0].message.content.strip()
        match = re.search(r"(\d+(\.\d+)?)\s*/\s*\d+", feedback)
        score = float(match.group(1)) if match else 0.0
        return score, feedback

    except Exception as e:
        return 0.0, f"⚠️ Grading error: {str(e)}"


# ✅ Grade all answers
def grade_student_answers():
    print("📥 Loading student answers...")
    answers_data = load_student_answers(INPUT_FILE)
    ap_guide = extract_text_from_pdf(AP_GUIDE_PATH)
    rubric_guide = extract_text_from_pdf(RUBRIC_PATH)
    question_points = fetch_quiz_question_points()

    graded_output = {
        "student_id": answers_data["student_id"],
        "graded_answers": []
    }

    for qa in answers_data["answers"]:
        qid = qa["question_id"]
        qtext = qa["question_text"]
        student_answer = qa["answer_text"]
        max_points = question_points.get(qid, 2.0)  # default to 2.0 if not found

        print(f"📝 Grading Question ID: {qid} ({max_points} pts)...")

        guide = ap_guide if max_points == 2.0 else rubric_guide
        score, feedback = grade_with_openai(qtext, student_answer, max_points, guide)

        graded_output["graded_answers"].append({
            "question_id": qid,
            "question_text": qtext,
            "student_answer": student_answer,
            "score": score,
            "feedback": feedback,
            "max_points": max_points
        })

    save_graded_results(graded_output, OUTPUT_FILE)
    print(f"\n✅ Grading complete. Results saved to:\n{OUTPUT_FILE}")


# ✅ Main
if __name__ == "__main__":
    grade_student_answers()
