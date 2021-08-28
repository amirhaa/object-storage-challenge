import os

import boto3
import botocore
from flask import request, current_app, jsonify
from flask.views import MethodView
from werkzeug.utils import secure_filename

__all__ = ['UploadFileApi']



class UploadFileApi(MethodView):
    """
    UploadFileApi is intended to receives a file, bucket, acl
    and save the file then send the file path to a celery task
    (upload_task) to be processed with s3 resource
    """

    def __init__(self):
        super().__init__()

        self.credentials = {
            "endpoint_url": current_app.config['ARVAN_ENDPOINT_URL'],
            "aws_access_key_id": current_app.config['ARVAN_ACCESS_KEY'],
            "aws_secret_access_key": current_app.config['ARVAN_SECRET_KEY'],
        }


    def post(self):
        file = request.files.get('file')
        bucket_name = request.form.get('bucket', None)
        acl = request.form.get('acl', 'private')

        if not bucket_name:
            return jsonify({"error": "bucket is required to proceed"}), 400

        if not file:
            return jsonify({"error": "file field is required to proceed"}), 400

        if not self.bucket_is_available(bucket_name):
            return jsonify({"error": "bucket name does not exists, please first create the bucket"}), 400

        # save the file in the provided folder (current_app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)

        from tasks import upload_task

        try:
            # send file address to the celery task
            upload_task.delay(file_path, file.filename, bucket_name, acl)
        except Exception as exc:
            current_app.logger.error(
                f"could not trigger upload_task celery, exc: {exc}")
            return jsonify({"error": "something went wrong start uploading"}), 400

        # todo: for example notify user with email or push notification
        return jsonify({"result": "uploaded file already started to be processed, you will be notified after it is finished"}), 200

    # create a HEAD request and 
    # checkout if bucket is already created or not
    def bucket_is_available(self, bucket_name):
        try:
            client = boto3.client('s3', **self.credentials)
            client.head_bucket(Bucket=bucket_name)
            return True
        except (client.exceptions.NoSuchBucket, botocore.exceptions.ClientError):
            return False