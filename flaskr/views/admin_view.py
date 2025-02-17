from flask import jsonify, Blueprint, session, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.models.user import AuthenticationCustomuser, TeacherProfile
from flaskr.models.class_model import Class
from flaskr.models.subject_model import Subject
from flaskr.validators.profile_validator import ProfileSchema
from flaskr.config.databaseconfig import db
from marshmallow import Schema, fields, ValidationError, validates
from flask_mail import  Message
from flaskr.config.mailconfig import mail
import os
import string
from sqlalchemy import func

admin_routes = Blueprint('admin', __name__, url_prefix='/admin')

#Middleware for admin route
@admin_routes.before_request
@jwt_required()
def admin_middleware():
    id = get_jwt_identity()
    auth_user = db.session.get(AuthenticationCustomuser, id)
   
    if auth_user and auth_user.role == 2 or auth_user.role == 3:
        return jsonify({"error": "You can't access"})
    
    session['auth_user'] = auth_user.serialize() if auth_user else None

@admin_routes.route('/dashboard', methods=['GET'])
def dashboard():
    users = AuthenticationCustomuser.query  

    active_teacher = users.filter_by(role=2, is_active=True).count()
    inactive_teacher = users.filter_by(role=2, is_active=False).count()

    active_student = users.filter_by(role=3, is_active=True).count()
    inactive_student = users.filter_by(role=3, is_active=False).count()
    
    data = {
            'active_teacher': active_teacher,
            'inactive_teacher': inactive_teacher,
            'active_student': active_student,
            'inactive_student': inactive_student
            }
    
    return jsonify({'data': data})

@admin_routes.route('/profile', methods=['PUT'])
def profile():
    auth_user = session['auth_user']

    if not auth_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = db.session.get(AuthenticationCustomuser, auth_user['id'])

    request_data = request.json
    schema = ProfileSchema(user.id)

    try:
        data = schema.load(request_data)
    except ValidationError as err:
        return jsonify(err.messages) , 400  

    user.first_name = data['first_name'] 
    user.last_name = data['last_name'] 
    user.email = data['email']
    user.username = data['username']
    user.phone_number = data['phone_number']

    db.session.commit()

    return jsonify({'message': 'User updated'})

@admin_routes.route('/classes', methods=['GET'])
def get_classes():
    classes = Class.query.all()
    classes = [ class_item.serialize() for class_item in classes]

    return jsonify({'classes' :classes})

class ClassSubjectSchema(Schema):
    class_subject = fields.List(fields.Int(), required=True)

@admin_routes.route('/add-class-subject/<int:id>', methods=['POST'])
def add_class_subject(id):
    schema = ClassSubjectSchema()
    try:
        class_record = db.session.get(Class,id)
        if not class_record:
            return jsonify({'message': 'Class not found'})
        
        data = schema.load(request.json)
        class_subjects = list(set(data['class_subject']))
        
        existing_ids = {s.id for s in Subject.query.filter(Subject.id.in_(class_subjects)).all()}
       
        if len(existing_ids) != len(class_subjects):
            return jsonify({'message': 'class_subject value is not correct'}), 422
        
        class_record.class_subject = class_subjects
        db.session.commit()

        return jsonify({'message': "Subject list added to class successfully"})

    except ValidationError as err:
        return jsonify(err.messages)    

@admin_routes.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    subjects = [ subject.serialize() for subject in subjects]

    return jsonify({'subjects' : subjects})

class SubjectSchema(Schema):
    name = fields.String(required=True)

@admin_routes.route('/create-subject', methods=['POST'])
def create_subject():
    schema = SubjectSchema()
    try:
        data = schema.load(request.json)
        name = string.capwords(data['name'])

        is_exist = Subject.query.filter_by(name=name).first()
        if is_exist:
            return jsonify({'error': 'Subject already exists'})
        
        subject = Subject(name=name)

        db.session.add(subject)
        db.session.commit()

        return jsonify({'message' : 'Subject created successfully'})

    except ValidationError as err:
        return jsonify(err.messages), 400   

@admin_routes.route('/update-subject/<int:id>', methods=['PUT'])
def update_subject(id):
    schema = SubjectSchema()
    try:
        data = schema.load(request.json)
        already_exist = Subject.query.filter(Subject.id!=id,Subject.name==data['name']).first()

        if already_exist:
            return jsonify({'error': 'Already exist'}),403
        
        subject = db.session.get(Subject,id)

        if not subject:
            return jsonify({'error': 'Subject not found'})
        
        subject.name = data['name']
        db.session.commit()

        return jsonify({'message' : 'Subject edit successfully'})
    except ValidationError as err:
        return jsonify(err.messages)

@admin_routes.route('/delete-subject/<int:id>', methods=['DELETE'])
def delete_subject(id):
    subject = db.session.get(Subject, id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    TeacherProfile.query.filter_by(subject_id=id).update({"subject_id": None})
    
    classes_to_update = Class.query.filter(
        func.json_contains(Class.class_subject, func.json_array(id))
    ).all()

    for class_record in classes_to_update:
        updated_subjects = [sid for sid in class_record.class_subject if sid != int(id)]
        class_record.class_subject = updated_subjects

    db.session.commit()

    db.session.delete(subject)
    db.session.commit()

    return jsonify({'message': 'Subject and its references removed successfully from teacher profiles and classes'}), 200

@admin_routes.route('/students', methods=['GET'])
def get_students():
    students = AuthenticationCustomuser.query.filter_by(role=3).all()

    if students:
        students = [student.serialize() for student in students]

    return jsonify({'students': students})

@admin_routes.route('/change-status/<int:id>', methods=['GET'])
def change_user_status(id):
    user = db.session.get(AuthenticationCustomuser, id)
    if user and user.role != 1:
        user.is_active = not user.is_active
        db.session.commit()

        context={"status": int(user.is_active)}
        
        email_message = Message(
            subject= 'Status Change Email',
            sender= os.getenv('ADMIN_EMAIL'),
            recipients= [user.email],
            html=render_template(template_name_or_list="mails/status_change_mail.html", **context)
        )

        mail.send(email_message)

        return jsonify({'message': 'Status hasn been changed'})
    else:
        return jsonify({'error': 'User not found or you can not change status'})  

@admin_routes.route('/delete-user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = db.session.get(AuthenticationCustomuser,id)

        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user and user.role == 1:
            return jsonify({'error' : 'You can not delete admin'})
        
        db.session.delete(user)
        db.session.commit()

        email_message = Message(
            subject= 'Account Deleted',
            sender= os.getenv('ADMIN_EMAIL'),
            recipients= [user.email],
            html=render_template(template_name_or_list="mails/delete_user_mail.html")
        )

        mail.send(email_message)
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred while deleting the user'}), 500
    
@admin_routes.route('/get-user/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(AuthenticationCustomuser,id)

    if user:
       user = user.serialize()
       
    return jsonify({'user': user})

@admin_routes.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = AuthenticationCustomuser.query.filter_by(role=2).all()

    if teachers:
        teachers = [teacher.serialize() for teacher in teachers]

    return jsonify({'teachers': teachers})

@admin_routes.route('/assign-class-teacher/<int:user_id>/<int:class_id>', methods=['GET'])
def assign_class_teacher(user_id, class_id):
    user = db.session.get(AuthenticationCustomuser, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'})
    elif user.role != 2:
        return jsonify({'error' : 'User is invalid'})
    
    class_exist = db.session.get(Class, class_id)
    if not class_exist:
        return jsonify({'error' : 'Class not found'})
    
    already_assigned_class = TeacherProfile.query.filter_by(class_teacher_id = class_id).first()
    
    if already_assigned_class:
        return jsonify({'error': 'Already class teacher is assigned'})
   
    if not user.teacher_profile:
        return jsonify({'error': 'You can not assign class'})
    
    user.teacher_profile.class_teacher_id = class_id
    db.session.commit()

    return jsonify({'message' : 'Class added successfully'})