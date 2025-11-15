"""
Configuration management module for emotion analysis system.

This module handles all configuration settings including:
- File paths (models, fonts, output)
- Camera settings
- Analysis parameters
- Logging configuration

All settings can be overridden using environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PathConfig:
    """File path configuration."""
    
    # Model paths
    MODEL_DIR = Path(os.getenv('MODEL_DIR', './models'))
    KERAS_MODEL_PATH = Path(os.getenv('KERAS_MODEL_PATH', MODEL_DIR / 'keras_model.h5'))
    LABELS_PATH = Path(os.getenv('LABELS_PATH', MODEL_DIR / 'labels.txt'))
    
    # Font paths
    FONT_DIR = Path(os.getenv('FONT_DIR', './fonts'))
    FONT_PATH = Path(os.getenv('FONT_PATH', FONT_DIR / 'NotoSansTC-VariableFont_wght.ttf'))
    
    # Output paths
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './output'))
    LOG_DIR = Path(os.getenv('LOG_DIR', './logs'))
    
    @classmethod
    def validate_paths(cls) -> Dict[str, bool]:
        """
        Validate that all required files exist.
        
        Returns:
            Dict mapping path names to their existence status.
        """
        return {
            'keras_model': cls.KERAS_MODEL_PATH.exists(),
            'labels': cls.LABELS_PATH.exists(),
            'font': cls.FONT_PATH.exists(),
        }
    
    @classmethod
    def get_missing_files(cls) -> list:
        """
        Get list of missing required files.
        
        Returns:
            List of (name, path) tuples for missing files.
        """
        missing = []
        validation = cls.validate_paths()
        
        if not validation['keras_model']:
            missing.append(('Keras Model', cls.KERAS_MODEL_PATH))
        if not validation['labels']:
            missing.append(('Labels File', cls.LABELS_PATH))
        if not validation['font']:
            missing.append(('Font File', cls.FONT_PATH))
        
        return missing
    
    @classmethod
    def ensure_output_dirs(cls):
        """Create output directories if they don't exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)


class CameraConfig:
    """Camera configuration."""
    
    # Camera IDs
    CAMERA_0_ID = int(os.getenv('CAMERA_0_ID', 0))
    CAMERA_1_ID = int(os.getenv('CAMERA_1_ID', 1))
    
    # Camera settings
    TARGET_FPS = 5
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    
    # Display resolution
    DISPLAY_WIDTH = 768
    DISPLAY_HEIGHT = 480


class AnalysisConfig:
    """Emotion analysis configuration."""
    
    # Detection timing (seconds)
    PRESENCE_DETECTION_DELAY_SEC = 3
    """Wait time before starting analysis after person detected."""
    
    ABSENCE_DETECTION_DELAY_SEC = 3
    """Wait time before stopping analysis after person absent."""
    
    LOW_CONFIDENCE_TIMEOUT_SEC = 3
    """Timeout for low confidence detection."""
    
    # Analysis duration (seconds)
    DEMOGRAPHIC_ANALYSIS_DURATION_SEC = 8
    """Duration to analyze demographics (age/gender) before caching."""
    
    # Scoring parameters
    BASELINE_SCORE = 60
    """Baseline sentiment score (neutral)."""
    
    EMOTION_WEIGHT_RANGE = 40
    """Score variation range from baseline."""
    
    # Emotion categorization
    EMOTION_CATEGORIES = {
        'positive': ['happy', 'surprise'],
        'negative': ['angry', 'sad'],
        'neutral': ['neutral', 'disgust', 'fear']
    }
    
    # Emotion weights for scoring
    EMOTION_WEIGHTS = {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }
    
    @classmethod
    def get_emotion_category(cls, emotion: str) -> str:
        """
        Get the category of an emotion.
        
        Args:
            emotion: The emotion name.
            
        Returns:
            Category name ('positive', 'negative', or 'neutral').
        """
        for category, emotions in cls.EMOTION_CATEGORIES.items():
            if emotion in emotions:
                return category
        return 'neutral'  # Default to neutral if unknown
    
    @classmethod
    def calculate_emotion_score(cls, emotions: list) -> float:
        """
        Calculate emotion score from a list of emotions.
        
        Args:
            emotions: List of detected emotions.
            
        Returns:
            Calculated emotion score (0-100).
        """
        if not emotions:
            return cls.BASELINE_SCORE
        
        # Count emotion categories
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for emotion in emotions:
            category = cls.get_emotion_category(emotion)
            counts[category] += 1
        
        total = sum(counts.values())
        if total == 0:
            return cls.BASELINE_SCORE
        
        # Calculate weighted score
        pos_ratio = counts['positive'] / total
        neg_ratio = counts['negative'] / total
        
        score = cls.BASELINE_SCORE + cls.EMOTION_WEIGHT_RANGE * (pos_ratio - neg_ratio)
        
        return round(score, 2)


class LogConfig:
    """Logging configuration."""
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Rotating log settings
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5  # Keep 5 backup files


class Config:
    """Main configuration class combining all configs."""
    
    paths = PathConfig
    camera = CameraConfig
    analysis = AnalysisConfig
    logging = LogConfig
    
    @classmethod
    def validate(cls):
        """
        Validate the entire configuration.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        # Check for missing files
        missing_files = cls.paths.get_missing_files()
        if missing_files:
            error_msg = "Missing required files:\n"
            for name, path in missing_files:
                error_msg += f"  - {name}: {path}\n"
            error_msg += "\nPlease check your .env file and ensure all paths are correct."
            return False, error_msg
        
        # Ensure output directories exist
        try:
            cls.paths.ensure_output_dirs()
        except Exception as e:
            return False, f"Failed to create output directories: {e}"
        
        return True, None


# Convenience exports
__all__ = [
    'Config',
    'PathConfig',
    'CameraConfig',
    'AnalysisConfig',
    'LogConfig',
]
