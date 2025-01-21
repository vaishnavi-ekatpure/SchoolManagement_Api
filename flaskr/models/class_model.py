from flaskr.config.databaseconfig import db
from sqlalchemy.dialects.postgresql import JSON

class Class(db.Model):
    __tablename__ = 'management_class'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(150), nullable=True)
    class_subject = db.Column(JSON, nullable=False)

    def serialize(self):
        return {
            'id' : self.id,
            'class_name' : self.class_name,
            'class_subject' : self.class_subject
        }