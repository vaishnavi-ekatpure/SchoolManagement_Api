import pytest
from flaskr import create_app
from flaskr.config.databaseconfig import db
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from flaskr.models.user import AuthenticationCustomuser, TeacherProfile
from flaskr.models.class_model import Class
from flaskr.models.subject_model import Subject

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with app.app_context():
        db.create_all() 
        
        try:
            test_data()
        except Exception as e:
            print(f"Error occure while inserting data {e}")    

    yield app  

    with app.app_context():
        db.session.remove()
        db.drop_all()  

def test_data():
    hasher = PBKDF2PasswordHasher()
    hashed_password = hasher.encode('Test@123', hasher.salt())  

    users = [
        AuthenticationCustomuser(first_name='admin', last_name='admin', email='admin@gmail.com', 
                                 username='admin', password=hashed_password, role=1, is_active=1),
        AuthenticationCustomuser(first_name='teacher', last_name='teacher', email='teacher@gmail.com', 
                                 username='teacher', password=hashed_password, role=2, is_active=1),
        AuthenticationCustomuser(first_name='student', last_name='student', email='student@gmail.com', 
                                 username='student', password=hashed_password, role=3, is_active=1)
    ]

    classes = [Class(class_name="First Standard"),Class(class_name="Second Standard")]
    subjects = [Subject(name="English"), Subject(name="Hindi")]

    db.session.bulk_save_objects(users + classes + subjects)
    db.session.commit()

    teacher = AuthenticationCustomuser.query.filter_by(username='teacher').first()
    subject = Subject.query.filter_by(name='English').first()

    teacher_profile = TeacherProfile(
        user_id=teacher.id,
        gender='M',
        address='Pune',
        education='B.S.C',
        subject_id=subject.id
    )

    db.session.add(teacher_profile)
    db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions:
    
    def __init__(self, client):
        self._client = client

    def login(self, username, password):
        login_data = {
            'username': username,
            'password': password
        }
        login_response = self._client.post('/auth/login', json=login_data)
        
        assert login_response.status_code == 200 

        login_json = login_response.get_json()
        assert 'access_token' in login_json  

        access_token = login_json['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}"  
        }

        return headers

@pytest.fixture
def auth(client):
    return AuthActions(client)