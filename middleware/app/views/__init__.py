from flask import Blueprint

from .bucket import BucketPrefixApi, BucketPrefixApiV2
from .upload import UploadFileApi

bucket_api_blueprint = Blueprint("bucket_api", __name__)
bucket_api_v2_blueprint = Blueprint("bucket_api_v2", __name__)
upload_file_blueprint = Blueprint("upload_file", __name__)

bucket_api_blueprint.add_url_rule(
    "/bucket",
    view_func=BucketPrefixApi.as_view('bucket_prefix_api'),
    methods=["POST"]
)
bucket_api_v2_blueprint.add_url_rule(
    "/bucket-v2",
    view_func=BucketPrefixApiV2.as_view('bucket_prefix_api_v2'),
    methods=["POST"]
)
upload_file_blueprint.add_url_rule(
    "/upload",
    view_func=UploadFileApi.as_view('upload_file'),
    methods=["POST"]
)
