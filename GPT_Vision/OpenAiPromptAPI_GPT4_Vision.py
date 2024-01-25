import pandas as pd
from openai import OpenAI
from pathlib import Path    
import json
import os
from dotenv import load_dotenv
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

with open (f"{_ROOT}/images_to_promt.json", "r") as json_file:
    IMAGES=json.load(json_file)

response = client.chat.completions.create(
  model= gpt_4,
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": image_descipcion_prompt},
        {
          "type": "image_url",
          "image_url": {
            "url": IMAGES["Images"]["image4"],
            "detail": "low" # "low" or "high" // TODO: Comprobar gasto de tokens  y si es necesario
          },
     
        },
      ],
    },
      {
      "role": "system",
      "content": IMAGES["Machine_prompt"],
  },
  ],
  max_tokens=1000,
)

for choice in response.choices:
    with open (f"{_ROOT}/image_responses/image_response_{_TODAY}.txt", "w") as text_file:
        text_file.write(choice.message.content)
    print(choice.message.content[:50])