"""
Storage Service

Provides file storage abstraction for development and production:
- LocalStorageService: File system storage for development
- S3StorageService: (Future) AWS S3 storage for production

Usage:
    from backend.services.storage_service import LocalStorageService

    # Initialize storage
    LocalStorageService.init()

    # Save file
    url = LocalStorageService.save_file(file, session_id, camera)

    # Generate upload path
    path_info = LocalStorageService.generate_upload_url(session_id, camera)
"""
from pathlib import Path
import os
import uuid
from werkzeug.utils import secure_filename


class LocalStorageService:
    """
    Local file system storage service for development environment

    Stores uploaded files in the 'uploads/' directory with organized structure.
    """

    UPLOAD_DIR = Path('uploads')
    ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov', 'mkv'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

    @classmethod
    def init(cls):
        """Initialize storage directory"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        print(f"📁 Storage initialized: {cls.UPLOAD_DIR.absolute()}")

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Check if file extension is allowed

        Args:
            filename: Original filename

        Returns:
            bool: True if extension is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in LocalStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_upload_url(session_id: str, camera: str) -> dict:
        """
        Generate upload path info for a session and camera

        Args:
            session_id: Interview session ID (UUID)
            camera: Camera identifier ('cam0', 'cam1', etc.)

        Returns:
            dict: {
                'url': '/api/uploads/<filename>',
                'path': 'uploads/<filename>',
                'filename': '<filename>'
            }
        """
        # Generate secure filename
        filename = secure_filename(f"{session_id}_{camera}.webm")
        filepath = LocalStorageService.UPLOAD_DIR / filename

        return {
            'url': f'/api/uploads/{filename}',
            'path': str(filepath),
            'filename': filename
        }

    @staticmethod
    def save_file(file, session_id: str, camera: str) -> str:
        """
        Save uploaded file to local storage

        Args:
            file: Werkzeug FileStorage object from request.files
            session_id: Interview session ID
            camera: Camera identifier

        Returns:
            str: Public URL to access the file

        Raises:
            ValueError: If file extension not allowed or file too large
        """
        if not file or not file.filename:
            raise ValueError('No file provided')

        if not LocalStorageService.allowed_file(file.filename):
            raise ValueError(f'File type not allowed. Allowed: {LocalStorageService.ALLOWED_EXTENSIONS}')

        # Generate storage info
        info = LocalStorageService.generate_upload_url(session_id, camera)

        # Save file
        file.save(info['path'])

        # Verify file size
        file_size = os.path.getsize(info['path'])
        if file_size > LocalStorageService.MAX_FILE_SIZE:
            os.remove(info['path'])
            raise ValueError(f'File too large: {file_size} bytes (max: {LocalStorageService.MAX_FILE_SIZE})')

        print(f"✅ File saved: {info['filename']} ({file_size / 1024 / 1024:.2f} MB)")
        return info['url']

    @staticmethod
    def get_file_path(filename: str) -> Path:
        """
        Get absolute file path from filename

        Args:
            filename: Filename to retrieve

        Returns:
            Path: Absolute path to file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = LocalStorageService.UPLOAD_DIR / secure_filename(filename)

        if not filepath.exists():
            raise FileNotFoundError(f'File not found: {filename}')

        return filepath

    @staticmethod
    def delete_file(filename: str) -> bool:
        """
        Delete file from storage

        Args:
            filename: Filename to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            filepath = LocalStorageService.UPLOAD_DIR / secure_filename(filename)
            if filepath.exists():
                filepath.unlink()
                print(f"🗑️  File deleted: {filename}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to delete {filename}: {e}")
            return False

    @staticmethod
    def list_files(session_id: str = None) -> list:
        """
        List all uploaded files, optionally filtered by session

        Args:
            session_id: Optional session ID to filter by

        Returns:
            list: List of file info dicts
        """
        files = []

        for filepath in LocalStorageService.UPLOAD_DIR.glob('*'):
            if filepath.is_file():
                filename = filepath.name

                # Filter by session_id if provided
                if session_id and not filename.startswith(session_id):
                    continue

                file_size = filepath.stat().st_size
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'size_mb': round(file_size / 1024 / 1024, 2),
                    'url': f'/api/uploads/{filename}'
                })

        return files


# TODO: Future implementation for production
class S3StorageService:
    """
    AWS S3 storage service for production environment

    Not implemented yet. Will use boto3 for S3 integration.
    """

    @staticmethod
    def init():
        raise NotImplementedError("S3Storage not implemented yet")

    @staticmethod
    def save_file(file, session_id: str, camera: str) -> str:
        raise NotImplementedError("S3Storage not implemented yet")

    @staticmethod
    def generate_presigned_url(key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for temporary access"""
        raise NotImplementedError("S3Storage not implemented yet")
