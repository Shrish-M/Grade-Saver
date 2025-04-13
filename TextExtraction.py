from huggingface_hub import InferenceClient
from huggingface_hub import upload_file
from PIL import Image
import extractAndCompare
from dotenv import load_dotenv
import os

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
print(hf_token)
cleaned_image = extractAndCompare.clean_image_final()
#extractAndCompare.show_image("Cleaned Image", cleaned_image)

image_pil = Image.fromarray(cleaned_image)
image_pil.save("temp_image.png")

url = upload_file(
        path_or_fileobj="temp_image.png",
        path_in_repo="temp-image.png",
        repo_id="ShrishM/grade-saver-images",
        token=hf_token,
        commit_message="Upload temp image",
    )

print(url)



# client = InferenceClient(
#     provider="nebius",
#     api_key="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"
# )
#
# completion = client.chat.completions.create(
#     model="Qwen/Qwen2.5-VL-72B-Instruct",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Describe this image in one sentence."
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
#                     }
#                 }
#             ]
#         }
#     ],
#     max_tokens=512,
# )
#
# print(completion.choices[0].message["content"])