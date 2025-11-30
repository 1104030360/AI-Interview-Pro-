#!/usr/bin/env python3
"""
Analytics Test Data Seed Script

Creates sample interviews and analysis reports for testing.

Usage:
    # CLI
    FLASK_ENV=development ALLOW_SEED_DATA=true python backend/tests/seed_analytics_data.py

    # With options
    FLASK_ENV=development ALLOW_SEED_DATA=true python backend/tests/seed_analytics_data.py -n 20
    FLASK_ENV=development ALLOW_SEED_DATA=true python backend/tests/seed_analytics_data.py --force
    FLASK_ENV=development ALLOW_SEED_DATA=true python backend/tests/seed_analytics_data.py --clear

WARNING: This script only runs in development/testing environments!
"""
import sys
import os
import random
import uuid
import argparse
from datetime import datetime, timedelta

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


# ============================================================
# Constants
# ============================================================
ALLOWED_ENVIRONMENTS = ['development', 'testing', 'local']
SEED_MARKER_PREFIX = '[SEED]'
DEFAULT_NUM_INTERVIEWS = 15
DEMO_USER_EMAIL = 'demo@example.com'

EMOTIONS = ['happy', 'neutral', 'sad', 'surprised', 'angry', 'fearful', 'disgusted']
POSITIVE_EMOTIONS = ['happy', 'surprised']
NEUTRAL_EMOTIONS = ['neutral']
NEGATIVE_EMOTIONS = ['sad', 'angry', 'fearful', 'disgusted']

JOB_POSITIONS = [
    'Software Engineer',
    'Product Manager',
    'Data Scientist',
    'UX Designer',
    'Marketing Manager',
    'Financial Analyst',
    'HR Specialist',
    'Sales Representative',
    'DevOps Engineer',
    'Business Analyst'
]

AI_SUGGESTIONS = [
    "Try to maintain more consistent eye contact with the camera.",
    "Consider speaking at a slightly slower pace for clarity.",
    "Your answers show good structure - keep using the STAR method.",
    "Remember to highlight quantifiable achievements.",
    "Your enthusiasm comes across well - maintain this energy.",
    "Consider pausing briefly before answering complex questions.",
    "Good use of specific examples to support your points.",
    "Try to reduce filler words like 'um' and 'uh'.",
    "Your body language appears confident and professional.",
    "Consider preparing more concise answers for time management."
]


# ============================================================
# Safety Check Functions
# ============================================================

def check_environment():
    """Ensure script only runs in development/testing environments"""
    env = os.getenv('FLASK_ENV', 'production')
    allow_seed = os.getenv('ALLOW_SEED_DATA', 'false').lower()

    errors = []

    # Check 1: FLASK_ENV
    if env not in ALLOWED_ENVIRONMENTS:
        errors.append(
            f"FLASK_ENV must be one of {ALLOWED_ENVIRONMENTS}, got: '{env}'"
        )

    # Check 2: ALLOW_SEED_DATA flag
    if allow_seed != 'true':
        errors.append(
            "ALLOW_SEED_DATA environment variable must be 'true'"
        )

    if errors:
        print("Environment check failed:")
        for e in errors:
            print(f"   - {e}")
        print("\nTo run seed script:")
        print("  FLASK_ENV=development ALLOW_SEED_DATA=true python backend/tests/seed_analytics_data.py")
        sys.exit(1)

    print(f"Environment check passed (env={env})")


def is_already_seeded(Interview):
    """Check if seed data already exists"""
    seed_interview = Interview.query.filter(
        Interview.title.like(f'{SEED_MARKER_PREFIX}%')
    ).first()
    return seed_interview is not None


def clear_seed_data(db, Interview, AnalysisReport):
    """Clear all seed data"""
    print("Clearing existing seed data...")

    # Find all seed interviews
    seed_interviews = Interview.query.filter(
        Interview.title.like(f'{SEED_MARKER_PREFIX}%')
    ).all()

    for interview in seed_interviews:
        # Delete associated analysis reports
        AnalysisReport.query.filter_by(interview_id=interview.id).delete()
        db.session.delete(interview)

    db.session.commit()
    print(f"   Removed {len(seed_interviews)} seed interviews")


# ============================================================
# Data Generation Functions
# ============================================================

def generate_emotion_data(duration_minutes: int) -> list:
    """Generate emotion timeline data"""
    data_points = []
    interval_seconds = 5
    total_points = (duration_minutes * 60) // interval_seconds

    for i in range(total_points):
        timestamp = i * interval_seconds

        # Random emotion with positive bias
        emotion_weights = [0.35, 0.30, 0.10, 0.10, 0.05, 0.05, 0.05]
        emotion = random.choices(EMOTIONS, weights=emotion_weights)[0]
        confidence = random.uniform(0.6, 0.95)

        if emotion in POSITIVE_EMOTIONS:
            category = 'positive'
        elif emotion in NEUTRAL_EMOTIONS:
            category = 'neutral'
        else:
            category = 'negative'

        data_points.append({
            'timestamp': timestamp,
            'emotion': emotion,
            'confidence': round(confidence, 3),
            'category': category
        })

    return data_points


def generate_analysis_scores() -> dict:
    """Generate analysis scores with realistic variation"""
    base_score = random.randint(60, 90)

    return {
        'overall_score': min(100, max(0, base_score + random.randint(-5, 10))),
        'empathy_score': min(100, max(0, base_score + random.randint(-8, 8))),
        'confidence_score': min(100, max(0, base_score + random.randint(-10, 5))),
        'technical_score': min(100, max(0, base_score + random.randint(-8, 8))),
        'clarity_score': min(100, max(0, base_score + random.randint(-5, 10)))
    }


def generate_ai_feedback() -> dict:
    """Generate AI feedback content"""
    num_suggestions = random.randint(3, 5)
    selected = random.sample(AI_SUGGESTIONS, num_suggestions)

    strengths = [
        "Good eye contact throughout the interview",
        "Clear and articulate speech",
        "Demonstrated relevant experience",
        "Showed enthusiasm for the role",
        "Used specific examples effectively"
    ]

    improvements = [
        "Could provide more quantifiable results",
        "Consider being more concise",
        "Prepare more company-specific examples",
        "Work on reducing nervous habits"
    ]

    return {
        'summary': "Overall performance was good with room for improvement in specific areas.",
        'strengths': random.sample(strengths, random.randint(2, 3)),
        'improvements': random.sample(improvements, random.randint(1, 2)),
        'suggestions': selected
    }


# ============================================================
# Main Seed Function
# ============================================================

def seed_analytics_data(num_interviews: int = DEFAULT_NUM_INTERVIEWS, force: bool = False):
    """
    Main data generation function

    Args:
        num_interviews: Number of interviews to create
        force: If True, clear existing seed data first

    Returns:
        dict: Result status and details
    """
    from backend.app import create_app
    from backend.database import db
    from backend.models.user import User
    from backend.models.interview import Interview
    from backend.models.analysis_report import AnalysisReport
    from backend.services.auth_service import AuthService

    app = create_app()

    with app.app_context():
        # Check if already seeded (idempotent)
        if is_already_seeded(Interview) and not force:
            print("Seed data already exists. Use --force to re-seed.")
            return {'status': 'skipped', 'reason': 'already_seeded'}

        # Clear old data if force mode
        if force and is_already_seeded(Interview):
            clear_seed_data(db, Interview, AnalysisReport)

        print(f"Generating {num_interviews} seed interviews...")

        # Get or create demo user
        demo_user = User.query.filter_by(email=DEMO_USER_EMAIL).first()
        if not demo_user:
            demo_user = AuthService.register_user(
                email=DEMO_USER_EMAIL,
                password='demo123456',
                name='Demo User'
            )
            print(f"   Created demo user: {DEMO_USER_EMAIL}")
        else:
            print(f"   Using existing demo user: {DEMO_USER_EMAIL}")

        # Generate interviews
        created_interviews = []
        base_date = datetime.now() - timedelta(days=30)

        for i in range(num_interviews):
            # Random date within last 30 days
            interview_date = base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(8, 18)
            )

            # Random duration 5-45 minutes
            duration_minutes = random.randint(5, 45)

            # Create Interview
            interview = Interview(
                id=str(uuid.uuid4()),
                user_id=demo_user.id,
                title=f"{SEED_MARKER_PREFIX} Sample Interview #{i+1}",
                job_position=random.choice(JOB_POSITIONS),
                status='completed',
                actual_duration=duration_minutes * 60,
                created_at=interview_date,
                completed_at=interview_date + timedelta(minutes=duration_minutes)
            )
            db.session.add(interview)
            db.session.flush()

            # Generate Analysis Report
            scores = generate_analysis_scores()
            emotion_data = generate_emotion_data(duration_minutes)
            ai_feedback = generate_ai_feedback()

            analysis = AnalysisReport(
                id=str(uuid.uuid4()),
                interview_id=interview.id,
                status='completed',
                overall_score=scores['overall_score'],
                empathy_score=scores['empathy_score'],
                confidence_score=scores['confidence_score'],
                technical_score=scores['technical_score'],
                clarity_score=scores['clarity_score'],
                emotion_data={
                    'emotion_timeline': emotion_data,
                    'dominant_emotion': max(
                        set(e['emotion'] for e in emotion_data),
                        key=lambda x: sum(1 for e in emotion_data if e['emotion'] == x)
                    )
                },
                ai_feedback=ai_feedback,
                created_at=interview_date
            )
            db.session.add(analysis)
            created_interviews.append(interview.id)

            print(f"   [{i+1}/{num_interviews}] Created: {interview.title}")

        db.session.commit()

        print(f"\nSuccessfully seeded {num_interviews} interviews!")
        print(f"   Demo user: {DEMO_USER_EMAIL}")
        print(f"   Password: demo123456")

        return {
            'status': 'success',
            'interviews_created': len(created_interviews),
            'demo_user_email': DEMO_USER_EMAIL,
            'demo_user_id': demo_user.id
        }


# ============================================================
# CLI Entry Point
# ============================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Seed analytics test data for development'
    )
    parser.add_argument(
        '-n', '--num',
        type=int,
        default=DEFAULT_NUM_INTERVIEWS,
        help=f'Number of interviews to generate (default: {DEFAULT_NUM_INTERVIEWS})'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-seed even if data already exists'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Only clear existing seed data without generating new data'
    )

    args = parser.parse_args()

    # Environment check
    check_environment()

    if args.clear:
        from backend.app import create_app
        from backend.database import db
        from backend.models.interview import Interview
        from backend.models.analysis_report import AnalysisReport

        app = create_app()
        with app.app_context():
            if is_already_seeded(Interview):
                clear_seed_data(db, Interview, AnalysisReport)
                print("Seed data cleared!")
            else:
                print("No seed data to clear.")
    else:
        result = seed_analytics_data(
            num_interviews=args.num,
            force=args.force
        )
        print(f"\nResult: {result}")


if __name__ == '__main__':
    main()
