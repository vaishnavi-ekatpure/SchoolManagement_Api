from flask import Flask, session, request, jsonify, Blueprint
from flaskr.validators.authentication_validator import *
from django.contrib.auth.hashers import PBKDF2PasswordHasher, check_password
from marshmallow import  ValidationError
from flaskr.models.user import *
from flaskr.config.databaseconfig import db
from flaskr.config.extensions import jwt
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity, get_jwt


auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

BLOCKLIST = set()

@auth_routes.route('')
def index():
    try:
        users = AuthenticationCustomuser.query.all()
        users_list = [user.serialize() for user in users]
        print('wertuop')
        return jsonify({'users': users_list})
    except Exception as e:
        print(f"error {e}")

@auth_routes.route('/register', methods=['POST'])
def register():
    schema = RegistrationSchema()  
    try:
        data = schema.load(request.json)
        hasher = PBKDF2PasswordHasher()

        hashed_password = hasher.encode(data['password'], hasher.salt())

        user = AuthenticationCustomuser(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            username = data['username'],
            password = hashed_password,
            role = data['role'],
            is_active = 0
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Registration successful"}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
@auth_routes.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()

    try:
        data = schema.load(request.json)
        
        user = AuthenticationCustomuser.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({"error": "Invalid username"})  
        
        if not user.is_active:
            return jsonify({"error": "Account is inactive"}) 
        
        hasher = PBKDF2PasswordHasher()
        if not hasher.verify(data['password'], user.password):
            return jsonify({"error": "Invalid password"})  
        
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@auth_routes.route('/auth-user', methods=['GET'])
@jwt_required()
def auth_user():
    auth_user = get_jwt_identity()
    return jsonify({'user': auth_user})

@jwt.token_in_blocklist_loader
def check_if_token_is_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        {"error": "User has been logout"}, 401
    )

@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def post():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)

    if session.get('auth_user'):
        session.pop('auth_user')

    return jsonify({'message': 'Successfully logged out'})