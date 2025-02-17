from flask import Blueprint, session, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.models.user import *
from flaskr.models.student_marks_model import *
from flaskr.validators.profile_validator import *
from flaskr.services.profile_store import upload_profile_image
from marshmallow import ValidationError
from flaskr.config.databaseconfig import db

student_routes = Blueprint('student', __name__, url_prefix='/student')

@student_routes.before_request
@jwt_required()
def student_middleware():
    id = get_jwt_identity()
    auth_user = db.session.get(AuthenticationCustomuser, id)

    if auth_user and (auth_user.role== 1 or auth_user.role == 2):
        return jsonify({"error" : "You can't access"}), 401
    
    session['auth_user'] = auth_user.serialize() if auth_user else None

@student_routes.route('/profile', methods=['PUT'])
def profile():
    auth_user = session.get('auth_user')
    if not auth_user:
        return jsonify({"error" : "User not found"})
    
    user = db.session.get(AuthenticationCustomuser, auth_user['id'])
    if not user:
        return jsonify({"error" : "User not found"})
    
    request_data = request.json
    try:
        profile_data = ProfileSchema(user.id).load(request_data)
        student_data = SpeficicDetailSchema(user.role).load(request_data)
        
    except ValidationError as err:
        return jsonify({"error": err.messages})  
    
    user.first_name = profile_data.get('first_name', user.first_name)
    user.last_name = profile_data.get('last_name', user.last_name)
    user.email = profile_data.get('email', user.email)
    user.username = profile_data.get('username', user.username)
    user.phone_number = profile_data.get('phone_number', user.phone_number)

    filename = None
    if 'profile' in student_data:
        data = upload_profile_image(student_data['profile'], 'static/student_profile')
        if not data['flage']:
            return jsonify({'error': data['error']}), 400
        filename = data['filename']

    student_profile = user.student_profile if user.student_profile else StudentProfile(user_id=user.id) 

    student_profile.date_of_birth = student_data.get('date_of_birth', student_profile.date_of_birth)   
    student_profile.gender = student_data.get('gender', student_profile.gender)   
    student_profile.address = student_data.get('address', student_profile.address)   
    student_profile.class_taken_id = student_data.get('class_taken', student_profile.class_taken_id) 

    if filename:
        student_profile.profile = f'static/student_profiles/{filename}'

    if not user.student_profile:
        db.session.add(student_profile)

    db.session.commit()

    return jsonify({'message': 'User updated successfully'}), 200


@student_routes.route('/subject_teachers', methods=['GET'])
def get_subject_teachers():
    auth_user = session.get('auth_user')
    teacher_list = []

    if auth_user['profile']:
        class_id = auth_user['profile']['class_taken_id']
        teacher_list = db.session.query(AuthenticationCustomuser).join(TeacherProfile).filter(
                TeacherProfile.class_teach.contains(class_id)
            ).all()
        teacher_list = [teacher.serialize() for teacher in teacher_list]


    return jsonify({"teacher_list" : teacher_list})    
    

@student_routes.route('/get_marks', methods=['GET'])
def get_marks():
    auth_user = session.get('auth_user')
    marks = StudentMarks.query.filter_by(user_id = auth_user['id']).all()
    marks = [mark.serialize() for mark in marks]

    return jsonify({"data": marks})    