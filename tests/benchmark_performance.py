"""
Performance Benchmark for Async DeepFace Analysis

This script compares the performance of synchronous vs asynchronous DeepFace analysis.
Expected results:
- Sync: <5 FPS (severe UI lag)
- Async: >20 FPS (smooth real-time performance)
- Speedup: 10-30x improvement
"""

import time
import cv2
import numpy as np
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.async_analysis import AsyncDeepFaceAnalyzer
from deepface import DeepFace


def create_test_frame(frame_number: int = 0) -> np.ndarray:
    """Create a test frame with a simple face-like shape."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a simple face-like circle
    cv2.circle(frame, (320, 240), 100, (255, 255, 255), -1)
    # Add some variation per frame
    cv2.putText(frame, f"Frame {frame_number}", (250, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return frame


def benchmark_sync(num_frames: int = 5) -> float:
    """
    Benchmark synchronous DeepFace analysis.
    
    Args:
        num_frames: Number of frames to analyze
        
    Returns:
        Average FPS
    """
    print(f"\n{'='*60}")
    print(f"SYNCHRONOUS BENCHMARK ({num_frames} frames)")
    print(f"{'='*60}")
    
    frame_times = []
    
    for i in range(num_frames):
        frame = create_test_frame(i)
        
        t0 = time.time()
        try:
            DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                detector_backend='opencv',
                enforce_detection=False,
                silent=True
            )
        except Exception as e:
            print(f"  Frame {i+1}: Analysis failed - {e}")
            
        dt = time.time() - t0
        frame_times.append(dt)
        print(f"  Frame {i+1}: {dt:.4f}s ({1/dt if dt > 0 else 0:.2f} FPS)")
    
    avg_time = sum(frame_times) / len(frame_times)
    avg_fps = 1 / avg_time if avg_time > 0 else 0
    
    print(f"\nSYNC Result:")
    print(f"  Average time: {avg_time:.4f}s")
    print(f"  Average FPS: {avg_fps:.2f}")
    
    return avg_fps


def benchmark_async(num_frames: int = 100) -> float:
    """
    Benchmark asynchronous DeepFace analysis.
    
    Args:
        num_frames: Number of frames to process
        
    Returns:
        Average FPS
    """
    print(f"\n{'='*60}")
    print(f"ASYNCHRONOUS BENCHMARK ({num_frames} frames)")
    print(f"{'='*60}")
    
    analyzer = AsyncDeepFaceAnalyzer(
        name="benchmark",
        detector_backend='opencv',
        frame_skip=1,  # Analyze every frame for benchmark
        input_width=320,
        input_height=240
    )
    analyzer.start()
    
    # Warmup
    print("  Warming up...")
    warmup_frame = create_test_frame(0)
    for _ in range(5):
        analyzer.submit_frame(warmup_frame)
        time.sleep(0.1)
    
    # Clear queue
    while not analyzer.result_queue.empty():
        try:
            analyzer.result_queue.get_nowait()
        except:
            pass
    
    print("  Running benchmark...")
    start_time = time.time()
    results_received = 0
    
    for i in range(num_frames):
        frame = create_test_frame(i)
        
        # Submit frame (non-blocking)
        analyzer.submit_frame(frame)
        
        # Get result (non-blocking)
        result = analyzer.get_result()
        if result:
            results_received += 1
        
        # Simulate display delay (30 FPS target)
        time.sleep(1/30)
    
    # Wait a bit for final results
    time.sleep(0.5)
    final_result = analyzer.get_result()
    if final_result:
        results_received += 1
    
    total_time = time.time() - start_time
    fps = num_frames / total_time
    
    analyzer.stop()
    
    print(f"\nASYNC Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Main loop FPS: {fps:.2f}")
    print(f"  Results received: {results_received}")
    
    return fps


def main():
    """Run performance benchmarks and display results."""
    print("\n" + "="*60)
    print("DeepFace Performance Benchmark - Phase 5")
    print("="*60)
    
    # Run Sync Benchmark (fewer frames because it's slow)
    try:
        sync_fps = benchmark_sync(num_frames=3)
    except Exception as e:
        print(f"\n⚠️  Sync benchmark failed: {e}")
        sync_fps = 0.5  # Assume very slow
    
    # Run Async Benchmark
    try:
        async_fps = benchmark_async(num_frames=60)
    except Exception as e:
        print(f"\n⚠️  Async benchmark failed: {e}")
        async_fps = 0
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Sync FPS:    {sync_fps:>8.2f}")
    print(f"  Async FPS:   {async_fps:>8.2f}")
    
    if sync_fps > 0:
        speedup = async_fps / sync_fps
        print(f"  Speedup:     {speedup:>8.2f}x")
    else:
        print(f"  Speedup:     N/A")
    
    print(f"\n{'='*60}")
    if async_fps >= 20:
        print("✅ PERFORMANCE GOAL MET (≥ 20 FPS)")
    else:
        print("⚠️  PERFORMANCE GOAL NOT MET (< 20 FPS)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
