import React, { useState, useEffect, useRef } from 'react';
import { Video, Mic, MicOff, VideoOff, Play, Square, Users, User, Settings2, ChevronDown, RefreshCcw, ArrowRight, PlayCircle, AlertCircle, X } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { useToast } from '../components/ui/Toast';
import { Spinner } from '../components/ui/Spinner';
import { UploadProgress } from '../components/ui/UploadProgress';
import { Page, SystemCapabilities } from '../types';
import { apiClient } from '../services/api';
import { useUploadTask } from '../hooks/useUploadTask';

// State Machine Definition
type RecorderState = 'idle' | 'preview' | 'recording' | 'review' | 'analyzing';

interface RecordProps {
  onNavigate: (page: Page, params?: any) => void;
  systemCapabilities: SystemCapabilities;
}

export const Record: React.FC<RecordProps> = ({ onNavigate, systemCapabilities }) => {
  const toast = useToast();

  // Upload hooks for progress tracking
  const cam0Upload = useUploadTask({
    maxRetries: 3,
    onSuccess: (taskId) => console.log('✅ cam0 uploaded, taskId:', taskId),
    onError: (error) => console.error('❌ cam0 upload error:', error)
  });

  const cam1Upload = useUploadTask({
    maxRetries: 3,
    onSuccess: (taskId) => console.log('✅ cam1 uploaded, taskId:', taskId),
    onError: (error) => console.error('❌ cam1 upload error:', error)
  });

  // UI Configuration
  const [mode, setMode] = useState<'Single' | 'Dual'>('Single');
  const [showModeError, setShowModeError] = useState(false);

  // Hardware State
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);

  // Recorder Logic
  const [recorderState, setRecorderState] = useState<RecorderState>('idle');
  const [timer, setTimer] = useState(0);
  const timerIntervalRef = useRef<number | null>(null);

  // Session Configuration
  const [scenario, setScenario] = useState('Sr. Frontend Engineer - System Design');
  const [duration, setDuration] = useState(30);
  const [candidateName, setCandidateName] = useState('');

  // MediaRecorder State
  const videoRef1 = useRef<HTMLVideoElement>(null);
  const videoRef2 = useRef<HTMLVideoElement>(null);
  const mediaRecorder1 = useRef<MediaRecorder | null>(null);
  const mediaRecorder2 = useRef<MediaRecorder | null>(null);
  const stream1 = useRef<MediaStream | null>(null);
  const stream2 = useRef<MediaStream | null>(null);
  const recordedChunks1 = useRef<Blob[]>([]);
  const recordedChunks2 = useRef<Blob[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleModeSwitch = (newMode: 'Single' | 'Dual') => {
    if (newMode === 'Dual' && systemCapabilities.cameraCount < 2) {
      setShowModeError(true);
    } else {
      setMode(newMode);
      setShowModeError(false);
    }
  };

  // Timer Effect
  useEffect(() => {
    if (recorderState === 'recording') {
      // Clear existing interval first to be safe
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

      timerIntervalRef.current = window.setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
    } else {
      // Pause timer when not recording (e.g. in review state)
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
    }
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [recorderState]);

  const formatTime = (totalSeconds: number) => {
    const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const s = (totalSeconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Cleanup streams on unmount
  useEffect(() => {
    return () => {
      if (stream1.current) {
        stream1.current.getTracks().forEach(track => track.stop());
      }
      if (stream2.current) {
        stream2.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Effect: Connect streams to video elements when state changes to preview/recording
  useEffect(() => {
    const connectStreamsToVideo = async () => {
      // Only connect when in preview or recording state
      if (recorderState !== 'preview' && recorderState !== 'recording') {
        return;
      }

      // Connect camera 1
      if (stream1.current && videoRef1.current && !videoRef1.current.srcObject) {
        console.log('🎥 [Camera] 連接 stream1 到 video 元素...');
        videoRef1.current.srcObject = stream1.current;

        // Add event listeners for debugging
        videoRef1.current.onloadedmetadata = () => {
          console.log('✅ [Camera] Video metadata 已加載');
          console.log('🎥 [Camera] Video dimensions:',
            videoRef1.current?.videoWidth, 'x', videoRef1.current?.videoHeight);
        };

        videoRef1.current.onplay = () => {
          console.log('✅ [Camera] Video 開始播放');
        };

        videoRef1.current.onerror = (e) => {
          console.error('❌ [Camera] Video 錯誤:', e);
        };

        try {
          await videoRef1.current.play();
          console.log('✅ [Camera] video.play() 成功');
        } catch (err) {
          console.error('❌ [Camera] video.play() 失敗:', err);
        }
      }

      // Connect camera 2 if dual mode
      if (mode === 'Dual' && stream2.current && videoRef2.current && !videoRef2.current.srcObject) {
        console.log('🎥 [Camera] 連接 stream2 到 video 元素...');
        videoRef2.current.srcObject = stream2.current;
        try {
          await videoRef2.current.play();
          console.log('✅ [Camera] video2.play() 成功');
        } catch (err) {
          console.error('❌ [Camera] video2.play() 失敗:', err);
        }
      }
    };

    connectStreamsToVideo();
  }, [recorderState, mode]);

  // Actions
  const handleInitialize = async () => {
    console.log('🎥 [Camera] 開始初始化攝像頭...');
    console.log('🎥 [Camera] 麥克風狀態:', micOn);
    console.log('🎥 [Camera] 攝像頭狀態:', camOn);
    console.log('🎥 [Camera] 模式:', mode);

    try {
      // Step 1: Set state to 'preview' to render video elements
      console.log('🎥 [Camera] 設置狀態為 preview...');
      setRecorderState('preview');
      setTimer(0);

      // Step 2: Get user media for camera 1
      console.log('🎥 [Camera] 請求攝像頭權限...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: micOn
      });

      console.log('✅ [Camera] 攝像頭權限獲取成功！');
      console.log('🎥 [Camera] Stream tracks:', stream.getTracks().map(t => ({
        kind: t.kind,
        label: t.label,
        enabled: t.enabled,
        readyState: t.readyState
      })));

      stream1.current = stream;
      console.log('🎥 [Camera] Stream 已保存到 stream1.current');

      // Step 3: If dual mode, get second camera
      if (mode === 'Dual') {
        console.log('🎥 [Camera] Dual 模式 - 嘗試訪問第二個攝像頭...');
        try {
          const devices = await navigator.mediaDevices.enumerateDevices();
          const videoDevices = devices.filter(d => d.kind === 'videoinput');
          console.log('🎥 [Camera] 找到的視頻設備:', videoDevices.map(d => d.label));

          if (videoDevices.length >= 2) {
            const stream2nd = await navigator.mediaDevices.getUserMedia({
              video: { deviceId: videoDevices[1].deviceId },
              audio: false
            });
            stream2.current = stream2nd;
            console.log('✅ [Camera] 第二個攝像頭獲取成功');
          } else {
            console.warn('⚠️ [Camera] 只找到', videoDevices.length, '個攝像頭');
          }
        } catch (err) {
          console.warn('⚠️ [Camera] 訪問第二個攝像頭失敗:', err);
        }
      }

      console.log('✅ [Camera] 初始化完成');
      // Note: Video connection is handled by useEffect above
    } catch (error) {
      console.error('❌ [Camera] 初始化失敗:', error);
      console.error('❌ [Camera] 錯誤詳情:', {
        name: (error as Error).name,
        message: (error as Error).message,
        stack: (error as Error).stack
      });
      // Revert to idle state on error
      setRecorderState('idle');
      toast.error('Camera Access Failed', 'Please check your camera permissions and try again.');
    }
  };

  const handleStartRecording = async () => {
    try {
      // Create interview session
      const response = await apiClient.createInterviewSession({
        scenario,
        mode,
        plannedDuration: duration,
        candidateName: candidateName || undefined
      });

      setSessionId(response.sessionId);

      // Setup MediaRecorder for camera 1
      if (stream1.current) {
        const recorder1 = new MediaRecorder(stream1.current, {
          mimeType: 'video/webm;codecs=vp8'
        });

        recorder1.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunks1.current.push(event.data);
          }
        };

        mediaRecorder1.current = recorder1;
        recorder1.start(1000); // Collect data every second
      }

      // Setup MediaRecorder for camera 2 if dual mode
      if (mode === 'Dual' && stream2.current) {
        const recorder2 = new MediaRecorder(stream2.current, {
          mimeType: 'video/webm;codecs=vp8'
        });

        recorder2.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunks2.current.push(event.data);
          }
        };

        mediaRecorder2.current = recorder2;
        recorder2.start(1000);
      }

      setRecorderState('recording');
    } catch (error) {
      console.error('Failed to start recording', error);
      toast.error('Recording Failed', 'Could not start the recording session. Please try again.');
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorder1.current && mediaRecorder1.current.state !== 'inactive') {
      mediaRecorder1.current.stop();
    }

    if (mediaRecorder2.current && mediaRecorder2.current.state !== 'inactive') {
      mediaRecorder2.current.stop();
    }

    setRecorderState('review');
  };

  const handleResumeRecording = () => {
    // Resume recording
    if (mediaRecorder1.current && mediaRecorder1.current.state === 'inactive') {
      mediaRecorder1.current.start(1000);
    }

    if (mediaRecorder2.current && mediaRecorder2.current.state === 'inactive') {
      mediaRecorder2.current.start(1000);
    }

    setRecorderState('recording');
  };

  const handleRetake = () => {
    // Stop and clear MediaRecorders
    if (mediaRecorder1.current) {
      if (mediaRecorder1.current.state !== 'inactive') {
        mediaRecorder1.current.stop();
      }
      mediaRecorder1.current = null;
    }

    if (mediaRecorder2.current) {
      if (mediaRecorder2.current.state !== 'inactive') {
        mediaRecorder2.current.stop();
      }
      mediaRecorder2.current = null;
    }

    // Clear recorded chunks
    recordedChunks1.current = [];
    recordedChunks2.current = [];

    // Reset to preview
    setRecorderState('preview');
    setTimer(0);
  };

  const handleStartInterviewAnalysis = async () => {
    // 邊界檢查：sessionId 必須存在
    if (!sessionId) {
      console.error('❌ [Upload] sessionId is null - recording flow may be incomplete');
      toast.error('錯誤', '沒有有效的面試 Session，請重新開始錄製');
      setRecorderState('idle');
      return;
    }

    // 邊界檢查：必須有錄製內容
    if (recordedChunks1.current.length === 0) {
      console.error('❌ [Upload] No recorded chunks - nothing to upload');
      toast.error('錯誤', '沒有錄製內容，請先完成錄製');
      setRecorderState('review');
      return;
    }

    setRecorderState('analyzing');

    // Reset upload states
    cam0Upload.reset();
    cam1Upload.reset();

    try {
      // Prepare upload promises
      const uploadPromises: Promise<string | null>[] = [];

      // Upload video for camera 0 (candidate)
      const blob1 = new Blob(recordedChunks1.current, { type: 'video/webm' });
      const file1 = new File([blob1], `${sessionId}_cam0.webm`, { type: 'video/webm' });
      console.log('📤 [Upload] Uploading cam0 video:', file1.name, `(${(file1.size / 1024 / 1024).toFixed(2)} MB)`);
      uploadPromises.push(cam0Upload.upload(sessionId, 'cam0', file1));

      // Upload video for camera 1 (interviewer) if dual mode
      if (mode === 'Dual' && recordedChunks2.current.length > 0) {
        const blob2 = new Blob(recordedChunks2.current, { type: 'video/webm' });
        const file2 = new File([blob2], `${sessionId}_cam1.webm`, { type: 'video/webm' });
        console.log('📤 [Upload] Uploading cam1 video:', file2.name, `(${(file2.size / 1024 / 1024).toFixed(2)} MB)`);
        uploadPromises.push(cam1Upload.upload(sessionId, 'cam1', file2));
      }

      // Wait for all uploads to complete
      const results = await Promise.all(uploadPromises);

      // Check if any upload failed
      if (results.some(r => r === null)) {
        // Stay in analyzing state to show retry option
        toast.error('上傳失敗', '視頻上傳失敗，請重試或取消');
        return;
      }

      // Navigate to Analysis page with sessionId
      console.log('✅ [Upload] All uploads completed, navigating to Analysis page');
      onNavigate(Page.Analysis, { interviewId: sessionId });
    } catch (error) {
      console.error('❌ [Upload] Unexpected error:', error);
      toast.error('上傳失敗', '發生意外錯誤，請重試');
      setRecorderState('review');
    }
  };

  const handleCancelUpload = () => {
    cam0Upload.cancel();
    cam1Upload.cancel();
    setRecorderState('review');
  };

  return (
    <div className="h-[calc(100vh-2rem)] flex flex-col relative">

      {/* Mode Restriction Modal/Alert */}
      {showModeError && (
        <div className="absolute top-14 right-0 z-50 bg-red-500/10 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 max-w-md backdrop-blur-md animate-in slide-in-from-top-2">
          <AlertCircle size={20} className="text-red-500 shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-sm">Dual Mode Unavailable</p>
            <p className="text-xs text-red-300/80 mt-0.5">Only 1 camera detected. Please connect a secondary camera to use this feature.</p>
          </div>
          <button onClick={() => setShowModeError(false)} className="text-red-400 hover:text-red-300"><X size={18} /></button>
        </div>
      )}

      {/* Header Configuration */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-textMain">Interview Session</h2>
          <p className="text-textMuted">Configure your environment and device settings.</p>
        </div>
        <div className="flex gap-3">
          <div className="bg-surface border border-border p-1 rounded-lg flex">
            <button
              onClick={() => handleModeSwitch('Single')}
              className={`px-4 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-all ${mode === 'Single' ? 'bg-surfaceHighlight text-textMain shadow-sm' : 'text-textMuted hover:text-textMain'}`}
            >
              <User size={16} /> Single
            </button>
            <button
              onClick={() => handleModeSwitch('Dual')}
              className={`px-4 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-all ${mode === 'Dual' ? 'bg-surfaceHighlight text-textMain shadow-sm' : 'text-textMuted hover:text-textMain'}`}
            >
              <Users size={16} /> Dual
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">
        {/* Left Column: Settings & Info */}
        <div className="space-y-6">
          <Card title="Session Details">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Scenario</label>
                <div className="relative">
                  <select
                    value={scenario}
                    onChange={(e) => setScenario(e.target.value)}
                    className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 appearance-none focus:ring-1 focus:ring-primary focus:outline-none"
                  >
                    <option>Sr. Frontend Engineer - System Design</option>
                    <option>Product Manager - Behavioral</option>
                    <option>Data Scientist - Technical Screen</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-3 text-textMuted pointer-events-none" size={16} />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Duration</label>
                <div className="relative">
                  <select
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 appearance-none focus:ring-1 focus:ring-primary focus:outline-none"
                  >
                    <option value={30}>30 Minutes</option>
                    <option value={45}>45 Minutes</option>
                    <option value={60}>60 Minutes</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-3 text-textMuted pointer-events-none" size={16} />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Candidate Name</label>
                <input
                  type="text"
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                  className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none"
                  placeholder="e.g., John Doe"
                />
              </div>
            </div>
          </Card>

          <Card title="Device Check">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-surfaceHighlight/50 border border-border">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${camOn ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-textMain">Camera (FaceTime HD)</span>
                </div>
                <Button size="sm" variant="outline" onClick={() => setCamOn(!camOn)}>
                  {camOn ? 'Active' : 'Inactive'}
                </Button>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-surfaceHighlight/50 border border-border">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${micOn ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-textMain">Microphone (Default)</span>
                </div>
                <Button size="sm" variant="outline" onClick={() => setMicOn(!micOn)}>
                  {micOn ? 'Active' : 'Inactive'}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Preview Area */}
        <div className="lg:col-span-2 relative bg-black rounded-2xl border border-zinc-800 overflow-hidden flex items-center justify-center group">
          {recorderState === 'idle' ? (
            <div className="text-center p-8">
              <div className="w-20 h-20 bg-surfaceHighlight rounded-full flex items-center justify-center mx-auto mb-6 border border-zinc-700">
                <Settings2 className="text-textMuted" size={32} />
              </div>
              <h3 className="text-xl font-semibold text-textMain mb-2">Ready to Start?</h3>
              <p className="text-textMuted max-w-md mx-auto mb-8">
                Ensure you are in a well-lit room with minimal background noise.
                {mode === 'Dual' ? ' Both cameras will be activated.' : ' Your primary camera will be used.'}
              </p>
              <Button size="lg" onClick={handleInitialize} icon={<Play size={20} />}>
                Initialize Camera
              </Button>
            </div>
          ) : (
            <div className="w-full h-full flex flex-col">
              {/* Live Camera Feed */}
              <div className={`flex-1 relative ${mode === 'Dual' ? 'grid grid-cols-2 divide-x divide-zinc-800' : ''}`}>
                {/* Cam 1 */}
                <div className="relative w-full h-full bg-zinc-900 flex items-center justify-center">
                  {camOn ? (
                    <>
                      <video
                        ref={videoRef1}
                        autoPlay
                        muted
                        playsInline
                        className="w-full h-full object-cover"
                      />
                    </>
                  ) : (
                    <div className="flex flex-col items-center text-zinc-600">
                      <VideoOff size={48} className="mb-2" />
                      <span>Camera Off</span>
                    </div>
                  )}
                  <span className="absolute top-4 left-4 bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">Candidate</span>

                  {/* Recording Indicator Overlay */}
                  {recorderState === 'recording' && (
                    <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500/20 border border-red-500/30 px-3 py-1 rounded-full">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                      <span className="text-xs font-medium text-red-500">REC</span>
                    </div>
                  )}

                  {recorderState === 'analyzing' && (
                    <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center backdrop-blur-sm z-20 p-8">
                      <h3 className="text-lg font-semibold text-textMain mb-6">Uploading Videos...</h3>

                      <div className="w-full max-w-md space-y-4">
                        {/* Camera 0 Upload Progress */}
                        {recordedChunks1.current.length > 0 && (
                          <UploadProgress
                            progress={cam0Upload.state.progress}
                            status={cam0Upload.state.status}
                            error={cam0Upload.state.error}
                            camera="cam0"
                            retryCount={cam0Upload.state.retryCount}
                            maxRetries={3}
                            onRetry={cam0Upload.retry}
                            onCancel={handleCancelUpload}
                          />
                        )}

                        {/* Camera 1 Upload Progress (Dual mode) */}
                        {mode === 'Dual' && recordedChunks2.current.length > 0 && (
                          <UploadProgress
                            progress={cam1Upload.state.progress}
                            status={cam1Upload.state.status}
                            error={cam1Upload.state.error}
                            camera="cam1"
                            retryCount={cam1Upload.state.retryCount}
                            maxRetries={3}
                            onRetry={cam1Upload.retry}
                            onCancel={handleCancelUpload}
                          />
                        )}
                      </div>

                      {/* All uploads complete message */}
                      {cam0Upload.state.status === 'success' &&
                       (mode !== 'Dual' || cam1Upload.state.status === 'success') && (
                        <p className="text-primary mt-4 animate-pulse">
                          All uploads complete! Redirecting...
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Cam 2 (Only in Dual) */}
                {mode === 'Dual' && (
                  <div className="relative w-full h-full bg-zinc-800 flex items-center justify-center">
                    <video
                      ref={videoRef2}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-full object-cover grayscale"
                    />
                    <span className="absolute top-4 left-4 bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">Interviewer</span>
                  </div>
                )}
              </div>

              {/* Control Bar */}
              <div className="h-24 bg-zinc-950 border-t border-zinc-800 flex items-center justify-center px-8">
                {/* Left Controls */}
                <div className="flex-1 flex items-center gap-4">
                  <button disabled={recorderState === 'analyzing'} className={`p-3 rounded-full transition-all ${micOn ? 'bg-surfaceHighlight hover:bg-zinc-700 text-textMain' : 'bg-red-500/20 text-red-500'}`} onClick={() => setMicOn(!micOn)}>
                    {micOn ? <Mic size={20} /> : <MicOff size={20} />}
                  </button>
                  <button disabled={recorderState === 'analyzing'} className={`p-3 rounded-full transition-all ${camOn ? 'bg-surfaceHighlight hover:bg-zinc-700 text-textMain' : 'bg-red-500/20 text-red-500'}`} onClick={() => setCamOn(!camOn)}>
                    {camOn ? <Video size={20} /> : <VideoOff size={20} />}
                  </button>
                </div>

                {/* Center Controls (Main Action & Timer) */}
                <div className="flex flex-col items-center justify-center gap-2 min-w-[300px]">
                  <div className="font-mono text-2xl font-bold tracking-wider text-textMain tabular-nums">
                    {formatTime(timer)}
                  </div>

                  {recorderState === 'preview' && (
                    <button
                      onClick={handleStartRecording}
                      className="h-10 px-6 rounded-full bg-red-500 hover:bg-red-600 text-white text-sm font-bold flex items-center gap-2 transition-all"
                    >
                      <div className="w-2 h-2 rounded-full bg-white" /> Start Recording
                    </button>
                  )}

                  {recorderState === 'recording' && (
                    <button
                      onClick={handleStopRecording}
                      className="h-10 px-6 rounded-full bg-zinc-800 hover:bg-zinc-700 text-textMain border border-zinc-600 text-sm font-bold flex items-center gap-2 transition-all"
                    >
                      <Square size={14} fill="currentColor" /> Stop Recording
                    </button>
                  )}

                  {recorderState === 'review' && (
                    <div className="flex items-center gap-3">
                      <button
                        onClick={handleResumeRecording}
                        className="h-10 px-5 rounded-full bg-zinc-800 hover:bg-zinc-700 text-textMain border border-zinc-600 text-sm font-bold flex items-center gap-2 transition-all"
                      >
                        <PlayCircle size={16} /> Continue Rec
                      </button>
                      <button
                        onClick={handleStartInterviewAnalysis}
                        className="h-10 px-5 rounded-full bg-primary hover:bg-primaryHover text-white text-sm font-bold flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                      >
                        Start Analysis <ArrowRight size={16} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Right Controls */}
                <div className="flex-1 flex justify-end">
                  {(recorderState === 'review' || recorderState === 'preview') && (
                    <button
                      onClick={handleRetake}
                      className="flex items-center gap-2 text-textMuted hover:text-textMain text-sm px-4 py-2 rounded-lg hover:bg-surfaceHighlight transition-all"
                    >
                      <RefreshCcw size={16} /> Reset
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
