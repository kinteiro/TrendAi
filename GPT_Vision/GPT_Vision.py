import pandas as pd
from pathlib import Path
import sys
# Obtén la ruta del directorio principal de tu proyecto
project_path = Path(__file__).resolve().parents[1].as_posix()
sys.path.append(project_path)
from common.utils import load_gpt_files, initialize_openai  
from common.s3_service import S3Connector


def get_image_responses(client, image_descipcion_prompt, system_prompt, df) -> list:
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
                    "content": system_prompt,
                },
            ],
            max_tokens=1000,
        )

        for choice in response.choices:
            data = {
                "timestamp": pd.Timestamp.now().strftime("%Y_%m_%d_%H_%M_%S"),  # Un timestamp único para cada fila
                "image_response": choice.message.content,
                "url": row["url"],
                "page_url": row["page_url"],
                "designer": row["designer"],
                "temporada": row["temporada"],
                "year": row["year"],
                "tipo": row.get("tipo"),  # Usar row.get() para manejar casos donde la columna puede no existir
                "city": row.get("city"),
            }
            responses_to_df.append(data)
            print(index, choice.message.content[:50])

    return responses_to_df


def get_df_from_list(list_of_dicts: list) -> pd.DataFrame:
    return pd.DataFrame(list_of_dicts)


def load_processed_df_for_compare(s3) -> pd.DataFrame:
    df = s3.read_csv_from_s3("gpt-responses", "GPT_Responses.csv")
    return df


def compare_dfs(processed_df, raw_df) -> pd.DataFrame:
    processed_df = processed_df.groupby(["designer", "temporada", "city"]).sample(1)
    raw_df = raw_df.groupby(["designer", "temporada", "city"]).sample(1)
    return pd.concat([processed_df, raw_df]).drop_duplicates(keep=False, subset=["page_url"], ignore_index=True)

def wrangling_raw_df(raw_df):
    supported_ends = ['png', 'jpeg', 'gif', 'webp', "jpg"]
    raw_df = raw_df[raw_df["url"].str.endswith(tuple(supported_ends))]
    return raw_df


def main():
    _ROOT = Path(__file__).parent
    client = initialize_openai("OPENAI_API_KEY")
    s3 = S3Connector(_ROOT.parent.as_posix())
    processed_df = load_processed_df_for_compare(s3)
    raw_df = s3.read_csv_from_s3("fn-scrapping", "FN_designer_and_images.csv")
    raw_df = wrangling_raw_df(raw_df)
    df = compare_dfs(processed_df, raw_df)
    if not df.empty:
        image_descipcion_prompt = load_gpt_files(_ROOT, "txt")
        system_prompt = load_gpt_files(_ROOT, "system")
        list_responses = get_image_responses(client, image_descipcion_prompt, system_prompt, df)
        df_result = get_df_from_list(list_responses)
        df_result = pd.concat([processed_df, df_result], ignore_index=True)
        try:
            s3.upload_df_to_s3("gpt-responses", df_result, "GPT_Responses.csv")
        except Exception as e:
            print(f"--ERROR UPLOADING TO S3--\n{e}")
            csv_filename = f"{project_path}/data/image_responses/image_responses_{pd.Timestamp.today().strftime('%Y_%m_%d_%H_%M')}.csv"
            df_result.to_csv(csv_filename, index=False)
    else:
        print("No hay nuevas imágenes para procesar.")


if __name__ == "__main__":
    main()