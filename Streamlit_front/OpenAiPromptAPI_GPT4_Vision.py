import pandas as pd
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv
import base64
import requests

load_dotenv()

OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY")
OpenAI.api_key = OPENAI_API_KEY
_TODAY = pd.Timestamp.today().strftime("%Y_%m_%d_%H_%M")
gpt_4 = "gpt-4-vision-preview"
_ROOT = Path(__file__).parent

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

with open (f"{_ROOT}/image_description_promt.txt", "r") as text_file:
    image_descipcion_prompt=text_file.read()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# OpenAI API Key
api_key = OPENAI_API_KEY

# Function to get text output from OpenAI
def text_output(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": image_descipcion_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            },
            {
                "role": "system",
                "content": "Eres el mejor analista de datos experto en moda, diseño marcas de moda y telas, cuando ves una imagen describes lo que ves desde los ojos de un experto en moda, diseño marcas de moda y telas."
            }
            
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()['choices'][0]['message']['content']
