import os
import json
import requests
from dotenv import load_dotenv
import TextExtraction

# Load environment variables from .env file
def return_response():
    load_dotenv()

    # Retrieve your Purdue Gen AI Studio API key from the environment.
    genai_api_key = os.environ.get("API_KEY")
    if not genai_api_key:
        raise EnvironmentError("API_KEY environment variable not set! Please set it in your .env file.")

    ###############################################
    # STEP 1: Load Extracted Text from File
    ###############################################

    # TextExtraction.full_extraction_func()

    extracted_text_file = "extracted_text2.txt"
    try:
        with open(extracted_text_file, "r", encoding="utf-8") as f:
            extracted_text = f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"{extracted_text_file} not found. Ensure your text extraction process has created it.")

    print("Extracted Text:")
    print(extracted_text)
    print("-" * 80)

    ###############################################
    # STEP 2: Load and Format Rubric Data
    ###############################################
    rubric_file = "rubric_data.json"
    try:
        with open(rubric_file, "r", encoding="utf-8") as f:
            rubric_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"{rubric_file} not found. Ensure your extraction script has created it.")

    rubric_text = ""
    for question in sorted(rubric_data.keys()):
        rubric_text += f"{question}:\n"
        # Process main question rubric items
        main_rubrics = rubric_data[question].get("main", [])
        if main_rubrics:
            rubric_text += "  Main Rubric:\n"
            for idx, item in enumerate(main_rubrics, start=1):
                if "-" in item["points"]:
                    rubric_text += f"    Rubric {idx}: {item['points']} — {item['comment']}\n"
        # Process subquestion rubric items
        sub_questions = rubric_data[question].get("sub", {})
        if sub_questions:
            for subq in sorted(sub_questions.keys(), key=lambda x: [int(i) for i in x.split('.')]):
                rubric_text += f"  Subquestion {subq}:\n"
                for idx, item in enumerate(sub_questions[subq], start=1):
                    if "-" in item["points"]:
                        rubric_text += f"    Rubric {idx}: {item['points']} — {item['comment']}\n"
        rubric_text += "\n"

    print("Rubric Text:")
    print(rubric_text)
    print("-" * 80)

    ###############################################
    # STEP 3: Construct the Regrade Request Prompt
    ###############################################
    regrade_prompt = (
        "You are an academic writing assistant. A student is preparing regrade requests for a computer science assignment. "
        "Below is the student's submission (extracted from an image) along with the detailed grading rubric. "
        "For each question where the student lost points (indicated by negative point values in the rubric), generate a separate, "
        "professional, and polite regrade request. Each regrade request should specify the question (and subquestion if applicable) "
        "and explain which rubric items might have been overlooked and why the student's submission meets the expected criteria.\n\n"
        "If the image has fewer questions than in the rubric, then only check the corresponding rubric. Create a regrade request separately for each question.\n\n"
        "Student Submission (Extracted Text):\n"
        f"{extracted_text}\n\n"
        "Rubric Details (only items with point deductions are shown):\n"
        f"{rubric_text}\n\n"
        "Regrade Requests (one per question with deductions):"
    )

    ###############################################
    # STEP 4: Call Purdue Gen AI Studio API for Regrade Requests
    ###############################################
    genai_endpoint = "https://genai.rcac.purdue.edu/api/chat/completions"

    genai_headers = {
        "Authorization": f"Bearer {genai_api_key}",
        "Content-Type": "application/json"
    }

    genai_body = {
        "model": "llama3.1:70b-instruct-q4_K_M",
        "messages": [
            {"role": "user", "content": regrade_prompt}
        ],
        "stream": False
    }

    response = requests.post(genai_endpoint, headers=genai_headers, json=genai_body)
    if response.status_code == 200:
        data = response.json()
        regrade_requests = data["choices"][0]["message"]["content"].strip()
        print("\nGenerated Regrade Requests:")
        print(regrade_requests)
        return regrade_requests
    else:
        raise Exception(f"Error from Gen AI Studio API: {response.status_code}, {response.text}")
        return None
