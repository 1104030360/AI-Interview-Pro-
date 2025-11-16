"""
Camera state data model.

This module defines the CameraState dataclass that encapsulates
all state information for a single camera's emotion analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CameraState:
    """
    Manages state for a single camera's emotion analysis.
    
    This class replaces the previous global variables approach with a
    clean, encapsulated data structure that can be easily extended.
    
    Attributes:
        person_detected: Whether a person is currently detected.
        session_end_detected: Whether session end (Class 2) is detected.
        detection_start_time: Timestamp when person was first detected.
        session_end_start_time: Timestamp when session end was first detected.
        low_confidence_start: Timestamp when low confidence started.
        ages: List of detected ages over time.
        genders: List of (gender, confidence) tuples over time.
        emotions: List of detected emotions over time.
        cached_age: Cached age result after initial analysis period.
        cached_gender: Cached gender result after initial analysis period.
        cached_gender_confidence: Cached gender confidence score.
    """
    
    # Detection state
    person_detected: bool = False
    session_end_detected: bool = False
    
    # Timing
    detection_start_time: Optional[float] = None
    session_end_start_time: Optional[float] = None
    low_confidence_start: Optional[float] = None
    
    # Analysis results over time
    ages: List[int] = field(default_factory=list)
    genders: List[Tuple[str, float]] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    
    # Cached results (after initial analysis period)
    cached_age: Optional[int] = None
    cached_gender: Optional[str] = None
    cached_gender_confidence: Optional[float] = None
    
    def reset(self):
        """Reset all state to initial values."""
        self.person_detected = False
        self.session_end_detected = False
        self.detection_start_time = None
        self.session_end_start_time = None
        self.low_confidence_start = None
        self.ages.clear()
        self.genders.clear()
        self.emotions.clear()
        self.cached_age = None
        self.cached_gender = None
        self.cached_gender_confidence = None
    
    def cache_demographics(self, age=None, gender=None, gender_confidence=None):
        """
        Cache demographic results.
        
        This should be called after analysis to cache the results
        and avoid repeated expensive demographic analysis.
        
        Args:
            age: Age to cache.
            gender: Gender to cache.
            gender_confidence: Gender confidence to cache.
        """
        if age is not None:
            self.cached_age = age
            self.ages.append(age)
        
        if gender is not None and gender_confidence is not None:
            self.cached_gender = gender
            self.cached_gender_confidence = gender_confidence
            self.genders.append((gender, gender_confidence))
    
    def get_elapsed_time(self, current_time: float) -> Optional[float]:
        """
        Get elapsed time since person detection started.
        
        Args:
            current_time: Current timestamp.
            
        Returns:
            Elapsed time in seconds, or None if not tracking.
        """
        if self.detection_start_time is None:
            return None
        return current_time - self.detection_start_time
    
    def should_analyze_demographics(self, current_time: float, threshold: float = 8.0) -> bool:
        """
        Determine if demographics should still be analyzed.
        
        Args:
            current_time: Current timestamp.
            threshold: Time threshold for demographic analysis (default 8 seconds).
            
        Returns:
            True if demographics should be analyzed, False if cached results should be used.
        """
        if self.detection_start_time is None:
            return False
        elapsed = current_time - self.detection_start_time
        return elapsed <= threshold
    
    def get_emotion_summary(self) -> dict:
        """
        Get summary statistics of detected emotions.
        
        Returns:
            Dictionary with emotion counts and percentages.
        """
        if not self.emotions:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'percentages': {}
            }
        
        from utils.analysis import categorize_emotion
        
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for emotion in self.emotions:
            category = categorize_emotion(emotion)
            counts[category] += 1
        
        total = sum(counts.values())
        percentages = {
            cat: round(count / total * 100, 2) if total > 0 else 0
            for cat, count in counts.items()
        }
        
        return {
            'total': total,
            **counts,
            'percentages': percentages
        }
