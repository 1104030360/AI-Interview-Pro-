"""
Integration tests for Questions API

Tests question bank management endpoints:
- GET /api/questions (list with filters)
- GET /api/questions/<id> (get single)
- POST /api/questions (create)
- PUT /api/questions/<id> (update)
- DELETE /api/questions/<id> (delete)
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.question import Question
from backend.services.auth_service import AuthService
from flask_jwt_extended import create_access_token
import uuid


@pytest.fixture(scope='module')
def app():
    """Create application for testing"""
    from backend.config_backend import Config

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        JWT_SECRET_KEY = 'test-secret-key'

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_token(app):
    """Create authenticated user and return JWT token"""
    with app.app_context():
        # Register user
        user = AuthService.register_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )

        # Create access token
        token = create_access_token(identity=user.id)
        yield token

        # Cleanup
        User.query.filter_by(email='test@example.com').delete()
        db.session.commit()


@pytest.fixture(scope='function')
def sample_questions(app, auth_token):
    """Create sample questions for testing"""
    with app.app_context():
        questions = [
            Question(
                id=str(uuid.uuid4()),
                text='What is REST?',
                type='Technical',
                difficulty='Junior',
                role='Backend',
                tags=['api', 'rest'],
                example_answer='REST is...',
                created_by='system'
            ),
            Question(
                id=str(uuid.uuid4()),
                text='Explain SOLID principles',
                type='Technical',
                difficulty='Mid',
                role='Backend',
                tags=['design', 'solid'],
                example_answer='SOLID stands for...',
                created_by='system'
            ),
            Question(
                id=str(uuid.uuid4()),
                text='Tell me about yourself',
                type='Behavioral',
                difficulty='Junior',
                role='General',
                tags=['intro', 'behavioral'],
                example_answer='I am...',
                created_by='system'
            )
        ]

        for q in questions:
            db.session.add(q)
        db.session.commit()

        question_ids = [q.id for q in questions]
        yield question_ids

        # Cleanup
        for qid in question_ids:
            Question.query.filter_by(id=qid).delete()
        db.session.commit()


class TestQuestionsAPI:
    """Test Questions API endpoints"""

    def test_get_questions_list(self, client, auth_token, sample_questions):
        """Test get questions list"""
        response = client.get(
            '/api/questions',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert 'items' in data
        assert 'pagination' in data
        assert len(data['items']) == 3
        assert data['pagination']['totalItems'] == 3

    def test_get_questions_with_type_filter(self, client, auth_token, sample_questions):
        """Test get questions filtered by type"""
        response = client.get(
            '/api/questions?type=Technical',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data['items']) == 2
        for q in data['items']:
            assert q['type'] == 'Technical'

    def test_get_questions_with_difficulty_filter(self, client, auth_token, sample_questions):
        """Test get questions filtered by difficulty"""
        response = client.get(
            '/api/questions?difficulty=Junior',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data['items']) == 2
        for q in data['items']:
            assert q['difficulty'] == 'Junior'

    def test_get_questions_with_role_filter(self, client, auth_token, sample_questions):
        """Test get questions filtered by role"""
        response = client.get(
            '/api/questions?role=Backend',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data['items']) == 2
        for q in data['items']:
            assert q['role'] == 'Backend'

    def test_get_questions_pagination(self, client, auth_token, sample_questions):
        """Test questions pagination"""
        response = client.get(
            '/api/questions?page=1&limit=2',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert len(data['items']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['limit'] == 2
        assert data['pagination']['totalPages'] == 2

    def test_get_single_question(self, client, auth_token, sample_questions):
        """Test get single question by ID"""
        question_id = sample_questions[0]

        response = client.get(
            f'/api/questions/{question_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['id'] == question_id
        assert 'text' in data
        assert 'type' in data

    def test_get_question_not_found(self, client, auth_token):
        """Test get non-existent question"""
        fake_id = str(uuid.uuid4())

        response = client.get(
            f'/api/questions/{fake_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_create_question(self, client, auth_token):
        """Test create new question"""
        new_question = {
            'text': 'What is GraphQL?',
            'type': 'Technical',
            'difficulty': 'Mid',
            'role': 'Backend',
            'tags': ['graphql', 'api'],
            'exampleAnswer': 'GraphQL is a query language...'
        }

        response = client.post(
            '/api/questions',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=new_question
        )

        assert response.status_code == 201
        data = response.get_json()

        assert data['text'] == new_question['text']
        assert data['type'] == new_question['type']
        assert 'id' in data

        # Cleanup
        Question.query.filter_by(id=data['id']).delete()
        db.session.commit()

    def test_create_question_missing_text(self, client, auth_token):
        """Test create question without text"""
        response = client.post(
            '/api/questions',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_update_question(self, client, auth_token, sample_questions):
        """Test update existing question"""
        question_id = sample_questions[0]

        update_data = {
            'text': 'Updated question text',
            'tags': ['updated', 'tags']
        }

        response = client.put(
            f'/api/questions/{question_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json=update_data
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['text'] == 'Updated question text'
        assert data['tags'] == ['updated', 'tags']

    def test_update_question_not_found(self, client, auth_token):
        """Test update non-existent question"""
        fake_id = str(uuid.uuid4())

        response = client.put(
            f'/api/questions/{fake_id}',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'text': 'Updated'}
        )

        assert response.status_code == 404

    def test_delete_question(self, client, auth_token):
        """Test delete question"""
        # Create question to delete
        with client.application.app_context():
            question = Question(
                id=str(uuid.uuid4()),
                text='Question to delete',
                type='Technical',
                difficulty='Mid',
                role='Backend'
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id

        # Delete question
        response = client.delete(
            f'/api/questions/{question_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

        # Verify deletion
        with client.application.app_context():
            question = Question.query.get(question_id)
            assert question is None

    def test_delete_question_not_found(self, client, auth_token):
        """Test delete non-existent question"""
        fake_id = str(uuid.uuid4())

        response = client.delete(
            f'/api/questions/{fake_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 404

    def test_questions_require_auth(self, client):
        """Test that endpoints require authentication"""
        # GET list
        response = client.get('/api/questions')
        assert response.status_code == 401

        # GET single
        response = client.get(f'/api/questions/{uuid.uuid4()}')
        assert response.status_code == 401

        # POST
        response = client.post('/api/questions', json={})
        assert response.status_code == 401

        # PUT
        response = client.put(f'/api/questions/{uuid.uuid4()}', json={})
        assert response.status_code == 401

        # DELETE
        response = client.delete(f'/api/questions/{uuid.uuid4()}')
        assert response.status_code == 401
