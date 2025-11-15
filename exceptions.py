"""
Custom exception classes for emotion analysis system.

This module defines specific exceptions for different error scenarios,
making error handling more precise and user-friendly.
"""


class EmotionAnalysisError(Exception):
    """Base exception for emotion analysis system."""
    pass


class CameraError(EmotionAnalysisError):
    """Exception raised for camera-related errors."""
    
    def __init__(self, camera_id: int, message: str = "Camera error occurred"):
        self.camera_id = camera_id
        self.message = f"Camera {camera_id}: {message}"
        super().__init__(self.message)


class CameraOpenError(CameraError):
    """Exception raised when camera cannot be opened."""
    
    def __init__(self, camera_id: int, retries: int = 0):
        message = f"Failed to open camera after {retries} attempts"
        super().__init__(camera_id, message)


class CameraReadError(CameraError):
    """Exception raised when frame cannot be read from camera."""
    
    def __init__(self, camera_id: int):
        message = "Failed to read frame from camera"
        super().__init__(camera_id, message)


class ModelLoadError(EmotionAnalysisError):
    """Exception raised when model cannot be loaded."""
    
    def __init__(self, model_path: str, reason: str = ""):
        self.model_path = model_path
        message = f"Failed to load model from {model_path}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class AnalysisError(EmotionAnalysisError):
    """Exception raised when emotion analysis fails."""
    
    def __init__(self, message: str = "Emotion analysis failed"):
        super().__init__(message)


class ConfigurationError(EmotionAnalysisError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class FileNotFoundError(EmotionAnalysisError):
    """Exception raised when required file is not found."""
    
    def __init__(self, file_type: str, file_path: str):
        message = (
            f"{file_type} not found: {file_path}\n"
            f"Please check your .env file and ensure the path is correct."
        )
        super().__init__(message)
