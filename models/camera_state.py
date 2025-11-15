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
        no_person_detected: Whether no person is currently detected.
        person_detection_start_time: Timestamp when person was first detected.
        no_person_detection_start_time: Timestamp when absence was first detected.
        low_confidence_start_time: Timestamp when low confidence started.
        ages_over_time: List of detected ages over time.
        genders_over_time: List of (gender, confidence) tuples over time.
        emotions_over_time: List of detected emotions over time.
        result_age: Cached age result after initial analysis period.
        result_gender: Cached gender result after initial analysis period.
        result_gender_confidence: Cached gender confidence score.
    """
    
    # Detection state
    person_detected: bool = False
    no_person_detected: bool = False
    
    # Timing
    person_detection_start_time: Optional[float] = None
    no_person_detection_start_time: Optional[float] = None
    low_confidence_start_time: Optional[float] = None
    
    # Analysis results over time
    ages_over_time: List[int] = field(default_factory=list)
    genders_over_time: List[Tuple[str, float]] = field(default_factory=list)
    emotions_over_time: List[str] = field(default_factory=list)
    
    # Cached results (after initial analysis period)
    result_age: Optional[int] = None
    result_gender: Optional[str] = None
    result_gender_confidence: Optional[float] = None
    
    def reset(self):
        """Reset all state to initial values."""
        self.person_detected = False
        self.no_person_detected = False
        self.person_detection_start_time = None
        self.no_person_detection_start_time = None
        self.low_confidence_start_time = None
        self.ages_over_time.clear()
        self.genders_over_time.clear()
        self.emotions_over_time.clear()
        self.result_age = None
        self.result_gender = None
        self.result_gender_confidence = None
    
    def cache_demographics(self):
        """
        Cache the most recent demographic results.
        
        This should be called after the initial analysis period
        to avoid repeated expensive demographic analysis.
        """
        if self.ages_over_time:
            self.result_age = self.ages_over_time[-1]
        
        if self.genders_over_time:
            gender, confidence = self.genders_over_time[-1]
            self.result_gender = gender
            self.result_gender_confidence = confidence
    
    def get_elapsed_time(self, current_time: float) -> Optional[float]:
        """
        Get elapsed time since person detection started.
        
        Args:
            current_time: Current timestamp.
            
        Returns:
            Elapsed time in seconds, or None if not tracking.
        """
        if self.person_detection_start_time is None:
            return None
        return current_time - self.person_detection_start_time
    
    def should_analyze_demographics(self, elapsed_time: float, threshold: float) -> bool:
        """
        Determine if demographics should still be analyzed.
        
        Args:
            elapsed_time: Time elapsed since detection started.
            threshold: Time threshold for demographic analysis.
            
        Returns:
            True if demographics should be analyzed, False if cached results should be used.
        """
        return elapsed_time <= threshold
    
    def get_emotion_summary(self) -> dict:
        """
        Get summary statistics of detected emotions.
        
        Returns:
            Dictionary with emotion counts and percentages.
        """
        if not self.emotions_over_time:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'percentages': {}
            }
        
        from config import AnalysisConfig
        
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for emotion in self.emotions_over_time:
            category = AnalysisConfig.get_emotion_category(emotion)
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
