import React from 'react';
import { Inbox, Plus } from 'lucide-react';
import { Button } from '../ui/Button';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-16 h-16 rounded-full bg-surfaceHighlight flex items-center justify-center mb-4">
        {icon || <Inbox size={32} className="text-textMuted" />}
      </div>

      <h3 className="text-lg font-medium text-textMain mb-2">{title}</h3>
      {description && (
        <p className="text-textMuted text-center max-w-md mb-6">{description}</p>
      )}

      {actionLabel && onAction && (
        <Button onClick={onAction}>
          <Plus size={16} className="mr-2" />
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
