from huggingface_hub import InferenceClient
from huggingface_hub import upload_file
from huggingface_hub import HfApi
from PIL import Image
import extractAndCompare
from dotenv import load_dotenv
import os
import base64
import requests


load_dotenv()

hf_token = os.getenv("HF_TOKEN")
cleaned_image = extractAndCompare.clean_image_final()

repo_id = "ShrishM/grade-saver-images"
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
                            "text": "Please extract text from this image, ignore background noise, please carefully and correctly extract squished text as well and text from annotations (boxes pointing ton text). Please make sure to ignore any username or Student ID information in the output."
                    },
                    # {
                    #         "type": "image_url",
                    #         "image_url": {
                    #                 "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                    #         }
                    # },
                    {
                            "type": "image_url",
                            "image_url": {
                                    "url" : "https://cdn-lfs-us-1.hf.co/repos/92/d9/92d95e25c44529467a094e86dcbc6ef8151d421b7727182b46e82c0e28dc0e36/8148ef1b30d7a730fb2e6c26e198e46abcbff87312de402e01d9dd469891fc59?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27temp_image.png%3B+filename%3D%22temp_image.png%22%3B&response-content-type=image%2Fpng&Expires=1744531418&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0NDUzMTQxOH19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy11cy0xLmhmLmNvL3JlcG9zLzkyL2Q5LzkyZDk1ZTI1YzQ0NTI5NDY3YTA5NGU4NmRjYmM2ZWY4MTUxZDQyMWI3NzI3MTgyYjQ2ZTgyYzBlMjhkYzBlMzYvODE0OGVmMWIzMGQ3YTczMGZiMmU2YzI2ZTE5OGU0NmFiY2JmZjg3MzEyZGU0MDJlMDFkOWRkNDY5ODkxZmM1OT9yZXNwb25zZS1jb250ZW50LWRpc3Bvc2l0aW9uPSomcmVzcG9uc2UtY29udGVudC10eXBlPSoifV19&Signature=Z3kvmhT9rZakscYLOrdYczFpLlQBC6voSR%7ErUsKJy9VMRwMXd0X45Se-qWrXOcgwq9kNbfg5j%7E79Fj4b-POWQtAEAm7j5bl8OXa9CNLEgVjyq%7E1X5qW8F6PgUIWBydaZfEywX67kOpTpNB3KPMMLFWcNLiavVG3DJ55XrDVuwTMfYvqLfl5-8jsPtXCUy8vhpfpNzjw3Twhp8OLrMRQ4okGMQXNYv1s1nq9sxjp0db0k%7E5rjdBziUlIUjeJgS3HxkSzpAIMk%7EuSuNWEzDESBqNeH7JMLAfjc8sNejyq1ATMa5bN-2E0kpG-Y8PnnP%7Edk8jSRCpuZgETOO7WGXNFZHQ__&Key-Pair-Id=K24J24Z295AEI9"
                            }
                    }
            ],
        }
    ],
    max_tokens=512,
)
print("Hello")
print(completion.choices[0].message["content"])

with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(completion.choices[0].message["content"])



