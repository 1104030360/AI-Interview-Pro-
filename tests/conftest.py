"""Test configuration for pytest."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


@pytest.fixture
def mock_model():
    """Mock Keras model for testing."""
    class MockModel:
        def predict(self, x, verbose=0):
            import numpy as np
            return np.array([[0.1, 0.9]])  # Mock prediction
    
    return MockModel()


@pytest.fixture
def mock_class_names():
    """Mock class names."""
    return ['Class 1', 'Class 2']


@pytest.fixture
def sample_frame():
    """Sample frame for testing."""
    import numpy as np
    return np.zeros((240, 320, 3), dtype=np.uint8)
