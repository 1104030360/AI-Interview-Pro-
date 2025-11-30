"""
Video Analysis Service

Provides automated video analysis using DeepFace:
- Extract frames from uploaded video
- Analyze emotions, age, gender per frame
- Aggregate results into AnalysisReport
- Calculate performance scores
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from collections import Counter

# Import DeepFace analysis from existing utils
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.analysis import (
    analyze_with_demographics,
    categorize_emotion,
    calculate_emotion_statistics,
    calculate_satisfaction_score
)

from backend.models.analysis_report import AnalysisReport
from backend.models.interview import Interview
from backend.database import db

logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """
    Video analysis service using DeepFace

    Usage:
        service = VideoAnalysisService()
        report = service.analyze_interview(interview_id, video_path)
    """

    # Analysis configuration
    FRAME_SKIP = 30  # Analyze every 30th frame (1 frame per second at 30fps)
    MIN_CONFIDENCE = 0.3  # Minimum confidence score for classification

    @classmethod
    def analyze_interview(
        cls,
        interview_id: str,
        video_path: Path,
        camera: str = 'cam1'
    ) -> Optional[AnalysisReport]:
        """
        Analyze uploaded interview video

        Args:
            interview_id: Interview UUID
            video_path: Path to uploaded video file
            camera: Camera identifier ('cam1' or 'cam2')

        Returns:
            AnalysisReport object or None if analysis fails
        """
        logger.info(f"🎬 Starting video analysis for interview {interview_id}")
        logger.info(f"📹 Video path: {video_path}")
        logger.info(f"📷 Camera: {camera}")

        try:
            # Step 1: Extract and analyze frames
            frame_results = cls._extract_and_analyze_frames(video_path)

            if not frame_results:
                logger.error("❌ No frames analyzed successfully")
                return None

            logger.info(f"✅ Analyzed {len(frame_results)} frames")

            # Step 2: Aggregate results
            aggregated_data = cls._aggregate_results(frame_results)

            # Step 3: Calculate scores
            scores = cls._calculate_scores(aggregated_data)

            # Step 4: Generate suggestions
            suggestions = cls._generate_suggestions(aggregated_data, scores)

            # Step 5: Create or update AnalysisReport
            report = cls._create_or_update_report(
                interview_id,
                scores,
                aggregated_data,
                suggestions
            )

            logger.info(f"✅ Analysis complete for interview {interview_id}")
            logger.info(f"📊 Overall score: {scores['overall_score']:.1f}")

            return report

        except Exception as e:
            logger.error(f"❌ Analysis failed for interview {interview_id}: {e}", exc_info=True)
            # Mark report as failed
            cls._mark_analysis_failed(interview_id, str(e))
            return None

    @classmethod
    def _extract_and_analyze_frames(cls, video_path: Path) -> List[Dict[str, Any]]:
        """
        Extract frames from video and analyze with DeepFace

        Args:
            video_path: Path to video file

        Returns:
            List of analysis results per frame
        """
        results = []

        # Open video
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            logger.error(f"❌ Failed to open video: {video_path}")
            return results

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0

        logger.info(f"📹 Video info: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s")

        frame_count = 0
        analyzed_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Skip frames according to FRAME_SKIP
                if frame_count % cls.FRAME_SKIP != 0:
                    frame_count += 1
                    continue

                # Analyze frame with DeepFace
                timestamp = frame_count / fps if fps > 0 else 0

                try:
                    # Use existing DeepFace analysis function
                    result = analyze_with_demographics(
                        frame,
                        class_name='Candidate',  # Fixed class name
                        confidence_score=1.0     # Video frames have 100% confidence
                    )

                    if result:
                        result['timestamp'] = timestamp
                        result['frame_number'] = frame_count
                        results.append(result)
                        analyzed_count += 1

                        if analyzed_count % 10 == 0:
                            logger.info(f"📊 Analyzed {analyzed_count} frames...")

                except Exception as e:
                    logger.warning(f"⚠️ Frame {frame_count} analysis failed: {e}")

                frame_count += 1

        finally:
            cap.release()

        logger.info(f"✅ Frame extraction complete: {analyzed_count}/{total_frames} frames analyzed")

        return results

    @classmethod
    def _aggregate_results(cls, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate frame analysis results

        Args:
            frame_results: List of per-frame analysis results

        Returns:
            Aggregated statistics and timeline data
        """
        emotions = [r['emotion'] for r in frame_results]
        ages = [r['age'] for r in frame_results]
        genders = [r['gender'] for r in frame_results]

        # Emotion statistics
        emotion_stats = calculate_emotion_statistics(emotions)
        emotion_counts = Counter(emotions)

        # Age statistics
        avg_age = sum(ages) / len(ages) if ages else 0

        # Gender statistics
        gender_counts = Counter(genders)
        dominant_gender = max(gender_counts, key=gender_counts.get) if genders else 'Unknown'

        # Timeline data for frontend charts
        emotion_timeline = [
            {
                'timestamp': r['timestamp'],
                'emotion': r['emotion'],
                'emotionCategory': categorize_emotion(r['emotion'])
            }
            for r in frame_results
        ]

        return {
            'emotion_stats': emotion_stats,
            'emotion_counts': dict(emotion_counts),
            'emotion_timeline': emotion_timeline,
            'avg_age': round(avg_age, 1),
            'dominant_gender': dominant_gender,
            'total_frames_analyzed': len(frame_results)
        }

    @classmethod
    def _calculate_scores(cls, aggregated_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate performance scores based on aggregated data

        Args:
            aggregated_data: Aggregated analysis data

        Returns:
            Dictionary of scores (0-100)
        """
        emotion_stats = aggregated_data['emotion_stats']

        # Confidence score: Based on positive emotions
        confidence_score = (
            emotion_stats['positive_percentage'] * 100
        )

        # Empathy score: Based on neutral + positive emotions (avoiding negative)
        empathy_score = (
            (emotion_stats['positive_percentage'] + emotion_stats['neutral_percentage'] * 0.5) * 100
        )

        # Clarity score: Based on emotion consistency (less variance = better)
        # For now, use positive percentage as proxy
        clarity_score = (
            emotion_stats['positive_percentage'] * 80 +
            emotion_stats['neutral_percentage'] * 60
        )

        # Technical score: Placeholder (would need additional analysis)
        # For now, inverse of negative emotions
        technical_score = (
            (1 - emotion_stats['negative_percentage']) * 100
        )

        # Overall score: Weighted average
        overall_score = (
            confidence_score * 0.3 +
            empathy_score * 0.3 +
            clarity_score * 0.2 +
            technical_score * 0.2
        )

        return {
            'overall_score': round(overall_score, 1),
            'confidence_score': round(confidence_score, 1),
            'empathy_score': round(empathy_score, 1),
            'clarity_score': round(clarity_score, 1),
            'technical_score': round(technical_score, 1)
        }

    @classmethod
    def _generate_suggestions(
        cls,
        aggregated_data: Dict[str, Any],
        scores: Dict[str, float]
    ) -> List[str]:
        """
        Generate improvement suggestions based on analysis

        Args:
            aggregated_data: Aggregated analysis data
            scores: Calculated scores

        Returns:
            List of suggestion strings
        """
        suggestions = []

        emotion_stats = aggregated_data['emotion_stats']

        # Confidence suggestions
        if scores['confidence_score'] < 60:
            suggestions.append(
                "Practice maintaining positive facial expressions throughout the interview."
            )

        # Empathy suggestions
        if emotion_stats['negative_percentage'] > 0.3:
            suggestions.append(
                "Try to reduce negative emotional expressions. Take deep breaths before answering."
            )

        # Clarity suggestions
        if scores['clarity_score'] < 70:
            suggestions.append(
                "Focus on maintaining a calm and composed demeanor to improve clarity."
            )

        # General suggestions
        if emotion_stats['positive_percentage'] < 0.4:
            suggestions.append(
                "Smile more frequently to convey enthusiasm and engagement."
            )

        # If doing well
        if scores['overall_score'] > 80:
            suggestions.append(
                "Great job! Your emotional presentation is professional and engaging."
            )

        return suggestions

    @classmethod
    def _create_or_update_report(
        cls,
        interview_id: str,
        scores: Dict[str, float],
        aggregated_data: Dict[str, Any],
        suggestions: List[str]
    ) -> AnalysisReport:
        """
        Create or update AnalysisReport in database

        Args:
            interview_id: Interview UUID
            scores: Calculated scores
            aggregated_data: Aggregated data
            suggestions: Generated suggestions

        Returns:
            AnalysisReport object
        """
        # Check if report already exists
        report = AnalysisReport.query.filter_by(interview_id=interview_id).first()

        if report:
            # Update existing report
            report.status = 'completed'
            report.overall_score = scores['overall_score']
            report.confidence_score = scores['confidence_score']
            report.empathy_score = scores['empathy_score']
            report.clarity_score = scores['clarity_score']
            report.technical_score = scores['technical_score']
            report.emotion_data = aggregated_data
            report.suggestions = suggestions

            logger.info(f"📝 Updated existing report for interview {interview_id}")
        else:
            # Create new report
            report = AnalysisReport(
                interview_id=interview_id,
                status='completed',
                overall_score=scores['overall_score'],
                confidence_score=scores['confidence_score'],
                empathy_score=scores['empathy_score'],
                clarity_score=scores['clarity_score'],
                technical_score=scores['technical_score'],
                emotion_data=aggregated_data,
                suggestions=suggestions
            )
            db.session.add(report)

            logger.info(f"📝 Created new report for interview {interview_id}")

        db.session.commit()

        return report

    @classmethod
    def _mark_analysis_failed(cls, interview_id: str, error_message: str):
        """
        Mark analysis as failed in database

        Args:
            interview_id: Interview UUID
            error_message: Error description
        """
        try:
            report = AnalysisReport.query.filter_by(interview_id=interview_id).first()

            if report:
                report.status = 'failed'
                report.suggestions = [f"Analysis failed: {error_message}"]
            else:
                report = AnalysisReport(
                    interview_id=interview_id,
                    status='failed',
                    suggestions=[f"Analysis failed: {error_message}"]
                )
                db.session.add(report)

            db.session.commit()
            logger.info(f"📝 Marked analysis as failed for interview {interview_id}")

        except Exception as e:
            logger.error(f"❌ Failed to mark analysis as failed: {e}")
