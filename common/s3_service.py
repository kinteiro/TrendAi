import boto3
import json
import pandas as pd

class S3Connector:
    def __init__(self, root: str):
        self.root = root
        self.connect_to_s3()

    def connect_to_s3(self, json_file: str = "boto3keys.local.json"):
        def open_boto3_keys():
            with open(f"{self.root}/{json_file}", "r") as f:
                return json.load(f)
        boto3keys = open_boto3_keys()
        self.session = boto3.session.Session(**boto3keys)
        self.s3 = self.session.client('s3')

    def download_from_s3(self, bucket_name: str, key: str, file_name: str):
        self.s3.download_file(bucket_name, key, file_name)

    def read_csv_from_s3(self, bucket_name: str, key: str) -> pd.DataFrame:
        obj = self.s3.get_object(Bucket=bucket_name, Key=key)
        return pd.read_csv(obj["Body"])

    def list_files_in_s3(self, bucket_name: str):
        response = self.s3.list_objects_v2(Bucket=bucket_name)
        return [content["Key"] for content in response["Contents"]] 

    def upload_df_to_s3(self, bucket_name: str, df: pd.DataFrame, key: str, mode: str = "w"):
        self.s3.put_object(Bucket=bucket_name, Key=key, Body=df.to_csv(index=False))
        if mode == "a":
            self.s3.put_object(Bucket=bucket_name, Key=key, Body=df.to_csv(index=False, header=False))

    def upload_file_to_s3(self, bucket_name: str, file_name: str, key: str):
        self.s3.upload_file(file_name, bucket_name, key)
