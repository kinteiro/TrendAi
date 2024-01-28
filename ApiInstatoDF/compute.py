# import sys
import logging
from azure.functions import HttpRequest, HttpResponse
from datetime import datetime

# sys.path.append('/Users/davidmolla/Data/Formacion/MBIT School/00 TFM/TrendAi_repo')
#### ---- IMPORTS ---- ####
from pathlib import Path  # noqa: E402

from .ApiInstatoDF import create_df, get_urls_to_df  # noqa: E402

# from common.utils import connect_to_s3, upload_to_s3
from common.utils import connect_to_s3, upload_to_s3  # noqa: E402

#### ---- GLOBAL VARIABLES ---- ####
INGEST_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")
_EXPORT_PATH = Path(__file__).parent / "data"
BUCKET_NAME = "trendai-bucket-01"
_ROOT = Path(__file__).parent.parent

### ---- MAIN COMPUTE FUNCION ---- ###


def main(req: HttpRequest) -> HttpResponse:
    req_body = req.get_json()
    """
    Main function to run the program.
    """
    s3 = connect_to_s3(_ROOT, json_file="boto3keys.local.json")
    NAME = req_body.get("name")
    LEN = req_body.get("len")
    df_data = get_urls_to_df(NAME, LEN)
    df = create_df(df_data)
    # Save the DataFrame to a csv file.
    df.to_csv(f"{_EXPORT_PATH/INGEST_DATE[:7]}-{NAME}.csv", index=False)
    # Upload the DataFrame to S3.
    try:
        upload_to_s3(s3, BUCKET_NAME, df, f"{INGEST_DATE[:7]}-{NAME}.csv")
    except Exception as e:
        logging.info(f"--ERROR UPLOADING TO S3--\n{e}")

    return HttpResponse(
        f"""Downloaded {len(df)} images from {NAME}.
        Ingested {INGEST_DATE}.
        Uploaded to S3 bucket {BUCKET_NAME}.""",
        status_code=200,
    )


# if __name__ == "__main__":
#     main()
