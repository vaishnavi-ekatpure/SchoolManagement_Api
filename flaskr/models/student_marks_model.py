from flaskr.config.databaseconfig import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import backref

class StudentMarks(db.Model):
    __tablename__ = 'student_studentmarks'
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer)
    marks = db.Column(JSON)
    student_class_id = db.Column(db.Integer, db.ForeignKey('management_class.id'))
    management_class = db.relationship("Class", backref=backref("student_class", uselist=False)) 
    user_id = db.Column(db.Integer, db.ForeignKey('authentication_customuser.id'))
    authentication_customuser = db.relationship("AuthenticationCustomuser", backref=backref("profile", uselist=False)) 


    def serialize(self):
        return {
            'id' : self.id,
            'semester' : self.semester,
            'marks' : self.marks,
            'student_class_id' : self.student_class_id,
            'user_id' : self.user_id,
            'user_details': self.authentication_customuser.serialize() if self.authentication_customuser else None
        }