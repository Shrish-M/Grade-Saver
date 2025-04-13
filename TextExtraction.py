from huggingface_hub import InferenceClient
from huggingface_hub import upload_file
from huggingface_hub import HfApi
from PIL import Image
import extractAndCompare
from dotenv import load_dotenv
import os
import base64
import requests

def extract():
    load_dotenv()

    hf_token = os.getenv("HF_TOKEN")
    cleaned_image = extractAndCompare.clean_image_final()

    image_pil = Image.fromarray(cleaned_image)
    image_pil.save("temp_image.png")

    #extractAndCompare.show_image("Cleaned Image", cleaned_image)
    api = HfApi(token=hf_token)
    url = api.upload_file(path_or_fileobj="temp_image.png",  # Path to your local file
        path_in_repo="temp_image.png",       # Desired path/filename in your repo
        repo_id="ShrishM/grade-saver-images",                     # Your Hugging Face repo ID
        repo_type='dataset',
        commit_message="Upload temporary image", create_pr=False)


    print(url)

    url = url.replace("blob", "resolve")

    print(url)


    client = InferenceClient(
        provider="hf-inference",
        api_key=hf_token
    )

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                        {
                                "type": "text",
                                "text": "Please extract text from this image (note that handwriting may be in cursive), ignore background noise, please carefully and correctly extract squished text as well and text from annotations (boxes pointing to text). Label the annotations separately as well. Don't include a concluding message or any lines containing student name or ID"
                        },
                        {
                                "type": "image_url",
                                "image_url": {
                                    "url": "https://cdn-lfs-us-1.hf.co/repos/92/d9/92d95e25c44529467a094e86dcbc6ef8151d421b7727182b46e82c0e28dc0e36/3dddabd608812d0f80c46ce9372a79501341957bc91b0e51cfe4ac196eb30575?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27temp_image.png%3B+filename%3D%22temp_image.png%22%3B&response-content-type=image%2Fpng&Expires=1744537386&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0NDUzNzM4Nn19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy11cy0xLmhmLmNvL3JlcG9zLzkyL2Q5LzkyZDk1ZTI1YzQ0NTI5NDY3YTA5NGU4NmRjYmM2ZWY4MTUxZDQyMWI3NzI3MTgyYjQ2ZTgyYzBlMjhkYzBlMzYvM2RkZGFiZDYwODgxMmQwZjgwYzQ2Y2U5MzcyYTc5NTAxMzQxOTU3YmM5MWIwZTUxY2ZlNGFjMTk2ZWIzMDU3NT9yZXNwb25zZS1jb250ZW50LWRpc3Bvc2l0aW9uPSomcmVzcG9uc2UtY29udGVudC10eXBlPSoifV19&Signature=OKoM2w9kWibhx13stqmjs84XV-TaN66mGfOhKy8dhwm6A%7EZzoApsO60pPRlcg1iWnPpKSr9XeIdBUSO43AjGGhd%7ESnS8vtvLiPjKWfrvfVwhmZITvW0vEruPaJINNz72AJzUgyuftwI3oD0Aud6-w4LBKVUtCGK7-zcNhtnW4BgRpenMQ5MU0sOweYjemiQmVAGXlNvItcFvkRfz9KGRJes-YGnHd8B%7Ef0jotSC4LDtiuYLFSeW48FF5mcAuaxZF7uOFXBXvM2-k0T27DZw17T7mQEZo5XcGabgBoGjjXPEtZD1bgkIMa5z9b7Lc%7EoKSAPr6WoEQVyWZJYAYE74kPQ__&Key-Pair-Id=K24J24Z295AEI9"
                                 }
                        }
                ],
            }
        ],
        max_tokens=1000,
    )
    print("Hello")
    print(completion.choices[0].message["content"])

    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(completion.choices[0].message["content"])

def clean():
    file_path = "extracted_text.txt"
    with open(file_path, 'r') as f:
        lines = f.readlines()

    filtered_lines = [
        line for line in lines
        if "Name:" not in line and "ID" not in line and "CS" not in line
    ]

    with open(file_path, 'w') as f:
        f.writelines(filtered_lines)

def full_extraction_func():
    extract()
    clean()

if __name__ == "__main__":
    extract()
    clean()


