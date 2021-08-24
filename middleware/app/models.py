import mongoengine as me


class User(me.Document):
    username = me.StringField(required=True)
    password= me.StringField(required=True)


class Prefix(me.Document):
    prefix = me.StringField()

    meta = {
        'indexes': [
            'prefix', # normal index
            "$prefix", # text index
        ],
        'index_background': True,
        'auto_create_index': True,
    }

class UserPrefix(me.Document):
    user_id = me.ReferenceField(User)
    prefix_id = me.ReferenceField(Prefix)
    is_allowed = me.BooleanField(default=True)
