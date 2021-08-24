from marshmallow import Schema, fields, validate


class PrefixApiValidatorSchema(Schema):
    """
    validation class to check post request data
    """
    username = fields.Str(required=True, validate=validate.Length(min=3))
    bucket = fields.Str(required=True, validate=validate.Length(min=3))