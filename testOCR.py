from openai import OpenAI

import requests
import base64

with open("testImage.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llava:7b",
    "prompt": "Read the text in this image.",
    "images": [img_base64]
})

print(response.json()["response"])
