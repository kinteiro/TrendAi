import pandas as pd
from pathlib import Path
from utils import load_gpt_files, save_gpt_response_txt, initialize_openai


def create_chat_response(client, image_descipcion_prompt, image_url, machine_prompt):
    return client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": image_descipcion_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "low"
                        },
                    },
                ],
            },
            {
                "role": "system",
                "content": machine_prompt,
            },
        ],
        max_tokens=1000,
    )

def get_image_responses(client, image_descipcion_prompt, IMAGES, _ROOT: str) -> list:
    responses_to_df = []
    image_urls = []
    machine_prompt = ""

    if isinstance(IMAGES, dict):
        image_urls = list(IMAGES["Images"].values())
        machine_prompt = IMAGES["Machine_prompt"]
    elif isinstance(IMAGES, str):
        image_urls = [IMAGES]

    for image_url in image_urls:
        response = create_chat_response(client, image_descipcion_prompt, image_url, machine_prompt)

        for file in _ROOT.glob("image_responses/*.txt"):
            file.unlink()

        for choice in response.choices:
            if "NO ES MODA" in choice.message.content.upper(): # TODO: ver si hacer continue o usar la funcion tag_if_image_response_isnot_fashion para etiquetar
                continue
            data = {"timestamp": pd.Timestamp.today().strftime("%Y_%m_%d_%H_%M"),
                    "image_response": choice.message.content,
                    "Fashion_tag": tag_if_image_response_isnot_fashion(choice)}
            responses_to_df.append(data)
            print(choice.message.content[:50])

    return responses_to_df


def tag_if_image_response_isnot_fashion(choice):
    if "NO ES MODA" in choice.message.content.upper():
        return "Imagen no es de moda"
    elif "YES" in choice.message.content.upper():
        return "Imagen es de moda"
    else:
        return None

def get_df_from_list(list_of_dicts: list) -> pd.DataFrame:
    return pd.DataFrame(list_of_dicts)

def lambda_handler(event, context):
    _ROOT = Path(__file__).parent
    # client = initialize_openai()
    client = initialize_openai("OPENAI_API_KEY")
    image_descipcion_prompt = load_gpt_files(_ROOT, "txt")
    IMAGES = load_gpt_files(_ROOT, "json")
    LIST = get_image_responses(client, image_descipcion_prompt, IMAGES, _ROOT)
    df = get_df_from_list(LIST)

    csv_filename = f"{_ROOT}/image_responses/image_responses_{pd.Timestamp.today().strftime('%Y_%m_%d_%H_%M')}.csv"
    df.to_csv(csv_filename, index=False)

    return {
        'statusCode': 200,
        'body': f"CSV file '{csv_filename}' created successfully."
    }

lambda_handler(None, None)