from flaskr.config.databaseconfig import db
from flaskr.models.class_model import Class 
from flaskr.models.subject_model import Subject
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from sqlalchemy.orm import backref
import enum


class AuthenticationCustomuser(db.Model):
    __tablename__ = 'authentication_customuser'
    id = db.Column(db.Integer, primary_key=True)  
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    role = db.Column(db.Integer, default=0)  
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.Integer)
    is_superuser = db.Column(db.Integer,default=0)
    is_staff = db.Column(db.Integer, default=0)
    phone_number = db.Column(db.String(10), nullable=True )

    def serialize(self):
      return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'date_joined': self.date_joined,
            'is_active': self.is_active,
            'profile': self.student_profile.serialize() if self.student_profile else 
                       self.teacher_profile.serialize() if self.teacher_profile else  None
        }

class Gender(enum.Enum):
    M = 'Male'
    F = 'Female'  

class StudentProfile(db.Model):
    __tablename__ = 'student_studentprofile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('authentication_customuser.id'))
    authentication_customuser = db.relationship("AuthenticationCustomuser", backref=backref("student_profile", uselist=False)) 
    date_of_birth = db.Column(db.DateTime)
    gender = db.Column(db.Enum(Gender))
    address = db.Column(db.Text)
    class_taken_id = db.Column(db.Integer, db.ForeignKey('management_class.id'))
    management_class = db.relationship("Class", backref=backref("management_class_student", uselist=False)) 
    profile = db.Column(db.String(150), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender.name if self.gender else None,
            'address': self.address,
            'class_taken_id': self.class_taken_id,
            # 'class_name': self.management_class.class_name if self.management_class else None,
            'profile': self.profile
        }
    
class TeacherProfile(db.Model):
    __tablename__ = 'teacher_teacherprofile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('authentication_customuser.id'))
    authentication_customuser = db.relationship("AuthenticationCustomuser", backref=backref("teacher_profile", uselist=False)) 
    gender = db.Column(db.Enum(Gender))
    address = db.Column(db.Text)
    education = db.Column(db.String)
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('management_class.id'))
    management_class = db.relationship("Class", backref=backref("management_class_teacher", uselist=False)) 
    class_teach = db.Column(JSON, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('management_subject.id'))
    management_subject = db.relationship("Subject", backref=backref("management_subject", uselist=False)) 
    profile = db.Column(db.String(150), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'gender': self.gender.name if self.gender else None,
            'address': self.address,
            'education': self.education,
            'class_teacher_id': self.class_teacher_id,
            'class_teach': self.class_teach,
            'subject_id': self.subject_id,
            'profile': self.profile
        }    
