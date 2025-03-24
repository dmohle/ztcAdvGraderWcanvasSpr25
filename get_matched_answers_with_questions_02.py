# get_matched_answers_with_questions_02.py
# dH 3/23/2025
# this works, 3/23/25, 15.05, Fresno, CA
# stores student answers in JSON objects in
# C:\2025_Spring\python_canvas_api_master\jsonReview\studentAnswers

# get_matched_answers_with_questions.py
# dH + Omni, 3/23/2025, Fresno, CA
# Stores student answers in JSON format at:
# C:\2025_Spring\python_canvas_api_master\jsonReview\studentAnswers

import requests
from bs4 import BeautifulSoup
import json
import os

# ✅ Canvas API Credentials
canvas_token = '13199~VmDTLerMJVWErfrWn9L28YraaWyEFPMmJADATTVFT7MzF7GQLwVzHPYAtB6N7VTF'
course_id = '105109'
quiz_id = '358458'
assignment_id = '1618986'
student_id = 138524

# ✅ Base URL and headers
BASE_URL = "https://fresnostate.instructure.com/api/v1"
HEADERS = {"Authorization": f"Bearer {canvas_token}"}


def fetch_quiz_questions():
    """Get quiz question text and map by question_id"""
    url = f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/questions"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    quiz_data = response.json()

    return {
        q["id"]: BeautifulSoup(q["question_text"], "html.parser").get_text(strip=True)
        for q in quiz_data
    }


def fetch_submission_with_history():
    """Get single student's submission including submission_history"""
    url = f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}?include[]=submission_history"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def create_JSON_object_for_student_138524():
    print("📥 Fetching submission and quiz questions...")
    questions = fetch_quiz_questions()
    submission = fetch_submission_with_history()

    submission_data = submission.get("submission_history", [])[-1].get("submission_data", [])
    result = {
        "student_id": student_id,
        "answers": []
    }

    for entry in submission_data:
        qid = entry.get("question_id")
        answer_html = entry.get("text", "")
        answer_text = BeautifulSoup(answer_html, "html.parser").get_text(strip=True)
        question_text = questions.get(qid, "[Question text not found]")

        result["answers"].append({
            "question_id": qid,
            "question_text": question_text,
            "answer_text": answer_text
        })

    # ✅ Output path
    output_dir = r"C:\2025_Spring\python_canvas_api_master\jsonReview\studentAnswers"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "student_138524_answers.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\n✅ JSON object written to:\n{output_file}")


if __name__ == "__main__":
    create_JSON_object_for_student_138524()
