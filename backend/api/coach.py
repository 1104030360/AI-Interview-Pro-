"""
Coach API

Endpoints for AI coach chat functionality
"""
import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.ai_service import AIService
from backend.utils.ai_exceptions import (
    AIServiceError,
    AIProviderNotConfigured,
    AIAuthError,
    AITimeoutError,
    AIRateLimitError,
    AIConnectionError
)

coach_bp = Blueprint('coach', __name__, url_prefix='/api/coach')


@coach_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """
    Chat with AI coach

    Request:
        {
            "message": "How should I prepare for behavioral interviews?",
            "context": {
                "conversationId": "conv-123",
                "history": [
                    {"role": "user", "content": "previous message"},
                    {"role": "assistant", "content": "previous reply"}
                ]
            }
        }

    Response:
        {
            "conversationId": "conv-123",
            "reply": "AI coach response",
            "suggestions": ["Follow-up question 1", "Follow-up question 2"]
        }
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    message = data['message']
    context = data.get('context', {})

    # Validate message length
    if len(message) > 2000:
        return jsonify({'error': 'Message too long (max 2000 characters)'}), 400

    try:
        # Call AI service using the factory method
        ai_service = AIService.for_user(user_id)
        result = ai_service.chat(message, context)

        return jsonify(result), 200

    except AIProviderNotConfigured as e:
        return jsonify(e.to_dict()), 400
    except AIAuthError as e:
        return jsonify(e.to_dict()), 401
    except AITimeoutError as e:
        return jsonify(e.to_dict()), 504
    except AIRateLimitError as e:
        return jsonify(e.to_dict()), 429
    except AIConnectionError as e:
        return jsonify(e.to_dict()), 503
    except AIServiceError as e:
        return jsonify(e.to_dict()), 500
    except ValueError as e:
        return jsonify({'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'error': {'code': 'INTERNAL_ERROR', 'message': f'Internal server error: {str(e)}'}}), 500


@coach_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """
    Get conversation starter suggestions based on context

    Query Parameters:
        context: Optional context type ('initial', 'technical', 'behavioral')

    Response:
        {
            "suggestions": [
                "How should I answer 'Tell me about yourself'?",
                "What are common behavioral interview questions?",
                "How can I improve my technical interview skills?"
            ]
        }
    """
    context_type = request.args.get('context', 'initial')

    # Context-based dynamic suggestions
    suggestions_map = {
        'initial': [
            "How should I answer 'Tell me about yourself'?",
            "What are common behavioral interview questions?",
            "How can I improve my technical interview skills?",
            "What questions should I ask the interviewer?"
        ],
        'technical': [
            "How do I explain complex technical concepts simply?",
            "What's the best way to approach system design questions?",
            "How should I handle questions I don't know the answer to?",
            "Can you give me tips for live coding interviews?"
        ],
        'behavioral': [
            "How do I use the STAR method effectively?",
            "Tell me about handling conflict questions",
            "How to discuss failures positively?",
            "Tips for leadership and teamwork questions"
        ]
    }

    suggestions = suggestions_map.get(context_type, suggestions_map['initial'])

    return jsonify({'suggestions': suggestions}), 200


@coach_bp.route('/chat/stream', methods=['POST'])
@jwt_required()
def chat_stream():
    """
    Streaming chat with AI coach using Server-Sent Events (SSE)

    Request:
        {
            "message": "How should I prepare for behavioral interviews?",
            "context": {
                "conversationId": "conv-123",
                "history": [...]
            }
        }

    Response: Server-Sent Events stream
        data: {"content": "chunk", "done": false}
        data: {"content": "", "done": true, "full_response": "complete text"}
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    message = data['message']
    context = data.get('context', {})

    # Validate message length
    if len(message) > 2000:
        return jsonify({'error': 'Message too long (max 2000 characters)'}), 400

    def generate():
        """Generator for SSE events."""
        try:
            ai_service = AIService.for_user(user_id)

            for chunk_data in ai_service.chat_stream(message, context):
                yield f"data: {json.dumps(chunk_data)}\n\n"

        except AIProviderNotConfigured as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except AIAuthError as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except AITimeoutError as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except AIRateLimitError as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except AIConnectionError as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except AIServiceError as e:
            error_data = {'error': e.to_dict(), 'done': True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except Exception as e:
            error_data = {
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': f'Internal server error: {str(e)}'
                },
                'done': True
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )
