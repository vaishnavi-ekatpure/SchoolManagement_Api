from marshmallow import Schema, fields, validates, ValidationError
from flaskr.models.user import AuthenticationCustomuser

class ProfileSchema(Schema):
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id


    first_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    last_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=lambda x: len(x) >= 5)
    phone_number = fields.String(required=True, validate=lambda x: len(x)==10 )


    def check_unique_filed(self, field, value):
        return  AuthenticationCustomuser.query.filter(
            getattr(AuthenticationCustomuser, field) == value,
            AuthenticationCustomuser.id != self.user_id
        ).first()


    @validates("username")
    def validate_username(self, value):
        if self.check_unique_filed('username', value):
            raise ValidationError("A user with this username already exists.")


    @validates("email")
    def validate_email(self, value):
        if self.check_unique_filed('email', value):
            raise ValidationError("A user with this email already exists.")
        
    @validates("phone_number")
    def validate_phone_number(self, value):
        if self.check_unique_filed('phone_number', value):
            raise ValidationError("A user with this phone_number already exists.")    