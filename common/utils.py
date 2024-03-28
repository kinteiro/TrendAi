import json 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv
import boto3
load_dotenv()
_TODAY = pd.Timestamp.today().strftime("%Y_%m_%d_%H_%M")

def initialize_openai(openai_api_key: str):
    OPENAI_API_KEY = os.getenv(openai_api_key)
    OpenAI.api_key = OPENAI_API_KEY
    return OpenAI(api_key=OPENAI_API_KEY)

def get_today_string() -> str:
    return datetime.today().strftime('%Y%m%d')


def get_last_month_int(nmonth:int = 1) -> int:
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    return (first_day_of_current_month - relativedelta(months=nmonth)).month


def load_gpt_files(code_bucket: str, type_file: str):
    if type_file == "json":
        with open(f"{code_bucket}/images_to_promt.json", "r", encoding='utf-8') as f:
            return json.load(f)
    elif type_file == "txt":
        with open(f"{code_bucket}/image_description_promt.txt", "r", encoding='utf-8') as f:
            return f.read()
    elif type_file == "system":
        with open(f"{code_bucket}/System_description_prompt.txt", "r", encoding='utf-8') as f:
            return f.read()

def save_gpt_response_txt(code_bucket: str, response: str):
    with open(f"{code_bucket}/image_responses/image_response_{_TODAY}.txt", "w") as text_file:
        text_file.write(response)


def connect_to_s3(_ROOT: str):
    def openboto3keys(_ROOT: str, json_file: str = "boto3keys.local.json"):
        with open(f"{_ROOT}/{json_file}", "r") as f:
            return json.load(f)
    boto3keys = openboto3keys(_ROOT)
    session = boto3.session.Session(**boto3keys)
    s3 = session.client('s3')
    return s3