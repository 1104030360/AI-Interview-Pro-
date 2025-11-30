import React from 'react';
import { 
  LayoutDashboard, 
  Video, 
  BarChart2, 
  History, 
  Bot, 
  Database, 
  Settings, 
  LogOut,
  User
} from 'lucide-react';
import { Page, UserProfile } from '../types';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  userProfile: UserProfile; // Added prop
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate, userProfile }) => {
  const navItems = [
    { id: Page.Overview, label: 'Overview', icon: LayoutDashboard },
    { id: Page.Record, label: 'Interview Room', icon: Video },
    { id: Page.Analysis, label: 'Analytics', icon: BarChart2 },
    { id: Page.History, label: 'History', icon: History },
    { id: Page.Coach, label: 'AI Coach', icon: Bot },
    { id: Page.QuestionBank, label: 'Question Bank', icon: Database },
  ];

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col h-screen sticky top-0 z-10">
      <div className="p-6 flex items-center gap-3 border-b border-border/50">
        <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
          <div className="w-4 h-4 bg-primary rounded-sm animate-pulse" />
        </div>
        <h1 className="text-lg font-bold tracking-tight text-textMain">AI Insight<span className="text-primary">.</span></h1>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-surfaceHighlight text-textMain border-l-2 border-primary'
                  : 'text-textMuted hover:text-textMain hover:bg-surfaceHighlight/50'
              }`}
            >
              <Icon size={18} className={isActive ? 'text-primary' : 'text-textMuted'} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border/50">
        <button 
          onClick={() => onNavigate(Page.Settings)}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
            currentPage === Page.Settings 
             ? 'bg-surfaceHighlight text-textMain' 
             : 'text-textMuted hover:text-textMain hover:bg-surfaceHighlight/50'
          }`}
        >
          <Settings size={18} />
          Settings
        </button>
        <div className="mt-4 flex items-center gap-3 px-3">
          {userProfile.avatarUrl ? (
            <img src={userProfile.avatarUrl} alt="Profile" className="w-8 h-8 rounded-full object-cover border border-zinc-700" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center">
                <User size={14} className="text-zinc-400" />
            </div>
          )}
          <div className="flex flex-col overflow-hidden">
            <span className="text-xs font-medium text-textMain truncate">{userProfile.name}</span>
            <span className="text-[10px] text-textMuted truncate">{userProfile.role}</span>
          </div>
        </div>
      </div>
    </aside>
  );
};