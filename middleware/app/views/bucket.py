import re

from flask import request, jsonify, current_app
from flask.views import MethodView
from models import User, Prefix, UserPrefix
from mongoengine import DoesNotExist
from validators import PrefixApiValidatorSchema

__all__ = ['BucketPrefixApi', 'BucketPrefixApiV2']


class BucketApiMixin(object):
    def ok_response(self):
        return jsonify({'result': 'ok'}), 200

    def disallowed_prefix_response(self, bucket):
        return jsonify({"error": f"you are not allowed to use '{bucket}', please try something else"}), 400

    def already_taken_prefix_response(self, bucket):
        return jsonify({"error": f"cannot use '{bucket}', it is already taken, please try something else"}), 400

    def error_response(self, error, status=400):
        return jsonify(error), status


class BucketPrefixApi(MethodView, BucketApiMixin):
    """
    BucketPrefixApi is used for checking if bucket
    name is valid for the user to create or not
    this view is use mongoengine to check out for
    the results
    """

    # use to set the max length of characters
    # to create combination of prefixes
    # for query on mongo
    prefix_max_length = 6

    def post(self):
        """
        handle post request to /bucket

        :return:
        """
        current_app.logger.info(
            "================== bucket api v1 ======================")

        # without forc=True does not work in production
        body = request.get_json(force=True)

        # Validate post request fields
        errors = PrefixApiValidatorSchema().validate(data=body)
        if errors:
            return self.error_response(errors)

        username = body.get('username')
        bucket = body.get('bucket').lower()

        # Check if user exists with this username and password
        try:
            user = User.objects.get(username=username)
        except DoesNotExist:
            return self.error_response({"error": "user does not exists"}, 404)

        # Check user prefixes (UserPrefix model)
        user_prefixes = UserPrefix.objects.filter(user_id=user.id)
        for user_prefix_obj in user_prefixes:
            # prefix name (str)
            u_prefix = user_prefix_obj.prefix_id.prefix

            if user_prefix_obj.is_allowed and bucket.startswith(u_prefix):
                return self.ok_response()
            elif bucket.startswith(u_prefix):
                return self.disallowed_prefix_response(bucket)

        # Check bucket name in all prefixes (Prefix model)
        query_regex = self.create_query_regex(bucket)
        if not query_regex:
            return self.ok_response()

        for matched in Prefix.objects.filter(prefix=query_regex):
            if bucket.startswith(matched.prefix):
                return self.already_taken_prefix_response(bucket)

        return self.ok_response()

    def prefix_combinations(self, bucket):
        """
        create a list of available combinations
        from the user request bucket name
        to query on mongo to check out
        if user bucket name is started
        with any prefixes in the database or not

        create combinations between 3 and self.prefix_max_length.
        for example if user provided bucket name is:

        'arvanbucket' -> arv, arva, arvan

        :param bucket:
        :return:
        """
        length = len(bucket)
        characters = list(bucket)
        up_to = min(length, self.prefix_max_length)

        for idx in range(up_to):
            if 1 < idx:
                result = characters[0: idx + 1]
                yield "".join(result)

    def create_query_regex(self, bucket):
        """
        Create a regex in order to use in mongo query

        :param bucket:
        :return:
        """
        prefix_gen = self.prefix_combinations(bucket)
        regex_str = f"{''.join([f'{p}|' for p in prefix_gen])}" # 'arv|arva|arvan'
        regex_str = regex_str[:-1]
        if not regex_str:
            # this is the case if prefix_gen returns empty (when len of the bucket is less than 3)
            return False
        return re.compile(regex_str)  # r'arv|arva|arvan'


class BucketPrefixApiV2(MethodView, BucketApiMixin):
    """
        BucketPrefixApiV2 is used for checking if bucket
        name is valid for the user to create or not
        this view is use pymongo to check out for
        the results
    """

    # use to set the max length of characters
    # to create combination of prefixes
    # for query on mongo
    prefix_max_length = 6

    def __init__(self):
        self.user_col = User._get_collection()
        self.prefix_col = Prefix._get_collection()

    def post(self):
        current_app.logger.info(
            "================== bucket api v2 ======================")

        body = request.get_json(force=True)

        # Validate post request fields
        errors = PrefixApiValidatorSchema().validate(data=body)
        if errors:
            return self.error_response(errors)

        username = body.get('username')
        bucket = body.get('bucket').lower()

        # use aggregation to get user prefix names
        for item in self.get_user_prefixes(username):
            if bucket.startswith(item['prefix']):
                if item['is_allowed']:
                    return self.ok_response()
                else:
                    return self.disallowed_prefix_response(bucket)

        # use text index for result
        if list(self.prefix_col.find({"$text": {"$search": f"{self.prefix_combinations(bucket)}"}})):
            return self.already_taken_prefix_response(bucket)

        return self.ok_response()

    def get_user_prefixes(self, username):
        """
            output is like:
                [
                    {'prefix': 'prefix1', 'is_allowed': True},
                    {'prefix': 'prefix2', 'is_allowed': False}
                ]
        """

        pipeline = [
            {"$match": {"username": username}},
            {"$project": {"_id": 1}},
            {"$lookup": {
                "from": "user_prefix", # collection to join
                "localField": "_id", # field from the input doc
                "foreignField": "user_id", # field from the doc of the "from"
                "as": "user_prefix" # output array field
            }
            },
            {"$unwind": "$user_prefix"},
            {"$project": {"user_prefix.prefix_id": 1, "user_prefix.is_allowed": 1}},
            {
                "$lookup": {
                    "from": "prefix",
                    "localField": "user_prefix.prefix_id",
                    "foreignField": "_id",
                    "as": "prefix_item"
                }
            },
            {"$unwind": "$prefix_item"},
            {"$project": {"prefix": "$prefix_item.prefix",
                          "is_allowed": "$user_prefix.is_allowed", "_id": 0}}
        ]

        return self.user_col.aggregate(pipeline)

    def prefix_combinations(self, bucket):
        """
        create a string contains combination
        of names with whitespace between in order
        to query on mongo as a text index

        create combinations between 3 and self.prefix_max_length.
        for example if user provided bucket name is:

        'arvanbucket' -> "arv arva arvan"

        :param bucket:
        :return:
        """
        length = len(bucket)
        characters = list(bucket)
        results = []

        up_to = min(length, self.prefix_max_length)

        for idx in range(length):
            if 1 < idx:
                result = characters[0: idx + 1]
                results.append("".join(result))

        return " ".join(results)
