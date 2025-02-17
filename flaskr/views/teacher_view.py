from flask import jsonify, Blueprint,session, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.models.user import AuthenticationCustomuser, StudentProfile,TeacherProfile
from flaskr.models.student_marks_model import StudentMarks
from flaskr.config.databaseconfig import db
from flaskr.validators.profile_validator import *
from flaskr.services.profile_store import *

teacher_routes = Blueprint('teacher', __name__,url_prefix='/teacher')

#Middleware for teacher route
@teacher_routes.before_request
@jwt_required()
def teacher_middleware():
    id = get_jwt_identity()
    auth_user = db.session.get(AuthenticationCustomuser,id)
   
    if auth_user and auth_user.role == 1 or auth_user.role == 3:
        return jsonify({"error": "You can't access"})
    
    session['auth_user'] = auth_user.serialize() if auth_user else None

@teacher_routes.route('/dashboard', methods=['GET'])
def dashboard():
    student_mark_list = []
    auth_user = session.get('auth_user')

    if auth_user and auth_user['profile']:
        class_id = auth_user['profile']['class_teacher_id']
        
        student_mark_list = StudentMarks.query.filter_by(student_class_id=class_id).all()
        student_mark_list = [student_mark.serialize() for student_mark in student_mark_list]

    return jsonify({'student_mark_list' : student_mark_list})

@teacher_routes.route('/students', methods=['GET'])
def get_students():
    auth_user = session['auth_user']
    student_list = []
    if auth_user['profile'] and auth_user['profile']['class_teacher_id'] :
        # student_list = StudentProfile.query.filter_by(class_taken_id=auth_user['profile']['class_teacher_id']).all()
        student_list = db.session.query(AuthenticationCustomuser).join(StudentProfile).filter(StudentProfile.class_taken_id == auth_user['profile']['class_teacher_id'])

    if student_list:
        student_list = [student.serialize() for student in student_list]    

    return jsonify({'student_list' : student_list})


@teacher_routes.route('/profile', methods=['PUT'])
def profile():
    auth_user = session.get('auth_user')
    if not auth_user:
        return jsonify({'message': 'User not found'}), 404

    user = db.session.get(AuthenticationCustomuser, auth_user['id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    request_data = request.json

    try:
        profile_data = ProfileSchema(user.id).load(request_data)
        personal_details = SpeficicDetailSchema(user.role).load(request_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    user.first_name = profile_data.get('first_name', user.first_name)
    user.last_name = profile_data.get('last_name', user.last_name)
    user.email = profile_data.get('email', user.email)
    user.username = profile_data.get('username', user.username)
    user.phone_number = profile_data.get('phone_number', user.phone_number)

    filename = None
    if 'profile' in personal_details:
        data = upload_profile_image(personal_details['profile'], 'static/teacher_profile')
        if not data['flage']:
            return jsonify({'error': data['error']}), 400
        filename = data['filename']

    teacher_profile = user.teacher_profile or TeacherProfile(user_id=user.id)

    teacher_profile.gender = personal_details.get('gender', teacher_profile.gender)
    teacher_profile.address = personal_details.get('address', teacher_profile.address)
    teacher_profile.subject_id = personal_details.get('subject', teacher_profile.subject_id)
    teacher_profile.education = personal_details.get('education', teacher_profile.education)

    if filename:
        teacher_profile.profile = f'static/teacher_profiles/{filename}'

    if not user.teacher_profile:
        db.session.add(teacher_profile)

    db.session.commit()

    return jsonify({'message': 'User updated successfully'}), 200