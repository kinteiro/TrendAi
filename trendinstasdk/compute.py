from pathlib import Path  
import sys
project_path = Path(__file__).resolve().parents[1].as_posix()
sys.path.append(project_path)
#### ---- IMPORTS ---- ####
from datetime import datetime
from trendinstasdk import create_df, get_urls_to_df   
from common.s3_service import S3Connector

#### ---- GLOBAL VARIABLES ---- ####
INGEST_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")
_EXPORT_PATH = Path(__file__).parent.parent / "data"
BUCKET_NAME = 'trendinstasdk'
_ROOT = Path(__file__).parent.parent
s3 = S3Connector(_ROOT)


### ---- FUNCTIONS ---- ###
def get_valid_input(prompt, data_type):
    while True:
        user_input = input(prompt)
        try:
            return data_type(user_input)
        except ValueError:
            print("Please enter a valid input.")


### ---- MAIN COMPUTE FUNCION ---- ###
def compute():
    """
    Main function to run the program.
    """
    NAME = get_valid_input("Enter the name of the profile: ", str)
    LEN = get_valid_input("Enter the number of images to scrape: ", int)
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
