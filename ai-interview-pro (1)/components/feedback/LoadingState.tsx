import React from 'react';
import { Spinner } from '../ui/Spinner';

interface LoadingStateProps {
  title?: string;
  description?: string;
  fullScreen?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  title = 'Loading',
  description,
  fullScreen = false
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <Spinner size="lg" className="mb-4" />
      <h3 className="text-lg font-medium text-textMain mb-2">{title}</h3>
      {description && (
        <p className="text-textMuted text-center max-w-md">{description}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};

export const InlineLoading: React.FC<{ text?: string }> = ({ text }) => (
  <div className="flex items-center gap-2 text-textMuted">
    <Spinner size="sm" />
    {text && <span className="text-sm">{text}</span>}
  </div>
);

export const ButtonLoading: React.FC = () => (
  <Spinner size="sm" color="white" />
);
