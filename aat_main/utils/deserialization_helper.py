from marshmallow import Schema, fields, post_load, ValidationError, validates_schema

from aat_main.models.account_model import AccountModel


class ModelSchema(Schema):
    def get_obj_class(self):
        return None

    @post_load
    def deserialize(self, data, **kwargs):
        obj_class = self.get_obj_class()
        instance = self.context.get('instance')
        if obj_class:
            if instance:
                for k, v in data.items():
                    setattr(instance, k, v)
                return instance
            return obj_class(**data)
        return data


class AccountSchema(ModelSchema):
    id = fields.Integer(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    name = fields.String(required=True)
    role = fields.String(required=True)

    def get_obj_class(self):
        return AccountModel

    @validates_schema
    def validate(self, data, **kwargs):
        if data.get('email'):
            try:
                email = data.get('email')
            except:
                raise ValidationError('Invalid email: {0}'.format(email))
