"""
Development Tools API

Endpoints for development utilities like seeding test data.
These endpoints are ONLY available in development/testing environments.
"""
from flask import Blueprint, jsonify, request
from functools import wraps
import os

dev_bp = Blueprint('dev', __name__, url_prefix='/api/dev')

# Allowed environments
ALLOWED_ENVIRONMENTS = ['development', 'testing', 'local']
DEFAULT_SEED_TOKEN = 'dev-seed-token-12345'


def require_dev_environment(f):
    """Decorator: Ensure endpoint only runs in development environment"""
    @wraps(f)
    def decorated(*args, **kwargs):
        env = os.getenv('FLASK_ENV', 'production')
        if env not in ALLOWED_ENVIRONMENTS:
            return jsonify({
                'error': {
                    'code': 'NOT_ALLOWED',
                    'message': 'This endpoint is only available in development environment'
                }
            }), 403
        return f(*args, **kwargs)
    return decorated


def require_seed_token(f):
    """Decorator: Validate seed token header"""
    @wraps(f)
    def decorated(*args, **kwargs):
        expected_token = os.getenv('DEV_SEED_TOKEN', DEFAULT_SEED_TOKEN)
        provided_token = request.headers.get('X-Seed-Token')

        if not provided_token or provided_token != expected_token:
            return jsonify({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid or missing X-Seed-Token header'
                }
            }), 401
        return f(*args, **kwargs)
    return decorated


@dev_bp.route('/seed-analytics', methods=['POST'])
@require_dev_environment
@require_seed_token
def api_seed_analytics():
    """
    POST /api/dev/seed-analytics

    Seed analytics test data.

    Headers:
        X-Seed-Token: <DEV_SEED_TOKEN>

    Body (optional):
        {
            "num_interviews": 15,
            "force": false
        }

    Response:
        {
            "status": "success" | "skipped",
            "interviews_created": 15,
            "demo_user_email": "demo@example.com"
        }
    """
    from backend.tests.seed_analytics_data import seed_analytics_data

    data = request.get_json() or {}
    num_interviews = data.get('num_interviews', 15)
    force = data.get('force', False)

    # Temporarily set ALLOW_SEED_DATA for the function
    os.environ['ALLOW_SEED_DATA'] = 'true'

    try:
        result = seed_analytics_data(
            num_interviews=num_interviews,
            force=force
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SEED_FAILED',
                'message': str(e)
            }
        }), 500
    finally:
        os.environ.pop('ALLOW_SEED_DATA', None)


@dev_bp.route('/seed-analytics', methods=['DELETE'])
@require_dev_environment
@require_seed_token
def api_clear_seed():
    """
    DELETE /api/dev/seed-analytics

    Clear all seed test data.

    Headers:
        X-Seed-Token: <DEV_SEED_TOKEN>

    Response:
        {
            "status": "success" | "skipped",
            "message": "Seed data cleared"
        }
    """
    from backend.database import db
    from backend.models.interview import Interview
    from backend.models.analysis_report import AnalysisReport
    from backend.tests.seed_analytics_data import is_already_seeded, clear_seed_data

    try:
        if is_already_seeded(Interview):
            clear_seed_data(db, Interview, AnalysisReport)
            return jsonify({
                'status': 'success',
                'message': 'Seed data cleared'
            }), 200
        else:
            return jsonify({
                'status': 'skipped',
                'message': 'No seed data to clear'
            }), 200
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'CLEAR_FAILED',
                'message': str(e)
            }
        }), 500


@dev_bp.route('/seed-analytics/status', methods=['GET'])
@require_dev_environment
def api_seed_status():
    """
    GET /api/dev/seed-analytics/status

    Check seed data status.

    Response:
        {
            "is_seeded": true,
            "seed_interview_count": 15,
            "environment": "development"
        }
    """
    from backend.models.interview import Interview
    from backend.tests.seed_analytics_data import is_already_seeded, SEED_MARKER_PREFIX

    seeded = is_already_seeded(Interview)
    seed_count = 0

    if seeded:
        seed_count = Interview.query.filter(
            Interview.title.like(f'{SEED_MARKER_PREFIX}%')
        ).count()

    return jsonify({
        'is_seeded': seeded,
        'seed_interview_count': seed_count,
        'environment': os.getenv('FLASK_ENV', 'production')
    }), 200
