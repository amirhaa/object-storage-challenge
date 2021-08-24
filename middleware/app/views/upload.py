import logging
import os

from flask import request, current_app, jsonify
from flask.views import MethodView
from werkzeug.utils import secure_filename

__all__ = ['UploadFileApi']

logging.basicConfig(level=logging.INFO)


class UploadFileApi(MethodView):
    """
    UploadFileApi is intended to receives a file, bucket, acl
    and save the file then send the file path to a celery task
    (upload_task) to be processed with s3 resource
    """

    def post(self):
        file = request.files.get('file')
        bucket_name = request.form.get('bucket', None)
        acl = request.form.get('acl', 'private')

        if not bucket_name:
            return jsonify("bucket is required to proceed"), 400

        # save the file in the provided folder (current_app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)

        from tasks import upload_task

        try:
            # send file address to the celery task
            upload_task.delay(file_path, file.filename, bucket_name, acl)
        except Exception as exc:
            logging.error(f"could not trigger upload_task celery, exc: {exc}")
            return jsonify("something went wrong start uploading"), 400

        # todo: for example notify user with email or push notification
        return jsonify("uploaded file already started to be processed, you will be notified after it is finished"), 200
