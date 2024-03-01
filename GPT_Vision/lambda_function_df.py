import pandas as pd
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv
import sys
# Obtén la ruta del directorio principal de tu proyecto
project_path = "/Users/davidmolla/Data/Formacion/MBIT School/00 TFM/TrendAi_repo"
sys.path.append(project_path)
from common.utils import load_gpt_files, initialize_openai, save_gpt_response_txt # FIX: import from common.utils  

def get_image_responses(client, image_descipcion_prompt, df, _ROOT: str) -> list:
    responses_to_df = []

    for index, row in df.iterrows():
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": image_descipcion_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": row["url"],
                                "detail": "low"
                            },
                        },
                    ],
                },
                {
                    "role": "system",
                    "content": "Eres el mejor analista de datos experto en moda, diseño marcas de moda y telas, cuando ves una imagen describes lo que ves desde los ojos de un experto en moda, diseño marcas de moda y telas.",
                },
            ],
            max_tokens=1000,
        )

        for file in _ROOT.glob("image_responses/*.txt"):
            file.unlink()

        for choice in response.choices:
            data = {
                "timestamp": pd.Timestamp.today().strftime("%Y_%m_%d_%H_%M"),
                "image_response": choice.message.content,
                "url": row["url"],
                "designer": row["designer"],
                "temporada": row["temporada"],
                "year": row["year"]
            }
            responses_to_df.append(data)
            print(index, choice.message.content[:50])

    return responses_to_df

def get_df_from_list(list_of_dicts: list) -> pd.DataFrame:
    return pd.DataFrame(list_of_dicts)

def lambda_handler(event, context):
    _ROOT = Path(__file__).parent
    # client = initialize_openai()
    client = initialize_openai("OPENAI_API_KEY")
    df = pd.read_csv("vogue_season_2_reduced.csv")
    image_descipcion_prompt = load_gpt_files(_ROOT, "txt")

    LIST = get_image_responses(client, image_descipcion_prompt, df, _ROOT)
    df_result = get_df_from_list(LIST)

    csv_filename = f"{_ROOT}/image_responses/image_responses_{pd.Timestamp.today().strftime('%Y_%m_%d_%H_%M')}.csv"
    df_result.to_csv(csv_filename, index=False)

    return {
        'statusCode': 200,
        'body': f"CSV file '{csv_filename}' created successfully."
    }

lambda_handler(None, None)
