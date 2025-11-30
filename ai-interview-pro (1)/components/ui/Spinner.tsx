import React from 'react';
import { cn } from '../../utils/cn';

interface SpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'muted';
  className?: string;
}

const sizeClasses = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12'
};

const colorClasses = {
  primary: 'text-primary',
  white: 'text-white',
  muted: 'text-textMuted'
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className
}) => (
  <svg
    className={cn(
      'animate-spin',
      sizeClasses[size],
      colorClasses[color],
      className
    )}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    role="status"
    aria-label="Loading"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
    />
  </svg>
);

interface SpinnerWithTextProps extends SpinnerProps {
  text?: string;
}

export const SpinnerWithText: React.FC<SpinnerWithTextProps> = ({
  text = 'Loading...',
  ...props
}) => (
  <div className="flex items-center gap-2">
    <Spinner {...props} />
    <span className="text-textMuted text-sm">{text}</span>
  </div>
);
