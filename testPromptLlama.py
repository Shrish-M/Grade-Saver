import os
import json
import base64
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from the environment
genai_api_key = os.environ.get("API_KEY")
if not genai_api_key:
    raise EnvironmentError("API_KEY environment variable not set! Please set it in your .env file.")

hf_api_key = os.environ.get("HF_API_KEY")
if not hf_api_key:
    raise EnvironmentError("HF_API_KEY environment variable not set! Please set it in your .env file.")

###############################################
# STEP 1: Extract Text from Image Using Qwen Online via Hugging Face
###############################################
# Using an image URL for this example.
image_path = "/Users/prathampatel/Documents/test-bash-grade.png"

# --- OPTIONAL: To use a local file, uncomment below:
#image_path = "/path/to/your/image.png"
try:
     with open(image_path, "rb") as image_file:
         image_data = image_file.read()
     image_base64 = base64.b64encode(image_data).decode("utf-8")
except Exception as e:
     raise Exception(f"Error reading image '{image_path}': {e}")

# Here, we'll use the image URL. If you'd like to use a local image file, you can encode it similarly.
# For demonstration, we'll assume the image URL can be used directly by the inference API.
# In many cases, you might want to download and encode a local image.
# For this example, we'll encode an empty string if no local image is provided.
# (Alternatively, you might use a helper method to download and encode the image from the URL.)
#image_base64 = f"(Image available at: {image_url})"

# Build the extraction prompt exactly as specified:
extraction_prompt = (
    "You are a vision-language model. Your task is to extract and return all text present in the image provided below. "
    "The image is given in base64 encoding. Please extract every bit of text exactly as it appears in the image.\n\n"
    "Image (Base64 encoded):\n"
    f"{image_base64}\n\n"
    "Extracted Text:"
)

# Create an InferenceClient for HF using the Hugging Face API key.
hf_client = InferenceClient(provider="hf-inference", api_key=hf_api_key)

# Build the message content for the extraction call.
hf_message = {
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": extraction_prompt
        }
    ]
}

# Call the Qwen model (Qwen2.5-VL-7B-Instruct) via HF Inference API.
hf_response = hf_client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-7B-Instruct",
    messages=[hf_message],
    max_tokens=512,
)
# Extract the text returned by the model.
# extracted_text = hf_response.choices[0].message.strip()
# print("Extracted Text from Image:")
# print(extracted_text)
# Option 1: If the message is a dict with a "content" key:
if isinstance(hf_response.choices[0].message, dict):
    extracted_text = hf_response.choices[0].message.get("content", "").strip()
else:
    extracted_text = str(hf_response.choices[0].message).strip()

print("Extracted Text from Image:")
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

# Build a formatted string from rubric data (only include items with point deductions)
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

###############################################
# STEP 3: Construct the Regrade Request Prompt
###############################################
regrade_prompt = (
    "You are an academic writing assistant. A student is preparing regrade requests for a computer science assignment. "
    "Below is the student's submission (extracted from an image) along with the detailed grading rubric. "
    "For each question where the student lost points (indicated by negative point values in the rubric), generate a separate, "
    "professional, and polite regrade request. Each regrade request should specify the question (and subquestion if applicable) "
    "and explain which rubric items might have been overlooked and why the student's submission meets the expected criteria.\n\n"
    "If the image has less question than in the rubric, then only check the corresponding rubric. Create a regrade request separately"
    "for each question"
    "Student Submission (Extracted Text):\n"
    f"{extracted_text}\n\n"
    "Rubric Details (only items with point deductions are shown):\n"
    f"{rubric_text}\n\n"
    "Regrade Requests (one per question with deductions):"
)

###############################################
# STEP 4: Call Purdue Gen AI Studio API for Regrade Requests
###############################################
# Gen AI Studio API endpoint (OpenAI-compatible)
genai_endpoint = "https://genai.rcac.purdue.edu/api/chat/completions"

# Prepare headers for the Gen AI Studio API call.
genai_headers = {
    "Authorization": f"Bearer {genai_api_key}",
    "Content-Type": "application/json"
}

# Construct the request body with the regrade prompt.
genai_body = {
    "model": "llama3.1:70b-instruct-q4_K_M",
    "messages": [
        {"role": "user", "content": regrade_prompt}
    ],
    "stream": False
}

# Send the regrade request prompt to the Gen AI Studio API.
genai_response = requests.post(genai_endpoint, headers=genai_headers, json=genai_body)
if genai_response.status_code == 200:
    genai_data = genai_response.json()
    regrade_requests = genai_data["choices"][0]["message"]["content"].strip()
    print("\nGenerated Regrade Requests:")
    print(regrade_requests)
else:
    raise Exception(f"Error from Gen AI Studio API: {genai_response.status_code}, {genai_response.text}")
