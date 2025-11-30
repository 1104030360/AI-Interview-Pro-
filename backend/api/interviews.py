"""
Interviews API Blueprint

Endpoints for interview records management and session control
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.interview_service import InterviewService

interviews_bp = Blueprint('interviews', __name__, url_prefix='/api/interviews')


@interviews_bp.route('', methods=['GET'])
@jwt_required()
def get_interviews():
    """
    Get user's interview list with pagination and filtering

    Query Parameters:
        - page: Page number (default 1)
        - pageSize: Items per page (default 20)
        - keyword: Search keyword for title/status
        - mode: Filter by mode (optional)

    Returns:
        200: {
            'items': [...],
            'pagination': {...}
        }
    """
    user_id = get_jwt_identity()

    result = InterviewService.get_user_interviews(
        user_id=user_id,
        page=request.args.get('page', 1, type=int),
        page_size=request.args.get('pageSize', 20, type=int),
        keyword=request.args.get('keyword', ''),
        mode=request.args.get('mode', '')
    )

    return jsonify(result), 200


@interviews_bp.route('/<interview_id>', methods=['GET'])
@jwt_required()
def get_interview(interview_id):
    """
    Get single interview details

    Args:
        interview_id: Interview UUID

    Returns:
        200: Interview data
        404: Interview not found
    """
    user_id = get_jwt_identity()
    interview = InterviewService.get_interview_detail(interview_id, user_id)

    if not interview:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Interview not found'
            }
        }), 404

    return jsonify(interview), 200


@interviews_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """
    Create interview session

    Request Body:
        {
            "title": "Interview Title",
            "status": "pending"  # optional
        }

    Returns:
        201: {
            'sessionId': str,
            'uploadUrls': {...},
            'createdAt': str
        }
        400: Missing required fields
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    if not data or 'title' not in data:
        return jsonify({
            'error': {
                'code': 'MISSING_FIELDS',
                'message': 'Title is required'
            }
        }), 400

    session = InterviewService.create_interview_session(
        user_id=user_id,
        title=data['title'],
        status=data.get('status', 'pending')
    )

    return jsonify(session), 201


@interviews_bp.route('/sessions/<session_id>/complete', methods=['POST'])
@jwt_required()
def complete_session(session_id):
    """
    Complete session and trigger analysis

    Args:
        session_id: Interview UUID

    Request Body:
        {
            "actualDuration": 1800,  # seconds
            "metadata": {...}  # optional
        }

    Returns:
        202: {
            'message': 'Analysis queued',
            'interviewId': str,
            'analysisId': str,
            'estimatedCompletionTime': int
        }
        400: Missing required fields
        404: Session not found
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    if not data or 'actualDuration' not in data:
        return jsonify({
            'error': {
                'code': 'MISSING_FIELDS',
                'message': 'actualDuration is required'
            }
        }), 400

    try:
        result = InterviewService.complete_session(
            session_id=session_id,
            user_id=user_id,
            actual_duration=data['actualDuration'],
            metadata=data.get('metadata', {})
        )

        return jsonify(result), 202

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'SESSION_NOT_FOUND',
                'message': str(e)
            }
        }), 404


@interviews_bp.route('/<interview_id>', methods=['DELETE'])
@jwt_required()
def delete_interview(interview_id):
    """
    Delete interview record

    Args:
        interview_id: Interview UUID

    Returns:
        200: {'message': 'Interview deleted successfully'}
        404: Interview not found
    """
    user_id = get_jwt_identity()

    try:
        InterviewService.delete_interview(interview_id, user_id)

        return jsonify({
            'message': 'Interview deleted successfully'
        }), 200

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
