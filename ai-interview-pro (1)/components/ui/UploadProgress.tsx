/**
 * UploadProgress Component
 *
 * Displays upload progress with status indicators and retry capability
 */
import React from 'react';
import { Upload, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

interface UploadProgressProps {
  progress: number;
  status: 'idle' | 'uploading' | 'success' | 'error' | 'retrying';
  error?: string | null;
  camera: string;
  retryCount?: number;
  maxRetries?: number;
  onRetry?: () => void;
  onCancel?: () => void;
}

const STATUS_CONFIG = {
  idle: {
    icon: Upload,
    color: 'text-textMuted',
    bg: 'bg-zinc-700',
    label: 'Ready'
  },
  uploading: {
    icon: Upload,
    color: 'text-primary',
    bg: 'bg-primary',
    label: 'Uploading'
  },
  success: {
    icon: CheckCircle,
    color: 'text-green-400',
    bg: 'bg-green-500',
    label: 'Complete'
  },
  error: {
    icon: XCircle,
    color: 'text-red-400',
    bg: 'bg-red-500',
    label: 'Failed'
  },
  retrying: {
    icon: RefreshCw,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500',
    label: 'Retrying'
  }
};

export const UploadProgress: React.FC<UploadProgressProps> = ({
  progress,
  status,
  error,
  camera,
  retryCount = 0,
  maxRetries = 3,
  onRetry,
  onCancel
}) => {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  const cameraLabel = camera === 'cam0' ? 'Candidate Camera' : 'Interviewer Camera';

  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return `${progress}%`;
      case 'success':
        return 'Complete';
      case 'error':
        return 'Failed';
      case 'retrying':
        return `Retry ${retryCount}/${maxRetries}...`;
      default:
        return 'Ready';
    }
  };

  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon
            size={16}
            className={`${config.color} ${
              status === 'uploading' || status === 'retrying' ? 'animate-pulse' : ''
            } ${status === 'retrying' ? 'animate-spin' : ''}`}
          />
          <span className="text-sm font-medium text-textMain">{cameraLabel}</span>
        </div>
        <span className={`text-xs ${config.color}`}>{getStatusText()}</span>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${config.bg} transition-all duration-300 ease-out`}
          style={{ width: `${status === 'success' ? 100 : progress}%` }}
        />
      </div>

      {/* Error Message & Actions */}
      {status === 'error' && (
        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-red-400 flex-1 mr-2">{error || 'Upload failed'}</span>
          <div className="flex gap-2 shrink-0">
            {onCancel && (
              <Button variant="ghost" size="sm" onClick={onCancel}>
                Cancel
              </Button>
            )}
            {onRetry && retryCount < maxRetries && (
              <Button variant="outline" size="sm" onClick={onRetry}>
                <RefreshCw size={14} className="mr-1" />
                Retry
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Retrying indicator */}
      {status === 'retrying' && (
        <div className="mt-2 text-xs text-yellow-400">
          Retrying upload... Please wait.
        </div>
      )}
    </div>
  );
};

export default UploadProgress;
