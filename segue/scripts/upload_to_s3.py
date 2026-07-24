"""
Upload the JSON audio features to bucket-fsx2px bucket
NB: This code was adapted from https://docs.aws.amazon.com/boto3/latest/guide/s3-uploading-files.html
Parameters:
    - input_path (string): String representing the path of the directory containing the audio features
Returns:
    None
"""
import boto3
import os
from pathlib import Path

def upload_to_s3(input_path):
    input_path = Path(input_path)
    bucket = 'bucket-fsx2px'
    total_uploaded = 0
    s3 = boto3.client('s3')
    print(f"[upload_to_s3][INFO] - Start uploading data to s3")
    for file in os.listdir(input_path):
        if file.endswith(".json"):
            file_name = os.path.join(input_path, file)
            # S3 object name
            object_name = f"audio_features/{file}"
            try:
                s3.upload_file(file_name, bucket, object_name)
            except ClientError as e:
                print(f"[upload_to_s3][ERROR] - Error while uploading file: {e}")
                continue
            total_uploaded += 1
    # Print stats
    print(f"[upload_to_s3][INFO] - Uploaded {total_uploaded:,} files")