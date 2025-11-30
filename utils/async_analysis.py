"""
Asynchronous DeepFace Analysis Module

This module provides a thread-based asynchronous analyzer for DeepFace emotion analysis.
It uses a Producer-Consumer pattern to avoid blocking the main UI loop.

Phase 5: Key Performance Optimizations:
- Non-blocking frame submission and result retrieval
- Automatic frame skipping
- Image downsampling before analysis
- Fast detector backend (opencv)
- Metal GPU memory growth configuration for macOS
"""

import threading
import queue
import time
import logging
import platform
from typing import Optional, Dict, Any, Tuple
import cv2
import numpy as np
from deepface import DeepFace

logger = logging.getLogger(__name__)


class AsyncDeepFaceAnalyzer:
    """
    Asynchronous DeepFace Analyzer using Producer-Consumer pattern.
    
    This class runs DeepFace analysis in a separate thread to prevent
    blocking the main UI loop, enabling smooth real-time video processing.
    """

    def __init__(
        self,
        name: str = "default",
        detector_backend: str = 'opencv',
        frame_skip: int = 5,
        input_width: int = 320,
        input_height: int = 240,
        analyze_actions: list = None
    ):
        """
        Initialize the AsyncDeepFaceAnalyzer.

        Args:
            name: Identifier for this analyzer (e.g., 'customer', 'server')
            detector_backend: Face detection backend (opencv, ssd, mtcnn, retinaface)
            frame_skip: Number of frames to skip between analyses
            input_width: Target width for analysis (downsampling)
            input_height: Target height for analysis (downsampling)
            analyze_actions: List of actions to analyze (e.g., ['emotion', 'age', 'gender'])
        """
        self.name = name
        self.detector_backend = detector_backend
        self.frame_skip = frame_skip
        self.input_width = input_width
        self.input_height = input_height
        self.analyze_actions = analyze_actions or ['emotion', 'age', 'gender']
        
        # Queue for incoming frames (max size 3 to prevent lag buildup)
        self.frame_queue = queue.Queue(maxsize=3)
        
        # Queue for results (max size 1, we only want the latest)
        self.result_queue = queue.Queue(maxsize=1)
        
        # Control flags
        self.running = False
        self.thread = None
        
        # Latest result cache
        self.latest_result = None
        
        # Frame counter for internal frame skipping
        self.frame_counter = 0
        
        # Statistics tracking
        self.total_analyses = 0
        self.failed_analyses = 0
        self.analysis_times = []
        
        # Configure Metal GPU memory growth for macOS
        self._configure_gpu()
        
        logger.info(f"AsyncDeepFaceAnalyzer '{name}' initialized with backend={detector_backend}, frame_skip={frame_skip}")
    
    @property
    def input_size(self) -> Tuple[int, int]:
        """Compatibility property: return (width, height) tuple."""
        return (self.input_width, self.input_height)
    
    @property
    def worker_thread(self):
        """Compatibility property: alias for self.thread."""
        return self.thread

    def _configure_gpu(self):
        """
        Configure Metal GPU memory growth to prevent memory exhaustion on macOS (M1/M2).
        
        This is CRITICAL for stable multi-threaded GPU usage on Apple Silicon.
        Without this, the system may experience:
        - GPU memory exhaustion
        - Multi-threading conflicts
        - Memory leaks
        """
        if platform.system() == 'Darwin':
            try:
                import tensorflow as tf
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    for gpu in gpus:
                        try:
                            tf.config.experimental.set_memory_growth(gpu, True)
                            logger.info(f"[{self.name}] Metal GPU memory growth enabled for {gpu}")
                        except RuntimeError as e:
                            # Memory growth must be set before GPUs have been initialized
                            logger.warning(f"[{self.name}] Could not set memory growth: {e}")
            except ImportError:
                logger.debug(f"[{self.name}] TensorFlow not found, skipping GPU config")
            except Exception as e:
                logger.warning(f"[{self.name}] GPU memory config failed (non-critical): {e}")

    def start(self):
        """Start the analysis worker thread."""
        if self.running:
            logger.warning(f"[{self.name}] Analyzer already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True, name=f"DeepFace-{self.name}")
        self.thread.start()
        logger.info(f"[{self.name}] AsyncDeepFaceAnalyzer thread started")

    def stop(self, timeout: float = 2.0):
        """
        Stop the analysis worker thread.
        
        Args:
            timeout: Maximum time to wait for thread to finish (seconds)
        """
        if not self.running:
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                logger.warning(f"[{self.name}] Worker thread did not stop within {timeout}s")
            else:
                logger.info(f"[{self.name}] AsyncDeepFaceAnalyzer thread stopped")

    def submit_frame(self, frame: np.ndarray, class_name: str = None, confidence: float = None):
        """
        Submit a frame for analysis. Non-blocking.
        
        Args:
            frame: Image frame to analyze
            class_name: Optional classification result from Keras model
            confidence: Optional confidence score
            
        Note:
            If queue is full, the oldest frame is removed to keep up with real-time processing.
        """
        if not self.running:
            return

        try:
            # Apply frame skipping
            self.frame_counter += 1
            if self.frame_counter % self.frame_skip != 0:
                return  # Skip this frame
            
            # If queue is full, remove oldest frame to keep latest data
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            
            # Add frame with metadata
            frame_data = {
                'frame': frame,
                'class_name': class_name,
                'confidence': confidence,
                'timestamp': time.time()
            }
            self.frame_queue.put_nowait(frame_data)
            
        except queue.Full:
            pass  # Should not happen due to logic above

    def get_result(self, timeout: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Get the latest analysis result. Non-blocking by default.
        
        Args:
            timeout: Maximum time to wait for a result (0.0 = non-blocking)
            
        Returns:
            Dictionary with analysis results or None if no result available
        """
        # Check if there is a new result in the queue
        try:
            if timeout > 0:
                self.latest_result = self.result_queue.get(timeout=timeout)
            else:
                # Non-blocking: drain all results and get the latest
                while not self.result_queue.empty():
                    self.latest_result = self.result_queue.get_nowait()
        except queue.Empty:
            pass
            
        return self.latest_result

    def _worker_loop(self):
        """Main loop for the worker thread."""
        logger.info(f"[{self.name}] Async analysis worker loop started")
        
        while self.running:
            try:
                # Wait for frame with timeout to allow checking self.running
                try:
                    frame_data = self.frame_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Extract frame
                frame = frame_data['frame']
                
                # Process frame with timing
                analysis_start = time.time()
                result = self._analyze(frame)
                analysis_time = time.time() - analysis_start
                
                # Update statistics
                self.total_analyses += 1
                self.analysis_times.append(analysis_time)
                if result is None:
                    self.failed_analyses += 1
                
                # Add metadata to result
                if result:
                    result['analyzer_name'] = self.name
                    result['analysis_timestamp'] = time.time()
                    
                    # Put result (replace old result if exists)
                    while not self.result_queue.empty():
                        try:
                            self.result_queue.get_nowait()
                        except queue.Empty:
                            break
                    
                    try:
                        self.result_queue.put_nowait(result)
                    except queue.Full:
                        pass  # Should not happen
                    
            except Exception as e:
                logger.error(f"[{self.name}] Error in async analysis loop: {e}", exc_info=True)
                time.sleep(0.1)  # Prevent tight loop on error

    def _analyze(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Perform the actual DeepFace analysis.
        
        Args:
            frame: Image frame to analyze
            
        Returns:
            Dictionary with analysis results or None if analysis failed
        """
        try:
            # Downsample for performance (40-50% faster)
            if self.input_width and self.input_height:
                small_frame = cv2.resize(frame, (self.input_width, self.input_height))
            else:
                small_frame = frame

            # DeepFace analysis
            # enforce_detection=False to avoid errors when face not detected
            # silent=True to suppress DeepFace logging
            objs = DeepFace.analyze(
                img_path=small_frame,
                actions=self.analyze_actions,
                detector_backend=self.detector_backend,
                enforce_detection=False,
                silent=True
            )
            
            if objs and len(objs) > 0:
                # Return the first face found (assuming single person per camera)
                analysis = objs[0]
                
                # Extract dominant emotion
                if 'emotion' in analysis:
                    emotions = analysis['emotion']
                    dominant_emotion = max(emotions, key=emotions.get)
                    analysis['dominant_emotion'] = dominant_emotion
                
                return analysis
            return None
            
        except Exception as e:
            # DeepFace might raise error if no face found even with enforce_detection=False
            # or other internal errors. We log at debug level to avoid spam.
            logger.debug(f"[{self.name}] DeepFace analysis failed: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get analysis statistics.
        
        Returns:
            Dictionary containing:
            - total_analyses: Total number of analyses performed
            - failed_analyses: Number of failed analyses
            - success_rate: Success rate as a percentage
            - average_analysis_time: Average time per analysis in seconds
        """
        success_count = self.total_analyses - self.failed_analyses
        success_rate = (success_count / self.total_analyses * 100) if self.total_analyses > 0 else 0.0
        avg_time = sum(self.analysis_times) / len(self.analysis_times) if self.analysis_times else 0.0
        
        return {
            'total_analyses': self.total_analyses,
            'failed_analyses': self.failed_analyses,
            'success_rate': success_rate,
            'average_analysis_time': avg_time
        }


# Convenience function for backward compatibility
def create_async_analyzer(name: str, **kwargs) -> AsyncDeepFaceAnalyzer:
    """
    Create and return an AsyncDeepFaceAnalyzer instance.
    
    Args:
        name: Identifier for the analyzer
        **kwargs: Additional arguments to pass to AsyncDeepFaceAnalyzer
        
    Returns:
        AsyncDeepFaceAnalyzer instance
    """
    return AsyncDeepFaceAnalyzer(name=name, **kwargs)
