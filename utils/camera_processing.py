"""
Camera processing utilities.

This module provides unified camera frame processing logic,
eliminating code duplication between multiple cameras.
"""

import time
from typing import Dict, Optional
import numpy as np

from models.camera_state import CameraState
from config import AnalysisConfig
from utils.logging_config import get_logger

logger = get_logger(__name__)


def process_camera_frame(
    frame: np.ndarray,
    class_name: str,
    confidence_score: float,
    camera_state: CameraState,
    camera_id: str,
    analyze_with_demographics_func,
    analyze_emotions_only_func
) -> Optional[Dict]:
    """
    Process a single camera frame with unified logic.
    
    This function handles both cameras with the same processing logic,
    eliminating code duplication.
    
    Args:
        frame: Input frame.
        class_name: Classification result.
        confidence_score: Classification confidence.
        camera_state: CameraState instance for this camera.
        camera_id: Camera identifier for logging.
        analyze_with_demographics_func: Function to analyze with demographics.
        analyze_emotions_only_func: Function to analyze emotions only.
        
    Returns:
        Dictionary with analysis results, or None if not analyzing.
    """
    current_time = time.time()
    
    # Check if we should start or stop analysis
    if class_name == 'Class 1':  # Person present
        # Handle low confidence
        if confidence_score < 1.0:
            if camera_state.low_confidence_start_time is None:
                camera_state.low_confidence_start_time = current_time
                logger.debug(f"{camera_id}: Low confidence started")
            elif (current_time - camera_state.low_confidence_start_time) > \
                 AnalysisConfig.LOW_CONFIDENCE_TIMEOUT_SEC:
                logger.warning(
                    f"{camera_id}: Low confidence timeout, stopping analysis"
                )
                return {'stop': True}
        else:
            camera_state.low_confidence_start_time = None
        
        # Start tracking if not already
        if not camera_state.person_detected:
            camera_state.person_detected = True
            camera_state.person_detection_start_time = current_time
            logger.info(f"{camera_id}: Person detected, starting tracking")
        
        camera_state.no_person_detected = False
        
    elif class_name == 'Class 2':  # Person absent
        if not camera_state.no_person_detected:
            camera_state.no_person_detected = True
            camera_state.no_person_detection_start_time = current_time
            logger.info(f"{camera_id}: Person absence detected")
        
        camera_state.person_detected = False
    
    else:
        # Unknown class - reset
        camera_state.person_detected = False
        camera_state.no_person_detected = False
        camera_state.person_detection_start_time = None
        camera_state.no_person_detection_start_time = None
        return None
    
    # Check if we should analyze
    if camera_state.person_detected and \
       camera_state.person_detection_start_time is not None:
        
        elapsed_time = current_time - camera_state.person_detection_start_time
        
        # Wait for presence detection delay
        if elapsed_time > AnalysisConfig.PRESENCE_DETECTION_DELAY_SEC:
            # Determine which analysis function to use
            if camera_state.should_analyze_demographics(
                elapsed_time,
                AnalysisConfig.DEMOGRAPHIC_ANALYSIS_DURATION_SEC
            ):
                # Analyze with demographics
                result = analyze_with_demographics_func(
                    frame, class_name, confidence_score,
                    camera_state, elapsed_time
                )
                
                # Cache demographics if we're at the threshold
                if elapsed_time >= AnalysisConfig.DEMOGRAPHIC_ANALYSIS_DURATION_SEC:
                    camera_state.cache_demographics()
                    logger.debug(f"{camera_id}: Demographics cached")
                
                return result
            else:
                # Use cached demographics, only analyze emotions
                result = analyze_emotions_only_func(
                    frame, class_name, confidence_score,
                    camera_state, elapsed_time
                )
                
                # Add cached demographics to result
                if result:
                    result['age'] = camera_state.result_age
                    result['gender'] = camera_state.result_gender
                    result['gender_confidence'] = camera_state.result_gender_confidence
                
                return result
    
    # Check for absence timeout
    if camera_state.no_person_detected and \
       camera_state.no_person_detection_start_time is not None:
        
        elapsed_time = current_time - camera_state.no_person_detection_start_time
        
        if elapsed_time > AnalysisConfig.ABSENCE_DETECTION_DELAY_SEC:
            logger.info(f"{camera_id}: Absence confirmed, stopping analysis")
            return {'stop': True}
    
    return None


def should_exit(camera_states: Dict[str, CameraState]) -> bool:
    """
    Determine if the program should exit based on camera states.
    
    Args:
        camera_states: Dictionary of camera states.
        
    Returns:
        True if should exit, False otherwise.
    """
    # Exit if any camera detected prolonged absence
    for camera_id, state in camera_states.items():
        if state.no_person_detected and \
           state.no_person_detection_start_time is not None:
            
            elapsed = time.time() - state.no_person_detection_start_time
            
            if elapsed > AnalysisConfig.ABSENCE_DETECTION_DELAY_SEC:
                logger.info(f"Exit triggered by {camera_id}")
                return True
    
    return False
