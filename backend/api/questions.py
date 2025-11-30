"""
Questions API

Endpoints for question bank management
"""
import csv
import io
import json
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.question import Question
from backend.services.ai_service import AIService
from backend.database import db

# Max file size for import: 5MB
MAX_IMPORT_FILE_SIZE = 5 * 1024 * 1024

questions_bp = Blueprint('questions', __name__, url_prefix='/api/questions')


@questions_bp.route('', methods=['GET'])
@jwt_required()
def get_questions():
    """
    Get question bank list with filters

    Query params:
        - type: Behavioral, Technical, System Design
        - difficulty: Junior, Mid, Senior
        - role: Frontend, Backend, PM, Data Science
        - page: Page number (default 1)
        - limit: Items per page (default 20)

    Response:
        {
            "items": [{...}],
            "pagination": {
                "totalItems": 100,
                "page": 1,
                "limit": 20,
                "totalPages": 5
            }
        }
    """
    # Get filter parameters
    q_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    role = request.args.get('role')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    # Build query
    query = Question.query

    if q_type:
        query = query.filter_by(type=q_type)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if role:
        query = query.filter_by(role=role)

    # Get total count
    total = query.count()

    # Paginate
    questions = query.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'items': [q.to_dict() for q in questions],
        'pagination': {
            'totalItems': total,
            'page': page,
            'limit': limit,
            'totalPages': (total + limit - 1) // limit
        }
    }), 200


@questions_bp.route('/<question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """
    Get single question by ID

    Response:
        {
            "id": "...",
            "text": "...",
            "type": "Technical",
            "difficulty": "Mid",
            "role": "Backend",
            "tags": ["python", "api"],
            "exampleAnswer": "..."
        }
    """
    question = Question.query.get(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    return jsonify(question.to_dict()), 200


@questions_bp.route('', methods=['POST'])
@jwt_required()
def create_question():
    """
    Create new question (manual entry)

    Request:
        {
            "text": "Explain the difference between REST and GraphQL",
            "type": "Technical",
            "difficulty": "Mid",
            "role": "Backend",
            "tags": ["api", "rest", "graphql"],
            "exampleAnswer": "REST uses multiple endpoints..."
        }

    Response:
        {
            "id": "...",
            "text": "...",
            ...
        }
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    if not data or 'text' not in data:
        return jsonify({'error': 'Question text is required'}), 400

    # Create question
    question = Question(
        id=str(uuid.uuid4()),
        text=data['text'],
        type=data.get('type', 'Technical'),
        difficulty=data.get('difficulty', 'Mid'),
        role=data.get('role', 'Software Engineer'),
        tags=data.get('tags', []),
        example_answer=data.get('exampleAnswer', ''),
        created_by=user_id
    )

    db.session.add(question)
    db.session.commit()

    return jsonify(question.to_dict()), 201


@questions_bp.route('/<question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    """
    Update existing question

    Request:
        {
            "text": "Updated question text",
            "tags": ["updated", "tags"]
        }

    Response:
        {
            "id": "...",
            "text": "...",
            ...
        }
    """
    question = Question.query.get(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    data = request.get_json()

    # Update fields
    if 'text' in data:
        question.text = data['text']
    if 'type' in data:
        question.type = data['type']
    if 'difficulty' in data:
        question.difficulty = data['difficulty']
    if 'role' in data:
        question.role = data['role']
    if 'tags' in data:
        question.tags = data['tags']
    if 'exampleAnswer' in data:
        question.example_answer = data['exampleAnswer']

    db.session.commit()

    return jsonify(question.to_dict()), 200


@questions_bp.route('/<question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    """
    Delete question

    Response:
        {
            "message": "Question deleted successfully"
        }
    """
    question = Question.query.get(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    db.session.delete(question)
    db.session.commit()

    return jsonify({'message': 'Question deleted successfully'}), 200


@questions_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_questions():
    """
    Generate questions using AI

    Request:
        {
            "role": "Backend",
            "difficulty": "Mid",
            "type": "Technical",
            "count": 5
        }

    Response:
        {
            "questions": [
                {
                    "text": "...",
                    "tags": ["python", "api"],
                    "exampleAnswer": "..."
                }
            ]
        }
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    criteria = {
        'role': data.get('role', 'Software Engineer'),
        'difficulty': data.get('difficulty', 'Mid'),
        'type': data.get('type', 'Technical'),
        'count': data.get('count', 5)
    }

    # Validate count
    if criteria['count'] < 1 or criteria['count'] > 20:
        return jsonify({'error': 'Count must be between 1 and 20'}), 400

    try:
        # Generate questions using AI
        questions = AIService.generate_questions(user_id, criteria)

        return jsonify({'questions': questions}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@questions_bp.route('/import', methods=['POST'])
@jwt_required()
def import_questions():
    """
    Batch import questions from CSV or JSON

    Supports:
        - CSV file upload (multipart/form-data)
        - JSON file upload (multipart/form-data)
        - JSON body (application/json)

    CSV columns:
        text, type, difficulty, role, tags, exampleAnswer
        (tags should be semicolon-separated)

    JSON format:
        {
            "questions": [
                {
                    "text": "Question text",
                    "type": "Technical",
                    "difficulty": "Mid",
                    "role": "Backend",
                    "tags": ["python", "api"],
                    "exampleAnswer": "..."
                }
            ]
        }

    Response:
        {
            "success": true,
            "imported": 5,
            "skipped": 2,
            "errors": [
                {"index": 3, "error": "Missing question text"}
            ]
        }
    """
    user_id = get_jwt_identity()
    questions_data = []

    # Check for file upload
    if 'file' in request.files:
        file = request.files['file']

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > MAX_IMPORT_FILE_SIZE:
            return jsonify({
                'error': {
                    'code': 'FILE_TOO_LARGE',
                    'message': f'File size exceeds limit ({MAX_IMPORT_FILE_SIZE // (1024*1024)}MB)'
                }
            }), 400

        filename = file.filename.lower() if file.filename else ''

        if filename.endswith('.csv'):
            questions_data = _parse_csv(file)
        elif filename.endswith('.json'):
            questions_data = _parse_json_file(file)
        else:
            return jsonify({
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': 'Supported formats: CSV, JSON'
                }
            }), 400

    # Check for JSON body
    elif request.is_json:
        data = request.get_json()
        questions_data = data.get('questions', [])

    else:
        return jsonify({
            'error': {
                'code': 'NO_DATA',
                'message': 'No file or JSON data provided'
            }
        }), 400

    # Validate and save
    results = _validate_and_save(user_id, questions_data)

    return jsonify({
        'success': True,
        'imported': results['imported'],
        'skipped': results['skipped'],
        'errors': results['errors']
    }), 200


@questions_bp.route('/export', methods=['GET'])
@jwt_required()
def export_questions():
    """
    Export questions as JSON

    Query params:
        - type: Filter by question type
        - difficulty: Filter by difficulty
        - role: Filter by role
        - format: 'json' (default) or 'csv'

    Response:
        JSON array of questions or CSV file download
    """
    # Get filter parameters
    q_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    role = request.args.get('role')
    export_format = request.args.get('format', 'json')

    # Build query
    query = Question.query

    if q_type:
        query = query.filter_by(type=q_type)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if role:
        query = query.filter_by(role=role)

    questions = query.all()

    if export_format == 'csv':
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['text', 'type', 'difficulty', 'role', 'tags', 'exampleAnswer'])

        # Data
        for q in questions:
            tags_str = ';'.join(q.tags) if q.tags else ''
            writer.writerow([
                q.text,
                q.type,
                q.difficulty,
                q.role,
                tags_str,
                q.example_answer or ''
            ])

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=questions_export.csv'
            }
        )

    # Default: JSON
    return jsonify({
        'questions': [q.to_dict() for q in questions]
    }), 200


def _parse_csv(file) -> list:
    """Parse CSV file to question list."""
    questions = []

    try:
        # Try UTF-8 first, then UTF-8-BOM, then latin-1
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
            try:
                file.seek(0)
                content = file.read().decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            return []

        stream = io.StringIO(content)
        reader = csv.DictReader(stream)

        for row in reader:
            # Support both 'text' and 'question' column names
            text = row.get('text') or row.get('question', '')

            # Parse tags (semicolon or comma separated)
            tags_str = row.get('tags', '')
            if tags_str:
                if ';' in tags_str:
                    tags = [t.strip() for t in tags_str.split(';') if t.strip()]
                else:
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            else:
                tags = []

            questions.append({
                'text': text,
                'type': row.get('type', 'Technical'),
                'difficulty': row.get('difficulty', 'Mid'),
                'role': row.get('role') or row.get('position', 'Software Engineer'),
                'tags': tags,
                'exampleAnswer': row.get('exampleAnswer') or row.get('example_answer', '')
            })

    except Exception as e:
        # Return empty list on parse error
        pass

    return questions


def _parse_json_file(file) -> list:
    """Parse JSON file to question list."""
    try:
        data = json.load(file)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'questions' in data:
            return data['questions']

    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    return []


def _validate_and_save(user_id: str, questions: list) -> dict:
    """Validate and save imported questions."""
    results = {
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    for i, q in enumerate(questions):
        # Validate required field
        text = q.get('text', '').strip()
        if not text:
            results['errors'].append({
                'index': i,
                'error': 'Missing question text'
            })
            results['skipped'] += 1
            continue

        # Check for duplicate
        existing = Question.query.filter_by(
            text=text
        ).first()

        if existing:
            results['errors'].append({
                'index': i,
                'error': 'Duplicate question'
            })
            results['skipped'] += 1
            continue

        # Create question
        try:
            question = Question(
                id=str(uuid.uuid4()),
                text=text,
                type=q.get('type', 'Technical'),
                difficulty=q.get('difficulty', 'Mid'),
                role=q.get('role', 'Software Engineer'),
                tags=q.get('tags', []),
                example_answer=q.get('exampleAnswer', ''),
                created_by=user_id
            )
            db.session.add(question)
            results['imported'] += 1

        except Exception as e:
            results['errors'].append({
                'index': i,
                'error': str(e)
            })
            results['skipped'] += 1

    # Commit all at once
    if results['imported'] > 0:
        db.session.commit()

    return results
