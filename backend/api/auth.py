from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from backend.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """使用者註冊"""
    data = request.json
    
    # 驗證必填欄位
    if not all(k in data for k in ['email', 'password', 'name']):
        return jsonify({
            'error': {
                'code': 'MISSING_FIELDS',
                'message': 'Email, password, and name are required'
            }
        }), 400
    
    try:
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            role=data.get('role', 'user')
        )
        
        # 生成 tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'userId': user.id,
            'email': user.email,
            'name': user.name,
            'accessToken': access_token,
            'refreshToken': refresh_token
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'REGISTRATION_FAILED',
                'message': str(e)
            }
        }), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    data = request.json
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({
            'error': {
                'code': 'MISSING_FIELDS',
                'message': 'Email and password are required'
            }
        }), 400
    
    try:
        user = AuthService.authenticate(
            email=data['email'],
            password=data['password']
        )
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'userId': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'accessToken': access_token,
            'refreshToken': refresh_token
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_FAILED',
                'message': str(e)
            }
        }), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新 access token"""
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'accessToken': new_access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """取得當前使用者資訊"""
    user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'error': {
                'code': 'USER_NOT_FOUND',
                'message': 'User not found'
            }
        }), 404
    
    return jsonify(user.to_dict()), 200
