from marshmallow import Schema, fields, validates, ValidationError, INCLUDE
from flaskr.models.user import AuthenticationCustomuser
from flaskr.models.subject_model import Subject
from flaskr.models.class_model import Class
from flaskr.config.databaseconfig import db

class ProfileSchema(Schema):
    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id


    first_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    last_name = fields.String(required=True, validate=lambda x: len(x) >= 5)
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=lambda x: len(x) >= 5)
    phone_number = fields.String(required=True, validate=lambda x: len(x)==10 )

    class Meta:
        unknown = INCLUDE

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

class TeacherProfileSchema(Schema):
    gender = fields.String(required=True)
    address = fields.String(required=True)  
    subject = fields.Integer(required=True)   
    education = fields.String(required=True) 
    profile = fields.String(required=False) 

    gender_value = ['F', 'M']

    class Meta:
        unknown = INCLUDE

    @validates("gender")  
    def validate_gender(self, value):
        if value not in self.gender_value:
            raise ValidationError(f"Gender value is incorrect it should be any value of {self.gender_value} ")
        
    @validates("subject")
    def validate_subject(self, value):
      if not Subject.query.get(value):
          raise ValidationError("Subject is not valid")
      
class StudentProfileSchema(Schema):
    gender = fields.String(required=True)  
    date_of_birth = fields.Date(required=True)  
    address = fields.String(required=True)  
    class_taken = fields.Integer(required=True)
    profile = fields.String(required=False)

    class Meta:
        unknown = INCLUDE

class SpeficicDetailSchema(Schema):
    gender = fields.String(required=True)
    date_of_birth = fields.Date()
    address = fields.String(required=True)
    subject = fields.Integer()
    education = fields.String()
    class_taken = fields.Integer()
    profile = fields.String()
    
    gender_value = ['F', 'M']

    class Meta:
        unknown = INCLUDE

    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if role == 2:
            self.fields["subject"].required = True
            self.fields["education"].required = True
        elif role == 3:
            self.fields["date_of_birth"].required = True
            self.fields["class_taken"].required = True

    @validates("gender")
    def validate_gender(self, value):
        if value not in self.gender_value:
            raise ValidationError(f"Gender value is incorrect, it should be any value of {self.gender_value}")

    @validates("subject")
    def validate_subject(self, value):
        if value and not db.session.get(Subject, value):  
            raise ValidationError("Subject is not valid")

    @validates("class_taken")
    def validate_class_taken(self, value):
        if value and not db.session.get(Class, value):
            raise ValidationError("Class is not valid")    

