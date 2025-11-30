/**
 * useUploadTask Hook
 *
 * Manages video upload state with progress tracking and retry logic
 */
import { useState, useRef, useCallback } from 'react';
import { apiClient } from '../services/api';

export interface UploadState {
  progress: number;           // 0-100
  status: 'idle' | 'uploading' | 'success' | 'error' | 'retrying';
  error: string | null;
  taskId: string | null;      // Backend analysis task ID
  retryCount: number;
}

interface UploadResult {
  url: string;
  taskId: string;
  analysisStatus: string;
}

interface UseUploadTaskOptions {
  maxRetries?: number;
  onProgress?: (progress: number) => void;
  onSuccess?: (taskId: string) => void;
  onError?: (error: string) => void;
}

const RETRY_CONFIG = {
  maxRetries: 3,
  baseDelay: 1000,      // 1 second
  maxDelay: 30000,      // 30 seconds max
  backoffMultiplier: 2
};

function calculateDelay(retryCount: number): number {
  const delay = RETRY_CONFIG.baseDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount);
  return Math.min(delay, RETRY_CONFIG.maxDelay);
}

export function useUploadTask(options: UseUploadTaskOptions = {}) {
  const {
    maxRetries = RETRY_CONFIG.maxRetries,
    onProgress,
    onSuccess,
    onError
  } = options;

  const [state, setState] = useState<UploadState>({
    progress: 0,
    status: 'idle',
    error: null,
    taskId: null,
    retryCount: 0
  });

  const abortControllerRef = useRef<(() => void) | null>(null);
  const pendingUploadRef = useRef<{
    sessionId: string;
    camera: string;
    file: File;
  } | null>(null);

  const upload = useCallback(async (
    sessionId: string,
    camera: string,
    file: File
  ): Promise<string | null> => {
    // Store upload params for retry
    pendingUploadRef.current = { sessionId, camera, file };

    setState(prev => ({
      ...prev,
      status: 'uploading',
      progress: 0,
      error: null
    }));

    try {
      const result = await apiClient.uploadVideoWithProgress(
        sessionId,
        camera,
        file,
        (progress) => {
          setState(prev => ({ ...prev, progress }));
          onProgress?.(progress);
        },
        (abort) => {
          abortControllerRef.current = abort;
        }
      );

      setState(prev => ({
        ...prev,
        status: 'success',
        progress: 100,
        taskId: result.taskId
      }));

      onSuccess?.(result.taskId);
      return result.taskId;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';

      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage
      }));

      onError?.(errorMessage);
      return null;
    }
  }, [onProgress, onSuccess, onError]);

  const retry = useCallback(async (): Promise<string | null> => {
    if (!pendingUploadRef.current) return null;

    if (state.retryCount >= maxRetries) {
      setState(prev => ({
        ...prev,
        error: `Max retries (${maxRetries}) exceeded`
      }));
      return null;
    }

    const { sessionId, camera, file } = pendingUploadRef.current;

    setState(prev => ({
      ...prev,
      status: 'retrying',
      retryCount: prev.retryCount + 1,
      progress: 0
    }));

    // Exponential backoff delay
    const delay = calculateDelay(state.retryCount);
    await new Promise(resolve => setTimeout(resolve, delay));

    return upload(sessionId, camera, file);
  }, [state.retryCount, maxRetries, upload]);

  const cancel = useCallback(() => {
    abortControllerRef.current?.();
    setState(prev => ({
      ...prev,
      status: 'idle',
      progress: 0
    }));
  }, []);

  const reset = useCallback(() => {
    setState({
      progress: 0,
      status: 'idle',
      error: null,
      taskId: null,
      retryCount: 0
    });
    pendingUploadRef.current = null;
  }, []);

  return { state, upload, retry, cancel, reset };
}
