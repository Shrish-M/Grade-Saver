import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve your API key from the environment
api_key = os.environ.get("API_KEY")
if not api_key:
    raise EnvironmentError("API_KEY environment variable not set! Check your .env file.")

# Specify the Purdue genAI Studio's OpenAI-compatible endpoint
endpoint = "https://genai.rcac.purdue.edu/api/chat/completions"

# Set up your API headers with the API key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Load the nested rubric data from the JSON file
rubric_file = "rubric_data.json"
try:
    with open(rubric_file, "r", encoding="utf-8") as f:
        rubric_data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"{rubric_file} not found. Ensure your extraction script has created it.")

# Build the rubric text to include in the prompt. This version accounts for both main questions and subquestions.
rubric_text = ""
# Optionally, sort questions if you prefer a specific order. Otherwise, iterate over the keys directly.
for question in sorted(rubric_data.keys()):
    rubric_text += f"{question}:\n"
    # Add main question rubric items, if they exist.
    main_rubrics = rubric_data[question].get("main", [])
    if main_rubrics:
        rubric_text += "  Main Rubric:\n"
        for idx, item in enumerate(main_rubrics, start=1):
            rubric_text += f"    Rubric {idx}: {item['points']} — {item['comment']}\n"
    # Add subquestion rubric items if any.
    sub_questions = rubric_data[question].get("sub", {})
    if sub_questions:
        for subq in sorted(sub_questions.keys(), key=lambda x: [int(i) for i in x.split('.')]):
            rubric_text += f"  Subquestion {subq}:\n"
            for idx, item in enumerate(sub_questions[subq], start=1):
                rubric_text += f"    Rubric {idx}: {item['points']} — {item['comment']}\n"
    rubric_text += "\n"

# Define a sample student submission. This could come from another source or be input by a user.
student_submission = (
    "In my answer, I provided a detailed explanation of the algorithm, including its time complexity and edge-case handling. "
    "I believe the clarity and thoroughness of my explanation meet the expectations outlined in the rubric."
)

# Construct the full prompt to send to the genAI Studio API.
prompt = (
    "You are an academic writing assistant. A student is preparing a regrade request for a computer science assignment. "
    "Below is the student's submission along with the detailed grading rubric (including both main questions and subquestions). "
    "Write a professional, polite, and detailed regrade request that outlines which rubric points might have been overlooked "
    "and explains how the submission meets the expected criteria.\n\n"
    "Student Submission:\n"
    f"{student_submission}\n\n"
    "Rubric Details:\n"
    f"{rubric_text}\n"
    "Regrade Request:"
)

# Uncomment the next line to print the constructed prompt for debugging purposes.
# print("Constructed Prompt:\n", prompt)

# Create the API request body in the OpenAI-compatible format
body = {
    "model": "llama3.1:latest",  # Update this identifier if necessary
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "stream": False  # Set to True if a streaming response is desired
}

# Send the POST request to genAI Studio API
response = requests.post(endpoint, headers=headers, json=body)

# Process the response from the API
if response.status_code == 200:
    data = response.json()
    # In an OpenAI-compatible API response, the content from the assistant is in data["choices"][0]["message"]["content"]
    regrade_request = data["choices"][0]["message"]["content"]
    print("Generated Regrade Request:\n")
    print(regrade_request)
else:
    raise Exception(f"Error: {response.status_code}, {response.text}")
