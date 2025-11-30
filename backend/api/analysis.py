"""
Analysis API Blueprint

Provides endpoints for:
- Retrieving analysis reports
- Exporting analysis reports (JSON/PDF)
- Checking analysis status (pending/processing/completed)
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.interview import Interview
from backend.models.analysis_report import AnalysisReport
from backend.tasks.analysis_task import AnalysisTask
from io import BytesIO
import json
import logging

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@analysis_bp.route('/<interview_id>', methods=['GET'])
@jwt_required()
def get_analysis(interview_id):
    """
    Get analysis report for an interview

    Args:
        interview_id: Interview ID (UUID)

    Returns:
        200: Analysis report data
        404: Interview or analysis not found
        403: Permission denied
    """
    user_id = get_jwt_identity()

    # Verify interview exists and belongs to user
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({
            'error': {
                'code': 'INTERVIEW_NOT_FOUND',
                'message': 'Interview not found or access denied'
            }
        }), 404

    # Get analysis report
    if not interview.analysis:
        return jsonify({
            'error': {
                'code': 'ANALYSIS_NOT_FOUND',
                'message': 'Analysis report not found for this interview'
            }
        }), 404

    # Build response with analysis data
    response = interview.analysis.to_dict()

    # Add video information
    response['videos'] = {
        'cam0': {
            'url': f'/api/uploads/{interview_id}_cam0.webm' if interview.video_url_cam0 else None,
            'available': interview.video_url_cam0 is not None,
            'filename': f'{interview_id}_cam0.webm' if interview.video_url_cam0 else None,
            'mimeType': 'video/webm'
        },
        'cam1': {
            'url': f'/api/uploads/{interview_id}_cam1.webm' if interview.video_url_cam1 else None,
            'available': interview.video_url_cam1 is not None,
            'filename': f'{interview_id}_cam1.webm' if interview.video_url_cam1 else None,
            'mimeType': 'video/webm'
        }
    }

    # Add interview basic info
    response['interview'] = {
        'id': interview.id,
        'title': interview.title,
        'createdAt': interview.created_at.isoformat() if interview.created_at else None,
        'duration': interview.actual_duration,
        'jobPosition': getattr(interview, 'job_position', None)
    }

    return jsonify(response), 200


@analysis_bp.route('/<interview_id>/export', methods=['GET'])
@jwt_required()
def export_report(interview_id):
    """
    Export analysis report as JSON or PDF

    Query Parameters:
        format: 'json' or 'pdf' (default: 'json')

    Args:
        interview_id: Interview ID (UUID)

    Returns:
        200: File download
        404: Interview or analysis not found
        403: Permission denied
        400: Invalid format
    """
    user_id = get_jwt_identity()
    export_format = request.args.get('format', 'json').lower()

    if export_format not in ['json', 'pdf']:
        return jsonify({
            'error': {
                'code': 'INVALID_FORMAT',
                'message': 'Format must be "json" or "pdf"'
            }
        }), 400

    # Verify interview exists and belongs to user
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({
            'error': {
                'code': 'INTERVIEW_NOT_FOUND',
                'message': 'Interview not found or access denied'
            }
        }), 404

    # Get analysis report
    if not interview.analysis:
        return jsonify({
            'error': {
                'code': 'ANALYSIS_NOT_FOUND',
                'message': 'Analysis report not found for this interview'
            }
        }), 404

    # Export as JSON
    if export_format == 'json':
        report_data = {
            'interview': interview.to_dict(),
            'analysis': interview.analysis.to_dict(),
            'exportedAt': interview.analysis.updated_at.isoformat() if interview.analysis.updated_at else None
        }

        # Create in-memory file
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        buffer = BytesIO(json_str.encode('utf-8'))
        buffer.seek(0)

        filename = f"analysis_report_{interview_id[:8]}.json"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )

    # Export as PDF (simple text-based PDF for now)
    elif export_format == 'pdf':
        # TODO: Implement proper PDF generation with ReportLab or WeasyPrint
        # For now, return error
        return jsonify({
            'error': {
                'code': 'PDF_NOT_IMPLEMENTED',
                'message': 'PDF export not yet implemented. Use format=json instead.'
            }
        }), 501


@analysis_bp.route('/<interview_id>/status', methods=['GET'])
@jwt_required()
def get_analysis_status(interview_id):
    """
    Get analysis status and progress

    Args:
        interview_id: Interview ID (UUID)

    Returns:
        200: Status information
        404: Interview not found
        403: Permission denied
    """
    user_id = get_jwt_identity()

    # Verify interview exists and belongs to user
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({
            'error': {
                'code': 'INTERVIEW_NOT_FOUND',
                'message': 'Interview not found or access denied'
            }
        }), 404

    # Check for active background task
    task = AnalysisTask.get_task(interview_id)

    if task:
        # Task is actively running
        task_status = task.get_status()
        logger.info(f"📊 Active task status for {interview_id}: {task_status['status']}")

        return jsonify({
            'status': task_status['status'],
            'progress': task_status['progress'],
            'message': 'Analysis in progress',
            'startedAt': task_status['startedAt'],
            'completedAt': task_status['completedAt']
        }), 200

    # No active task, check database for report
    report = AnalysisReport.query.filter_by(interview_id=interview_id).first()

    if report:
        # Report exists, return its status
        logger.info(f"📊 Report status for {interview_id}: {report.status}")

        return jsonify({
            'status': report.status,
            'progress': 100 if report.status == 'completed' else 0,
            'message': f'Analysis {report.status}',
            'createdAt': report.created_at.isoformat() if report.created_at else None,
            'updatedAt': report.updated_at.isoformat() if report.updated_at else None
        }), 200

    # No task and no report - not started yet
    logger.info(f"📊 No analysis found for {interview_id}")

    return jsonify({
        'status': 'not_started',
        'progress': 0,
        'message': 'Analysis not yet started'
    }), 200


@analysis_bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_export():
    """
    Export multiple analysis reports at once

    Request Body:
        {
            "interviewIds": ["uuid1", "uuid2", ...],
            "format": "json"
        }

    Returns:
        200: ZIP file with multiple reports
        400: Invalid request
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    interview_ids = data.get('interviewIds', [])
    export_format = data.get('format', 'json')

    if not interview_ids:
        return jsonify({
            'error': {
                'code': 'NO_INTERVIEWS',
                'message': 'No interview IDs provided'
            }
        }), 400

    # TODO: Implement batch export with ZIP file
    return jsonify({
        'error': {
            'code': 'BATCH_NOT_IMPLEMENTED',
            'message': 'Batch export not yet implemented'
        }
    }), 501
