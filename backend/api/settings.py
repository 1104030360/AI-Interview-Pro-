"""
Settings API Blueprint

Endpoints for user settings management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.settings_service import SettingsService

settings_bp = Blueprint('settings', __name__, url_prefix='/api/users/me')


@settings_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """
    Get user settings

    Returns:
        200: {
            'profile': {
                'name': str,
                'role': str,
                'language': str,
                'avatarUrl': str
            },
            'ai': {
                'provider': str,
                'apiKey': str,
                'model': str
            },
            'prompts': {
                'global': str,
                'interviewSuggestions': str,
                'coachChat': str
            }
        }
    """
    user_id = get_jwt_identity()
    settings = SettingsService.get_user_settings(user_id)
    return jsonify(settings), 200


@settings_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """
    Update user settings

    Request Body:
        {
            "profile": {
                "name": "John Doe",
                "role": "Senior Engineer",
                "language": "en",
                "avatarUrl": "..."
            },
            "ai": {
                "provider": "openai",
                "apiKey": "sk-...",
                "model": "gpt-4"
            },
            "prompts": {
                "global": "You are...",
                "interviewSuggestions": "Provide...",
                "coachChat": "You are a coach..."
            }
        }

    Returns:
        200: {
            'message': 'Settings updated successfully',
            'settings': {...}
        }
        400: Invalid request
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            'error': {
                'code': 'INVALID_REQUEST',
                'message': 'Request body is required'
            }
        }), 400

    try:
        settings = SettingsService.update_user_settings(user_id, data)

        return jsonify({
            'message': 'Settings updated successfully',
            'settings': settings
        }), 200

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'UPDATE_FAILED',
                'message': str(e)
            }
        }), 400
