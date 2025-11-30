"""
Uploads API Blueprint

Provides endpoints for:
- File upload (video recordings)
- File serving (download/stream videos)
- File listing

Uses LocalStorageService for development environment.
Auto-triggers video analysis after upload.
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.storage_service import LocalStorageService
from backend.models.interview import Interview
from backend.database import db
from backend.tasks.analysis_task import start_analysis_task
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

# Initialize storage on first import
LocalStorageService.init()


@uploads_bp.route('/<filename>', methods=['GET'])
def serve_upload(filename):
    """
    Serve uploaded file for download/streaming

    Args:
        filename: Filename to retrieve

    Returns:
        200: File content
        404: File not found
    """
    try:
        filepath = LocalStorageService.get_file_path(filename)
        return send_file(filepath, as_attachment=False)
    except FileNotFoundError:
        return jsonify({
            'error': {
                'code': 'FILE_NOT_FOUND',
                'message': f'File not found: {filename}'
            }
        }), 404


@uploads_bp.route('/', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload interview video recording

    Form Data:
        file: Video file (webm, mp4, etc.)
        sessionId: Interview session ID (UUID)
        camera: Camera identifier ('cam0' or 'cam1')

    Returns:
        200: Upload successful with file URL
        400: Invalid request (no file, invalid format, etc.)
        404: Interview not found
    """
    user_id = get_jwt_identity()

    # Validate request
    if 'file' not in request.files:
        return jsonify({
            'error': {
                'code': 'NO_FILE',
                'message': 'No file provided in request'
            }
        }), 400

    file = request.files['file']
    session_id = request.form.get('sessionId')
    camera = request.form.get('camera', 'cam0')

    if not session_id:
        return jsonify({
            'error': {
                'code': 'NO_SESSION_ID',
                'message': 'sessionId is required'
            }
        }), 400

    # Verify interview exists and belongs to user
    interview = Interview.query.filter_by(id=session_id, user_id=user_id).first()
    if not interview:
        return jsonify({
            'error': {
                'code': 'INTERVIEW_NOT_FOUND',
                'message': 'Interview not found or access denied'
            }
        }), 404

    # Save file
    try:
        url = LocalStorageService.save_file(file, session_id, camera)

        # Update interview record with video URL
        if camera == 'cam0':
            interview.video_url_cam0 = url
        elif camera == 'cam1':
            interview.video_url_cam1 = url

        db.session.commit()

        # Auto-trigger video analysis in background
        try:
            video_path = LocalStorageService.get_file_path(
                f"{session_id}_{camera}.webm"
            )

            logger.info(f"🎬 Triggering analysis for interview {session_id}")
            task = start_analysis_task(session_id, video_path, camera)

            logger.info(f"✅ Analysis task started for interview {session_id}")

            # Use session_id as the task identifier for now
            # In future, this could be a separate task queue ID
            task_id = f"{session_id}_{camera}"

            return jsonify({
                'url': url,
                'camera': camera,
                'sessionId': session_id,
                'taskId': task_id,
                'analysisStatus': 'pending',
                'message': 'Upload successful, analysis started'
            }), 200

        except Exception as analysis_error:
            # Log error but don't fail the upload
            logger.error(
                f"❌ Failed to start analysis for {session_id}: {analysis_error}",
                exc_info=True
            )

            return jsonify({
                'url': url,
                'camera': camera,
                'sessionId': session_id,
                'taskId': f"{session_id}_{camera}",
                'analysisStatus': 'failed',
                'warning': 'Upload successful but analysis failed to start'
            }), 200

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_FILE',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'UPLOAD_FAILED',
                'message': str(e)
            }
        }), 500


@uploads_bp.route('/list', methods=['GET'])
@jwt_required()
def list_uploads():
    """
    List all uploaded files for the current user

    Query Parameters:
        sessionId: Optional - filter by session ID

    Returns:
        200: List of file info objects
    """
    session_id = request.args.get('sessionId')

    try:
        files = LocalStorageService.list_files(session_id=session_id)
        return jsonify({
            'files': files,
            'count': len(files)
        }), 200
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_FAILED',
                'message': str(e)
            }
        }), 500


@uploads_bp.route('/<filename>', methods=['DELETE'])
@jwt_required()
def delete_upload(filename):
    """
    Delete uploaded file

    Args:
        filename: Filename to delete

    Returns:
        200: File deleted
        404: File not found
    """
    user_id = get_jwt_identity()

    # Extract session_id from filename (format: <session_id>_<camera>.webm)
    session_id = filename.split('_')[0]

    # Verify ownership
    interview = Interview.query.filter_by(id=session_id, user_id=user_id).first()
    if not interview:
        return jsonify({
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'You do not have permission to delete this file'
            }
        }), 403

    # Delete file
    success = LocalStorageService.delete_file(filename)

    if success:
        # Update interview record to remove video URL
        if 'cam0' in filename:
            interview.video_url_cam0 = None
        elif 'cam1' in filename:
            interview.video_url_cam1 = None
        db.session.commit()

        return jsonify({
            'message': 'File deleted successfully',
            'filename': filename
        }), 200
    else:
        return jsonify({
            'error': {
                'code': 'FILE_NOT_FOUND',
                'message': 'File not found'
            }
        }), 404
