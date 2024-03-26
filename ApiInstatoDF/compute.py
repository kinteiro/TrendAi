import sys
sys.path.append('/Users/davidmolla/Data/Formacion/MBIT School/00 TFM/TrendAi_repo')
#### ---- IMPORTS ---- ####
from pathlib import Path  # noqa: E402
from ApiInstatoDF import INGEST_DATE, create_df, get_urls_to_df    # noqa: E402
from common.s3_service import S3Connector

#### ---- GLOBAL VARIABLES ---- ####
_EXPORT_PATH = Path(__file__).parent / "data"
BUCKET_NAME = 'trendai-bucket-01'
_ROOT = Path(__file__).parent.parent
s3 = S3Connector(_ROOT)
# s3 = connect_to_s3(_ROOT, json_file="boto3keys.local.json")

### ---- MAIN COMPUTE FUNCION ---- ###

def compute():
    """
    Main function to run the program.
    """
    NAME = input("Enter the name of the profile: ")
    LEN = int(input("Enter the number of images to scrape: "))
    df_data = get_urls_to_df(NAME, LEN)
    df = create_df(df_data)
    # Save the DataFrame to a csv file.
    df.to_csv(f"{_EXPORT_PATH/INGEST_DATE[:7]}-{NAME}.csv", index=False)
    # Upload the DataFrame to S3.
    try:
        s3.upload_df_to_s3(BUCKET_NAME, df, f"{INGEST_DATE[:7]}-{NAME}.csv")
    except Exception as e:
        print(f"--ERROR UPLOADING TO S3--\n{e}")
    

    print(df.head(5))


if __name__ == "__main__":
    compute()
