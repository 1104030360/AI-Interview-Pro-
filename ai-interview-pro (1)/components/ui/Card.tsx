import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', title, subtitle, action }) => {
  return (
    <div className={`bg-surface border border-border rounded-xl overflow-hidden ${className}`}>
      {(title || action) && (
        <div className="px-6 py-5 border-b border-border flex items-center justify-between">
          <div>
            {title && <h3 className="text-base font-semibold text-textMain">{title}</h3>}
            {subtitle && <p className="text-sm text-textMuted mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
};