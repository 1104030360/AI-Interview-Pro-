import React from 'react';
import { AlertCircle, RefreshCw, Home, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  code?: string;
  onRetry?: () => void;
  showHomeButton?: boolean;
  showBackButton?: boolean;
  onBack?: () => void;
  onHome?: () => void;
  fullScreen?: boolean;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  code,
  onRetry,
  showHomeButton = false,
  showBackButton = false,
  onBack,
  onHome,
  fullScreen = false
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
        <AlertCircle size={32} className="text-red-400" />
      </div>

      <h3 className="text-xl font-semibold text-textMain mb-2">{title}</h3>
      <p className="text-textMuted text-center max-w-md mb-2">{message}</p>

      {code && (
        <p className="text-xs text-textMuted font-mono bg-surfaceHighlight px-2 py-1 rounded mb-6">
          Error Code: {code}
        </p>
      )}

      <div className="flex gap-3 mt-4">
        {showBackButton && onBack && (
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft size={16} className="mr-2" />
            Go Back
          </Button>
        )}

        {onRetry && (
          <Button onClick={onRetry}>
            <RefreshCw size={16} className="mr-2" />
            Try Again
          </Button>
        )}

        {showHomeButton && onHome && (
          <Button variant="outline" onClick={onHome}>
            <Home size={16} className="mr-2" />
            Go Home
          </Button>
        )}
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-background flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return (
    <div className="bg-red-500/5 border border-red-500/20 rounded-lg">
      {content}
    </div>
  );
};
