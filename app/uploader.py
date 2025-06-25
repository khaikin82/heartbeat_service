import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_UPLOAD_PREFIX,
)


def upload_directory_to_s3(directory_path: str):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, directory_path)
            s3_path = f"{S3_UPLOAD_PREFIX}/{relative_path}"

            try:
                s3.upload_file(local_path, S3_BUCKET_NAME, s3_path)
                print(f"[✓] Uploaded {local_path} to s3://{S3_BUCKET_NAME}/{s3_path}")
            except (BotoCoreError, ClientError) as e:
                print(f"[X] Failed to upload {local_path}: {e}")
