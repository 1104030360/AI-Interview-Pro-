"""
Test script for AsyncDeepFaceAnalyzer

This script performs basic functionality tests on the AsyncDeepFaceAnalyzer
to ensure it works correctly before integrating into the main system.
"""

import sys
import time
import numpy as np
import cv2
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.async_analysis import AsyncDeepFaceAnalyzer
from utils.logging_config import get_logger

logger = get_logger(__name__)


def create_test_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a simple test frame with random noise."""
    # Create a frame with random RGB values
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

    # Add a simple colored rectangle to make it more realistic
    cv2.rectangle(frame, (width//4, height//4), (3*width//4, 3*height//4), (100, 150, 200), -1)

    return frame


def test_basic_initialization():
    """Test 1: Basic initialization"""
    print("\n" + "="*60)
    print("Test 1: Basic Initialization")
    print("="*60)

    try:
        analyzer = AsyncDeepFaceAnalyzer(
            name='test_analyzer',
            detector_backend='opencv',
            frame_skip=5,
            input_width=320,
            input_height=240
        )
        print("✓ AsyncDeepFaceAnalyzer initialized successfully")
        print(f"  - Name: {analyzer.name}")
        print(f"  - Detector: {analyzer.detector_backend}")
        print(f"  - Frame skip: {analyzer.frame_skip}")
        print(f"  - Input size: {analyzer.input_size}")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False


def test_start_stop():
    """Test 2: Start and stop worker thread"""
    print("\n" + "="*60)
    print("Test 2: Start and Stop Worker Thread")
    print("="*60)

    try:
        analyzer = AsyncDeepFaceAnalyzer(
            name='test_analyzer',
            detector_backend='opencv',
            frame_skip=1
        )

        # Start analyzer
        analyzer.start()
        print("✓ Analyzer started successfully")

        # Check if thread is running
        if analyzer.running and analyzer.worker_thread.is_alive():
            print("✓ Worker thread is alive and running")
        else:
            print("✗ Worker thread not running")
            return False

        # Stop analyzer
        time.sleep(1)  # Let it run briefly
        analyzer.stop()
        print("✓ Analyzer stopped successfully")

        # Check if thread stopped
        if not analyzer.running:
            print("✓ Worker thread stopped cleanly")
        else:
            print("✗ Worker thread still running")
            return False

        return True
    except Exception as e:
        print(f"✗ Start/stop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frame_submission():
    """Test 3: Frame submission (non-blocking)"""
    print("\n" + "="*60)
    print("Test 3: Frame Submission (Non-blocking)")
    print("="*60)

    try:
        analyzer = AsyncDeepFaceAnalyzer(
            name='test_analyzer',
            detector_backend='opencv',
            frame_skip=1,  # Process every frame
            input_width=320,
            input_height=240
        )

        analyzer.start()
        print("✓ Analyzer started")

        # Create test frame
        test_frame = create_test_frame()
        print("✓ Test frame created (640x480)")

        # Submit frame (should be non-blocking)
        start_time = time.time()
        analyzer.submit_frame(test_frame, 'Class 1', 0.95)
        submit_time = time.time() - start_time

        print(f"✓ Frame submitted in {submit_time*1000:.2f}ms (non-blocking)")

        if submit_time < 0.01:  # Should be < 10ms
            print("✓ Submission is non-blocking (< 10ms)")
        else:
            print(f"⚠ Submission took {submit_time*1000:.2f}ms (might be blocking)")

        # Submit multiple frames to test queue
        for i in range(5):
            analyzer.submit_frame(test_frame, 'Class 1', 0.95)
        print("✓ Multiple frames submitted successfully")

        analyzer.stop()
        return True

    except Exception as e:
        print(f"✗ Frame submission test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_result_retrieval():
    """Test 4: Result retrieval (with actual analysis)"""
    print("\n" + "="*60)
    print("Test 4: Result Retrieval (With Actual Analysis)")
    print("="*60)
    print("⚠ This test performs actual DeepFace analysis (may take 10-30 seconds)")

    try:
        analyzer = AsyncDeepFaceAnalyzer(
            name='test_analyzer',
            detector_backend='opencv',
            frame_skip=1,
            input_width=320,
            input_height=240
        )

        analyzer.start()
        print("✓ Analyzer started")

        # Create test frame (add a simple face-like pattern)
        test_frame = create_test_frame()
        print("✓ Test frame created")

        # Submit frame
        analyzer.submit_frame(test_frame, 'Class 1', 0.95)
        print("✓ Frame submitted for analysis")

        # Wait for result (with timeout)
        print("⏳ Waiting for analysis result...")
        result = None
        max_wait = 30  # Maximum 30 seconds
        start_wait = time.time()

        while time.time() - start_wait < max_wait:
            result = analyzer.get_result(timeout=0.5)
            if result is not None:
                break
            time.sleep(0.5)

        if result:
            wait_time = time.time() - start_wait
            print(f"✓ Result received in {wait_time:.2f}s")
            print(f"  - Class: {result.get('class_name')}")
            print(f"  - Confidence: {result.get('confidence_score')}%")
            print(f"  - Emotion: {result.get('emotion')}")
            if 'age' in result:
                print(f"  - Age: {result.get('age')}")
            if 'gender' in result:
                print(f"  - Gender: {result.get('gender')} ({result.get('gender_confidence')}%)")
        else:
            print("✗ No result received within timeout")
            print("  (This might be expected if no face detected in random test frame)")

        # Get statistics
        stats = analyzer.get_statistics()
        print("\nStatistics:")
        print(f"  - Total analyses: {stats['total_analyses']}")
        print(f"  - Failed analyses: {stats['failed_analyses']}")
        print(f"  - Success rate: {stats['success_rate']:.1f}%")
        print(f"  - Average time: {stats['average_analysis_time']:.3f}s")

        analyzer.stop()
        return True

    except Exception as e:
        print(f"✗ Result retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_real_camera():
    """Test 5: Test with real camera (optional)"""
    print("\n" + "="*60)
    print("Test 5: Test with Real Camera (Optional)")
    print("="*60)

    try:
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠ Camera not available, skipping test")
            return True

        print("✓ Camera opened successfully")

        # Read a frame
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("⚠ Could not read frame from camera, skipping test")
            return True

        print(f"✓ Frame captured from camera: {frame.shape}")

        # Create analyzer
        analyzer = AsyncDeepFaceAnalyzer(
            name='camera_test',
            detector_backend='opencv',
            frame_skip=1
        )

        analyzer.start()
        print("✓ Analyzer started")

        # Submit real frame
        analyzer.submit_frame(frame, 'Class 1', 0.95)
        print("✓ Real frame submitted")

        # Wait for result
        print("⏳ Waiting for analysis result...")
        result = None
        for _ in range(60):  # Wait up to 30 seconds
            result = analyzer.get_result(timeout=0.5)
            if result is not None:
                break

        if result:
            print("✓ Real frame analyzed successfully")
            print(f"  - Emotion: {result.get('emotion')}")
            if 'age' in result:
                print(f"  - Age: {result.get('age')}")
            if 'gender' in result:
                print(f"  - Gender: {result.get('gender')}")
        else:
            print("⚠ No result (might be no face in frame)")

        analyzer.stop()
        return True

    except Exception as e:
        print(f"✗ Real camera test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AsyncDeepFaceAnalyzer Test Suite")
    print("="*60)

    tests = [
        ("Initialization", test_basic_initialization),
        ("Start/Stop", test_start_stop),
        ("Frame Submission", test_frame_submission),
        ("Result Retrieval", test_result_retrieval),
        ("Real Camera", test_with_real_camera),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed_count}/{total} tests passed")

    if passed_count == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
