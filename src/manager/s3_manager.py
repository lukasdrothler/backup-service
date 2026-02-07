from boto3 import client
from botocore.client import Config
import requests

import logging, os
import subprocess

logger = logging.getLogger(__name__)


class S3Manager:
    def __init__(self):
        if "S3_ENDPOINT" in os.environ:
            self.endpoint = os.environ["S3_ENDPOINT"]
            logger.info(f"S3 endpoint set from env: {self.endpoint}")
        else:
            self.endpoint = "https://nbg1.your-objectstorage.com"
            logger.info(f"S3 endpoint set to default: {self.endpoint}")

        if "S3_BUCKET_NAME" in os.environ:
            self.bucket_name = os.environ["S3_BUCKET_NAME"]
            logger.info(f"S3 bucket name set from env: {self.bucket_name}")
        else:
            raise ValueError("S3_BUCKET_NAME environment variable is required")

        if "S3_REGION_NAME" in os.environ:
            self.region_name = os.environ["S3_REGION_NAME"]
            logger.info(f"S3 region name set from env: {self.region_name}")
        else:
            self.region_name = "nbg1"
            logger.info(f"S3 region name set to default: {self.region_name}")

        if "S3_ACCESS_KEY_ID" in os.environ:
            self.access_key_id = os.environ["S3_ACCESS_KEY_ID"].strip()
        else:
            raise ValueError("S3_ACCESS_KEY_ID environment variable is required")

        if "S3_SECRET_KEY" in os.environ:
            self.secret_key = os.environ["S3_SECRET_KEY"].strip()
        else:
            raise ValueError("S3_SECRET_KEY environment variable is required")
        
        if "AGE_PUBLIC_KEY" in os.environ:
            self.age_public_key = os.environ["AGE_PUBLIC_KEY"]
        else:
            raise ValueError("AGE_PUBLIC_KEY environment variable is required")
        
        self.client = self.get_client()
        logger.info("S3 client initialized")


    def get_client(self):
        return client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_key,
            config=Config(
                signature_version='s3v4',
                s3={
                    'payload_signing_enabled': True,
                    'addressing_style': 'virtual',
                },
            )
        )


    def encrypt_age_file(self, file_path, output_file_path=None, cleanup=True):
        if output_file_path is None:
            output_file_path = file_path + ".enc"
        try:
            subprocess.run(['sops', '--encrypt', '--age', self.age_public_key, '--output', output_file_path, file_path])
            logger.info(f"File encrypted: {file_path} to {output_file_path}")
        except Exception as e:
            logger.error(f"Failed to encrypt file: {file_path}. Error: {e}")
            return None

        if cleanup:
            try:
                subprocess.run(['rm', '-f', file_path])
            except Exception as e:
                logger.warning(f"Failed to remove original file: {file_path}. Error: {e}")
        return output_file_path


    def upload_file(self, file_path, key, encrypt=True, cleanup=True):
        if encrypt:
            _file_path = self.encrypt_age_file(file_path, cleanup=cleanup)
        else:
            _file_path = file_path
        try:
            url = self.client.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=3600
            )
            with open(_file_path, 'rb') as f:
                # Get file size for Content-Length header
                file_size = os.path.getsize(_file_path)
                response = requests.put(url, data=f, headers={'Content-Length': str(file_size)})
                response.raise_for_status()
            logger.info(f"File uploaded: {_file_path} to {self.bucket_name}/{key}")
        except Exception as e:
            logger.error(f"Failed to upload file: {_file_path} to {self.bucket_name}/{key}. Error: {e}")

        if cleanup:
            try:
                subprocess.run(['rm', '-f', _file_path])
            except Exception as e:
                logger.warning(f"Failed to remove file: {_file_path}. Error: {e}")