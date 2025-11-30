"""
Unit tests for StorageService

Tests LocalStorageService functionality:
- File storage and retrieval
- File validation
- File deletion
- File listing
"""
import pytest
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.storage_service import LocalStorageService
from werkzeug.datastructures import FileStorage
from io import BytesIO


@pytest.fixture(scope='module')
def setup_storage():
    """Initialize storage for tests"""
    LocalStorageService.init()
    yield
    # Cleanup after tests
    for file in LocalStorageService.UPLOAD_DIR.glob('test_*'):
        file.unlink(missing_ok=True)


class TestLocalStorageService:
    """Test LocalStorageService methods"""

    def test_init(self):
        """Test storage directory initialization"""
        LocalStorageService.init()
        assert LocalStorageService.UPLOAD_DIR.exists()
        assert LocalStorageService.UPLOAD_DIR.is_dir()

    def test_allowed_file_valid(self):
        """Test allowed file extensions"""
        assert LocalStorageService.allowed_file('video.webm') == True
        assert LocalStorageService.allowed_file('video.mp4') == True
        assert LocalStorageService.allowed_file('video.avi') == True
        assert LocalStorageService.allowed_file('video.mov') == True
        assert LocalStorageService.allowed_file('video.mkv') == True

    def test_allowed_file_invalid(self):
        """Test disallowed file extensions"""
        assert LocalStorageService.allowed_file('video.exe') == False
        assert LocalStorageService.allowed_file('video.txt') == False
        assert LocalStorageService.allowed_file('novideo') == False

    def test_generate_upload_url(self, setup_storage):
        """Test upload URL generation"""
        session_id = 'test-session-123'
        camera = 'cam0'

        info = LocalStorageService.generate_upload_url(session_id, camera)

        assert 'url' in info
        assert 'path' in info
        assert 'filename' in info
        assert session_id in info['filename']
        assert camera in info['filename']
        assert info['url'].startswith('/api/uploads/')

    def test_save_file_success(self, setup_storage):
        """Test successful file save"""
        # Create mock file
        file_content = b'Mock video content for testing'
        file = FileStorage(
            stream=BytesIO(file_content),
            filename='test_video.webm',
            content_type='video/webm'
        )

        session_id = 'test-session-save'
        camera = 'cam0'

        url = LocalStorageService.save_file(file, session_id, camera)

        assert url is not None
        assert '/api/uploads/' in url
        assert session_id in url

        # Verify file exists
        info = LocalStorageService.generate_upload_url(session_id, camera)
        assert Path(info['path']).exists()

        # Cleanup
        LocalStorageService.delete_file(info['filename'])

    def test_save_file_no_file(self, setup_storage):
        """Test save with no file provided"""
        with pytest.raises(ValueError, match='No file provided'):
            LocalStorageService.save_file(None, 'session-id', 'cam0')

    def test_save_file_invalid_extension(self, setup_storage):
        """Test save with invalid file extension"""
        file = FileStorage(
            stream=BytesIO(b'content'),
            filename='test_file.txt',
            content_type='text/plain'
        )

        with pytest.raises(ValueError, match='File type not allowed'):
            LocalStorageService.save_file(file, 'session-id', 'cam0')

    def test_get_file_path_exists(self, setup_storage):
        """Test getting path for existing file"""
        # Create test file
        file = FileStorage(
            stream=BytesIO(b'test content'),
            filename='test.webm'
        )
        session_id = 'test-get-path'
        LocalStorageService.save_file(file, session_id, 'cam0')

        # Get path
        info = LocalStorageService.generate_upload_url(session_id, 'cam0')
        filepath = LocalStorageService.get_file_path(info['filename'])

        assert filepath.exists()
        assert filepath.is_file()

        # Cleanup
        LocalStorageService.delete_file(info['filename'])

    def test_get_file_path_not_found(self, setup_storage):
        """Test getting path for non-existent file"""
        with pytest.raises(FileNotFoundError):
            LocalStorageService.get_file_path('nonexistent_file.webm')

    def test_delete_file_success(self, setup_storage):
        """Test successful file deletion"""
        # Create test file
        file = FileStorage(
            stream=BytesIO(b'test content'),
            filename='test.webm'
        )
        session_id = 'test-delete'
        LocalStorageService.save_file(file, session_id, 'cam0')

        # Delete
        info = LocalStorageService.generate_upload_url(session_id, 'cam0')
        success = LocalStorageService.delete_file(info['filename'])

        assert success == True
        assert not Path(info['path']).exists()

    def test_delete_file_not_found(self, setup_storage):
        """Test deleting non-existent file"""
        success = LocalStorageService.delete_file('nonexistent.webm')
        assert success == False

    def test_list_files(self, setup_storage):
        """Test listing all files"""
        # Create multiple test files
        for i in range(3):
            file = FileStorage(
                stream=BytesIO(f'content {i}'.encode()),
                filename='test.webm'
            )
            LocalStorageService.save_file(file, f'test-list-{i}', 'cam0')

        # List files
        files = LocalStorageService.list_files()

        assert len(files) >= 3
        assert all('filename' in f for f in files)
        assert all('size' in f for f in files)
        assert all('url' in f for f in files)

        # Cleanup
        for i in range(3):
            info = LocalStorageService.generate_upload_url(f'test-list-{i}', 'cam0')
            LocalStorageService.delete_file(info['filename'])

    def test_list_files_filter_by_session(self, setup_storage):
        """Test listing files filtered by session ID"""
        # Create files for specific session
        target_session = 'test-filter-session'
        for i in range(2):
            file = FileStorage(
                stream=BytesIO(f'content {i}'.encode()),
                filename='test.webm'
            )
            LocalStorageService.save_file(file, target_session, f'cam{i}')

        # List files for this session
        files = LocalStorageService.list_files(session_id=target_session)

        assert len(files) == 2
        assert all(target_session in f['filename'] for f in files)

        # Cleanup
        for i in range(2):
            info = LocalStorageService.generate_upload_url(target_session, f'cam{i}')
            LocalStorageService.delete_file(info['filename'])
