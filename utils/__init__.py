"""
工具模組包

提供情緒分析系統所需的各種工具功能。
"""
from .logging_config import setup_logging, get_logger
from .camera import (
    open_camera_with_retry,
    configure_camera,
    read_frame,
    release_camera,
    get_camera_info
)
from .model import load_keras_model, validate_model
from .classification import (
    preprocess_frame,
    classify_frame,
    is_person_detected,
    is_session_end
)
from .analysis import (
    analyze_with_demographics,
    analyze_emotions_only,
    analyze_frame_with_retry,
    categorize_emotion,
    map_emotion_to_score,
    calculate_emotion_statistics,
    calculate_satisfaction_score
)
from .display import (
    put_text_chinese,
    draw_analysis_results,
    resize_and_flip_frame,
    create_split_screen
)
from .video import (
    create_video_writer,
    convert_avi_to_mp4,
    release_video_resources,
    get_video_info
)
from .visualization import (
    generate_emotion_wave_chart,
    generate_emotion_bar_chart,
    generate_combined_wave_chart,
    generate_demographics_title,
    generate_all_charts
)
from .camera_processing import (
    process_camera_frame,
    should_exit
)

__all__ = [
    # Logging
    'setup_logging',
    'get_logger',
    
    # Camera
    'open_camera_with_retry',
    'configure_camera',
    'read_frame',
    'release_camera',
    'get_camera_info',
    
    # Model
    'load_keras_model',
    'validate_model',
    
    # Classification
    'preprocess_frame',
    'classify_frame',
    'is_person_detected',
    'is_session_end',
    
    # Analysis
    'analyze_with_demographics',
    'analyze_emotions_only',
    'analyze_frame_with_retry',
    'categorize_emotion',
    'map_emotion_to_score',
    'calculate_emotion_statistics',
    'calculate_satisfaction_score',
    
    # Display
    'put_text_chinese',
    'draw_analysis_results',
    'resize_and_flip_frame',
    'create_split_screen',
    
    # Video
    'create_video_writer',
    'convert_avi_to_mp4',
    'release_video_resources',
    'get_video_info',
    
    # Visualization
    'generate_emotion_wave_chart',
    'generate_emotion_bar_chart',
    'generate_combined_wave_chart',
    'generate_demographics_title',
    'generate_all_charts',
    
    # Camera Processing
    'process_camera_frame',
    'should_exit',
]
