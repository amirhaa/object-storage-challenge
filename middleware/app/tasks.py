import os
import logging
import math
import boto3
from boto3.s3.transfer import TransferConfig
from flask import current_app

from main import celery

logging.basicConfig(level=logging.INFO)


@celery.task(name='upload_to_bucket')
def upload_task(file_path, file_name, bucket_name, acl):
    """
    upload_task receives a file path and a bucket name
    then create a s3 resource and upload the file to
    the provided bucket.
    also check if size of uploaded file is large then
    does a multipart upload to s3 resource.

    :param file_path:
    :param file_name:
    :param bucket_name:
    :return:
    """

    # Calculate total size of the uploader file in bytes
    total_bytes = os.path.getsize(file_path)
    logging.info(f"==================== total size of the file: {total_bytes} bytes =========================")

    # this is the callback that boto3 calls periodically
    # and send the transferred bytes to this callback
    def upload_progress(bytes_transferred):
        logging.info("===========================================================================================")
        logging.info(f"{math.trunc(((bytes_transferred * 100) / total_bytes))}% progressed, "
                     f"transferred {bytes_transferred} bytes of {total_bytes}")
        logging.info("===========================================================================================")

    # Set TransferConfig
    MB = 1024 ** 2
    config = TransferConfig(
        multipart_threshold=50 * MB,  # set the limit of multipart upload to 50 MB
        use_threads=True,
    )

    try:
        s3 = boto3.resource(
            's3',
            endpoint_url=current_app.config['ARVAN_ENDPOINT_URL'],
            aws_access_key_id=current_app.config['ARVAN_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['ARVAN_SECRET_KEY']
        )

        s3.meta.client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=file_name,
            ExtraArgs={
                'ACL': acl,
            },
            Callback=upload_progress,
            Config=config,
        )

    except Exception as exc:
        logging.error(f"================== could not commit a s3 upload, exc: {exc} ======================")
