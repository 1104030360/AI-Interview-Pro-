"""Tests for CameraState class."""

import pytest
from models.camera_state import CameraState


def test_camera_state_initialization():
    """Test that CameraState initializes with correct default values."""
    state = CameraState()
    
    assert state.person_detected == False
    assert state.no_person_detected == False
    assert state.person_detection_start_time is None
    assert state.no_person_detection_start_time is None
    assert state.low_confidence_start_time is None
    assert state.ages_over_time == []
    assert state.genders_over_time == []
    assert state.emotions_over_time == []
    assert state.result_age is None
    assert state.result_gender is None
    assert state.result_gender_confidence is None


def test_camera_state_reset():
    """Test that reset() clears all state."""
    state = CameraState()
    
    # Set some values
    state.person_detected = True
    state.person_detection_start_time = 123.45
    state.ages_over_time.append(25)
    state.emotions_over_time.append('happy')
    state.result_age = 25
    
    # Reset
    state.reset()
    
    # Verify all cleared
    assert state.person_detected == False
    assert state.person_detection_start_time is None
    assert state.ages_over_time == []
    assert state.emotions_over_time == []
    assert state.result_age is None


def test_cache_demographics():
    """Test that cache_demographics() saves the latest results."""
    state = CameraState()
    
    # Add some data
    state.ages_over_time = [20, 25, 30]
    state.genders_over_time = [
        ('Man', 0.8),
        ('Man', 0.85),
        ('Man', 0.9)
    ]
    
    # Cache
    state.cache_demographics()
    
    # Verify cached values
    assert state.result_age == 30  # Last age
    assert state.result_gender == 'Man'
    assert state.result_gender_confidence == 0.9


def test_get_elapsed_time():
    """Test elapsed time calculation."""
    state = CameraState()
    
    # No start time
    assert state.get_elapsed_time(100.0) is None
    
    # With start time
    state.person_detection_start_time = 100.0
    assert state.get_elapsed_time(105.0) == 5.0
    assert state.get_elapsed_time(110.5) == 10.5


def test_should_analyze_demographics():
    """Test demographic analysis decision."""
    state = CameraState()
    
    # Should analyze if within threshold
    assert state.should_analyze_demographics(5.0, 8.0) == True
    assert state.should_analyze_demographics(8.0, 8.0) == True
    
    # Should not analyze if beyond threshold
    assert state.should_analyze_demographics(9.0, 8.0) == False
    assert state.should_analyze_demographics(10.0, 8.0) == False


def test_get_emotion_summary():
    """Test emotion summary calculation."""
    state = CameraState()
    
    # Empty emotions
    summary = state.get_emotion_summary()
    assert summary['total'] == 0
    assert summary['positive'] == 0
    assert summary['negative'] == 0
    assert summary['neutral'] == 0
    
    # With emotions
    state.emotions_over_time = [
        'happy', 'happy', 'happy',  # 3 positive
        'sad', 'angry',  # 2 negative
        'neutral'  # 1 neutral
    ]
    
    summary = state.get_emotion_summary()
    assert summary['total'] == 6
    assert summary['positive'] == 3
    assert summary['negative'] == 2
    assert summary['neutral'] == 1
    assert summary['percentages']['positive'] == 50.0
    assert summary['percentages']['negative'] == pytest.approx(33.33, 0.01)
    assert summary['percentages']['neutral'] == pytest.approx(16.67, 0.01)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
