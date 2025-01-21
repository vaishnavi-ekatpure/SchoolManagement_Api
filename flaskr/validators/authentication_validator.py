from marshmallow import Schema, fields, validates, ValidationError
from flaskr.models.user import *

class RegistrationSchema(Schema):
    first_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    last_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=lambda x: len(x) >= 5)
    password = fields.String(required=True, validate=lambda x: len(x) >= 8)
    role = fields.Integer(required=True, validate=lambda x: x in [2,3])

    @validates("username")
    def validate_username(self, value):
        result = AuthenticationCustomuser.query.filter_by(username=value).first()
        if result:
            raise ValidationError("A user with this username already exists.")

    @validates("email")
    def validate_email(self, value):
        result = AuthenticationCustomuser.query.filter_by(email=value).first()
        if result:
            raise ValidationError("A user with this email already exists.")
        
class LoginSchema(Schema):

    username = fields.String(required=True, validate=lambda x: len(x) >= 5)
    password = fields.String(required=True, validate=lambda x: len(x) >= 8)        
