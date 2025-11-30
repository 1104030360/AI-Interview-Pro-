/**
 * VideoPlayer Component
 *
 * Video playback with camera switching, timeline, and controls
 */
import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Minimize, User, Users, Download, VideoOff } from 'lucide-react';
import { Button } from './ui/Button';

interface VideoInfo {
  url: string | null;
  available: boolean;
  filename: string | null;
  mimeType: string;
}

interface VideoPlayerProps {
  cam0?: VideoInfo;
  cam1?: VideoInfo;
  onTimeUpdate?: (currentTime: number) => void;
  className?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  cam0,
  cam1,
  onTimeUpdate,
  className = ''
}) => {
  const [activeCamera, setActiveCamera] = useState<'cam0' | 'cam1'>('cam0');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const cam0Available = cam0?.available ?? false;
  const cam1Available = cam1?.available ?? false;
  const currentVideo = activeCamera === 'cam0' ? cam0 : cam1;
  const currentUrl = currentVideo?.url || null;

  // Handle camera switch - preserve playback position
  useEffect(() => {
    if (videoRef.current && currentUrl) {
      const savedTime = currentTime;
      const wasPlaying = isPlaying;

      videoRef.current.load();

      videoRef.current.onloadeddata = () => {
        if (videoRef.current) {
          videoRef.current.currentTime = savedTime;
          if (wasPlaying) {
            videoRef.current.play().catch(() => {});
          }
        }
      };
    }
  }, [activeCamera]);

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(console.error);
      }
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      setCurrentTime(time);
      onTimeUpdate?.(time);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value);
    setVolume(vol);
    if (videoRef.current) {
      videoRef.current.volume = vol;
      videoRef.current.muted = vol === 0;
      setIsMuted(vol === 0);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !isMuted;
      videoRef.current.muted = newMuted;
      setIsMuted(newMuted);
    }
  };

  const toggleFullscreen = async () => {
    if (!containerRef.current) return;

    try {
      if (!isFullscreen) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (err) {
      console.error('Fullscreen error:', err);
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    if (currentUrl) {
      const link = document.createElement('a');
      link.href = currentUrl;
      link.download = currentVideo?.filename || 'video.webm';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // No videos available
  if (!cam0Available && !cam1Available) {
    return (
      <div className={`bg-surface border border-border rounded-xl p-12 text-center ${className}`}>
        <VideoOff className="mx-auto mb-4 text-zinc-600" size={48} />
        <p className="text-textMuted">No video recordings available</p>
        <p className="text-sm text-zinc-600 mt-2">
          Record an interview session to view playback here
        </p>
      </div>
    );
  }

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      className={`bg-surface border border-border rounded-xl overflow-hidden ${className}`}
    >
      {/* Camera Switch Buttons */}
      <div className="flex items-center justify-between p-3 border-b border-border bg-surfaceHighlight/30">
        <span className="text-sm font-medium text-textMain">Interview Recording</span>
        <div className="flex gap-2">
          <Button
            variant={activeCamera === 'cam0' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveCamera('cam0')}
            disabled={!cam0Available}
          >
            <User size={14} className="mr-1" /> Candidate
          </Button>
          {cam1Available && (
            <Button
              variant={activeCamera === 'cam1' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveCamera('cam1')}
            >
              <Users size={14} className="mr-1" /> Interviewer
            </Button>
          )}
        </div>
      </div>

      {/* Video Player */}
      <div className="relative aspect-video bg-black">
        {currentUrl ? (
          <video
            ref={videoRef}
            src={currentUrl}
            className="w-full h-full"
            muted={isMuted}
            playsInline
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-textMuted">
            <div className="text-center">
              <VideoOff className="mx-auto mb-2 text-zinc-600" size={32} />
              <span>Video not available</span>
            </div>
          </div>
        )}

        {/* Play button overlay when paused */}
        {!isPlaying && currentUrl && (
          <button
            onClick={handlePlayPause}
            className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
          >
            <div className="w-16 h-16 bg-white/20 backdrop-blur rounded-full flex items-center justify-center">
              <Play size={32} className="text-white ml-1" />
            </div>
          </button>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 border-t border-border bg-surfaceHighlight/50">
        {/* Progress Bar */}
        <div className="relative mb-3">
          <input
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1 appearance-none bg-zinc-700 rounded cursor-pointer"
            style={{
              background: `linear-gradient(to right, #06b6d4 0%, #06b6d4 ${progressPercent}%, #3f3f46 ${progressPercent}%, #3f3f46 100%)`
            }}
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Play/Pause */}
            <button
              onClick={handlePlayPause}
              disabled={!currentUrl}
              className="p-2 hover:bg-surfaceHighlight rounded transition-colors disabled:opacity-50"
            >
              {isPlaying ? <Pause size={18} /> : <Play size={18} />}
            </button>

            {/* Volume */}
            <button
              onClick={toggleMute}
              className="p-2 hover:bg-surfaceHighlight rounded transition-colors"
            >
              {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-16 h-1 appearance-none bg-zinc-700 rounded cursor-pointer"
            />

            {/* Time Display */}
            <span className="text-xs text-textMuted ml-2 font-mono">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Download Button */}
            {currentUrl && (
              <button
                onClick={handleDownload}
                className="p-2 hover:bg-surfaceHighlight rounded transition-colors flex items-center gap-1 text-sm text-textMuted hover:text-textMain"
              >
                <Download size={16} />
              </button>
            )}

            {/* Fullscreen */}
            <button
              onClick={toggleFullscreen}
              className="p-2 hover:bg-surfaceHighlight rounded transition-colors"
            >
              {isFullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
