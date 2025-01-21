from flaskr.config.databaseconfig import db

class Subject(db.Model):
    __tablename__ = 'management_subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    

    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name
        }
