from pathlib import Path
import base64
import requests
import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
gpt_model = "gpt-4-vision-preview"
_ROOT = Path(__file__).parent


with open (f"{_ROOT}/image_description_promt.txt", "r") as text_file:
    image_descipcion_prompt=text_file.read()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



# Function to get text output from OpenAI
def text_output(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": gpt_model,
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
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    text_output = response.json()['choices'][0]['message']['content']

    return text_output
