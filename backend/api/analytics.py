"""
Analytics API Blueprint

Provides endpoints for:
- Performance trend visualization (time-series data)
- User statistics summary (aggregated metrics)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/performance-trend', methods=['GET'])
@jwt_required()
def get_performance_trend():
    """
    Get performance trend data for charting

    Query Parameters:
        timeRange: Time range filter ('1W', '1M', '3M', 'All')
        metric: Metric type ('Tone', 'Professionalism', 'Technical', 'Overall')

    Returns:
        200: Trend data with date/value pairs
        400: Invalid parameters
    """
    user_id = get_jwt_identity()
    time_range = request.args.get('timeRange', '1W')
    metric = request.args.get('metric', 'Professionalism')

    # Validate parameters
    valid_ranges = ['1W', '1M', '3M', 'All']
    valid_metrics = ['Tone', 'Professionalism', 'Technical', 'Overall']

    if time_range not in valid_ranges:
        return jsonify({
            'error': {
                'code': 'INVALID_TIME_RANGE',
                'message': f'Time range must be one of: {", ".join(valid_ranges)}'
            }
        }), 400

    if metric not in valid_metrics:
        return jsonify({
            'error': {
                'code': 'INVALID_METRIC',
                'message': f'Metric must be one of: {", ".join(valid_metrics)}'
            }
        }), 400

    try:
        data = AnalyticsService.calculate_trend(user_id, time_range, metric)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'ANALYTICS_ERROR',
                'message': str(e)
            }
        }), 500


@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """
    Get user statistics summary

    Returns:
        200: Summary statistics object
        500: Server error
    """
    user_id = get_jwt_identity()

    try:
        summary = AnalyticsService.get_user_summary(user_id)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'ANALYTICS_ERROR',
                'message': str(e)
            }
        }), 500
