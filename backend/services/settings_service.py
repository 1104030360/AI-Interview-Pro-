"""
Settings Service

Business logic for managing user settings
"""
from backend.database import db
from backend.models.user_settings import UserSettings
from backend.utils.crypto import encrypt_api_key


class SettingsService:
    """Handle user settings operations"""

    @staticmethod
    def get_user_settings(user_id: str) -> dict:
        """
        Get user settings, return as dict

        Args:
            user_id: User UUID string

        Returns:
            dict: Settings in frontend format (profile, ai, prompts)

        Raises:
            ValueError: If user not found
        """
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        if not settings:
            # Create default settings if not exist
            settings = SettingsService._create_default_settings(user_id)

        return settings.to_dict()

    @staticmethod
    def _create_default_settings(user_id: str) -> UserSettings:
        """
        Create default settings for new user

        Args:
            user_id: User UUID string

        Returns:
            UserSettings: Created settings object
        """
        settings = UserSettings(
            user_id=user_id,
            ai_provider='ollama',
            ai_model='llama3:latest',
            language='en'
        )

        db.session.add(settings)
        db.session.commit()

        return settings

    @staticmethod
    def update_user_settings(user_id: str, data: dict) -> dict:
        """
        Update user settings

        Args:
            user_id: User UUID string
            data: Update data (profile, ai, prompts)

        Returns:
            dict: Updated settings

        Raises:
            ValueError: If validation fails
        """
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        if not settings:
            settings = SettingsService._create_default_settings(user_id)

        # Update profile
        if 'profile' in data:
            profile = data['profile']
            if 'name' in profile:
                settings.display_name = profile['name']
            if 'role' in profile:
                settings.job_role = profile['role']
            if 'language' in profile:
                settings.language = profile['language']
            if 'avatarUrl' in profile:
                settings.avatar_url = profile['avatarUrl']

        # Update AI config
        if 'ai' in data:
            ai = data['ai']
            if 'provider' in ai:
                if ai['provider'] not in ['openai', 'ollama', 'claude', 'gemini']:
                    raise ValueError(f"Unsupported AI provider: {ai['provider']}")
                settings.ai_provider = ai['provider']
            if 'apiKey' in ai:
                # Encrypt API key before storing
                if ai['apiKey']:
                    settings.ai_api_key_encrypted = encrypt_api_key(ai['apiKey'])
                else:
                    settings.ai_api_key_encrypted = ''
            if 'model' in ai:
                settings.ai_model = ai['model']

        # Update prompts
        if 'prompts' in data:
            prompts = data['prompts']
            if 'global' in prompts:
                settings.prompt_global = prompts['global']
            if 'interviewSuggestions' in prompts:
                settings.prompt_interview = prompts['interviewSuggestions']
            if 'coachChat' in prompts:
                settings.prompt_coach = prompts['coachChat']

        db.session.commit()

        return settings.to_dict()
