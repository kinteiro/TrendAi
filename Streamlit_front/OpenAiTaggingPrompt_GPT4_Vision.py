from pathlib import Path
import base64
import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from s3_service import S3Connector

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
gpt_model = "gpt-4-vision-preview"
_ROOT = Path(__file__).parent
image_timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")


with open(f"{_ROOT}/image_tagging_prompt.txt", "r") as text_file:
    image_tagging_prompt = text_file.read()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



# Function to get text output from OpenAI
def compute(base64_image, year, designer, temporada):
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
                        "text": image_tagging_prompt
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

    df = pd.DataFrame([{'year': year, 'designer': designer, 'temporada': temporada, 'text': text_output}])
    df_name = f"{image_timestamp}_streamlit_tags.csv"
    # df.to_csv(df_name, index=False)
    try:
        s3 = S3Connector(root=_ROOT)
        s3.upload_df_to_s3(bucket_name='streamlit-tags', df=df, key=f"{year}/{df_name}")
        output_text = f"Carga exitosa a S3: {df_name}"  
        return output_text
    except Exception as e:
        print(f"Error uploading to S3: {e}")

