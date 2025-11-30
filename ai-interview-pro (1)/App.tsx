import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { Record } from './pages/Record';
import { Analysis } from './pages/Analysis';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Coach } from './pages/Coach';
import { QuestionBank } from './pages/QuestionBank';
import { SystemCheckModal } from './components/SystemCheckModal';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './components/ui/Toast';
import { Page, AppSettings, SystemCapabilities } from './types';
import { apiClient } from './services/api';

// Default Settings Definition
const DEFAULT_SETTINGS: AppSettings = {
  profile: {
    name: 'Alex Chen',
    role: 'Senior Engineer',
    language: 'en',
  },
  ai: {
    provider: 'ollama',
    apiKey: '',
    model: 'llama3:latest',
  },
  prompts: {
    global: 'You are an expert technical interviewer. Analyze the candidate\'s responses for clarity, accuracy, and depth.',
    interviewSuggestions: 'Provide 3 actionable tips to improve the answer. Focus on STAR method structure.',
    coachChat: 'You are a friendly and encouraging career coach. Help the user practice behavioral questions.',
  }
};

const DEFAULT_CAPABILITIES: SystemCapabilities = {
  browserSupported: true,
  hasMicrophone: true,
  cameraCount: 1,
  backendOnline: true
};

type AppState = 'login' | 'landing' | 'checking' | 'app';

const App: React.FC = () => {
  // 應用流程：Landing -> Login -> Checking -> App
  const [appState, setAppState] = useState<AppState>('landing');
  const [currentPage, setCurrentPage] = useState<Page>(Page.Overview);
  const [navigationParams, setNavigationParams] = useState<any>(null);
  const [appSettings, setAppSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [systemCaps, setSystemCaps] = useState<SystemCapabilities>(DEFAULT_CAPABILITIES);

  // Load settings from backend (fallback to localStorage)
  useEffect(() => {
    if (appState === 'app' && apiClient.isAuthenticated()) {
      loadUserSettings();
    } else {
      // Fallback to localStorage if not authenticated
      const saved = localStorage.getItem('ai_interview_settings');
      if (saved) {
        try {
          setAppSettings(JSON.parse(saved));
        } catch (e) {
          console.error('Failed to parse settings', e);
        }
      }
    }
  }, [appState]);

  async function loadUserSettings() {
    try {
      const backendSettings = await apiClient.getSettings();
      setAppSettings(backendSettings);
      // Backup to localStorage
      localStorage.setItem('ai_interview_settings', JSON.stringify(backendSettings));
    } catch (error) {
      console.error('Failed to load user settings from backend', error);
      // Fallback to localStorage
      const saved = localStorage.getItem('ai_interview_settings');
      if (saved) {
        try {
          setAppSettings(JSON.parse(saved));
        } catch (e) {
          console.error('Failed to parse settings', e);
        }
      }
    }
  }

  // Update Settings Handler
  const updateSettings = async (newSettings: AppSettings) => {
    setAppSettings(newSettings);

    if (apiClient.isAuthenticated()) {
      try {
        await apiClient.updateSettings(newSettings);
      } catch (error) {
        console.error('Failed to update settings on backend', error);
      }
    }

    // Always backup to localStorage
    localStorage.setItem('ai_interview_settings', JSON.stringify(newSettings));
  };

  const handleCheckComplete = (caps: SystemCapabilities) => {
    setSystemCaps(caps);
    setAppState('app');
  };

  const handleNavigate = (page: Page, params?: any) => {
    setCurrentPage(page);
    setNavigationParams(params || null);
  };

  const renderPage = () => {
    switch (currentPage) {
      case Page.Overview: return <Overview onNavigate={handleNavigate} />;
      case Page.Record: return <Record onNavigate={handleNavigate} systemCapabilities={systemCaps} />;
      case Page.Analysis: return <Analysis interviewId={navigationParams?.interviewId} />;
      case Page.History: return <History />;
      case Page.Coach: return <Coach />;
      case Page.QuestionBank: return <QuestionBank onNavigate={handleNavigate} />;
      case Page.Settings: return <Settings settings={appSettings} onUpdateSettings={updateSettings} />;
      default: return <Overview onNavigate={handleNavigate} />;
    }
  };

  // 渲染流程：Landing -> Login -> Checking -> App
  if (appState === 'landing') {
    return <Landing onEnter={() => setAppState('login')} />;
  }

  if (appState === 'login') {
    return (
      <ToastProvider>
        <Login onLoginSuccess={() => setAppState('checking')} />
      </ToastProvider>
    );
  }

  if (appState === 'checking') {
    return <SystemCheckModal onComplete={handleCheckComplete} onBack={() => setAppState('login')} />;
  }

  return (
    <ErrorBoundary>
      <ToastProvider>
        <div className="flex min-h-screen bg-background text-textMain font-sans antialiased selection:bg-primary/30">
          <Sidebar
            currentPage={currentPage}
            onNavigate={setCurrentPage}
            userProfile={appSettings.profile}
          />
          <main className="flex-1 h-screen overflow-y-auto">
            <div className="container mx-auto p-6 md:p-12">
              {renderPage()}
            </div>
          </main>
        </div>
      </ToastProvider>
    </ErrorBoundary>
  );
};

export default App;
