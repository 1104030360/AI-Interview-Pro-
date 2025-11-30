import React, { useState, useRef, useEffect } from 'react';
import { Save, User, Cpu, Terminal, AlertCircle, Eye, EyeOff, Upload, Camera } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { AppSettings } from '../types';
import { apiClient } from '../services/api';

interface SettingsProps {
  settings: AppSettings;
  onUpdateSettings: (newSettings: AppSettings) => void;
}

export const Settings: React.FC<SettingsProps> = ({ settings, onUpdateSettings }) => {
  const [showKey, setShowKey] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    setLoading(true);
    try {
      const backendSettings = await apiClient.getSettings();
      onUpdateSettings(backendSettings);
    } catch (error) {
      console.error('Failed to load settings from backend', error);
      // Fallback to localStorage if backend fails
      const saved = localStorage.getItem('ai_interview_settings');
      if (saved) {
        try {
          onUpdateSettings(JSON.parse(saved));
        } catch (e) {
          console.error('Failed to parse localStorage settings', e);
        }
      }
    } finally {
      setLoading(false);
    }
  }

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiClient.updateSettings(settings);
      // Backup to localStorage
      localStorage.setItem('ai_interview_settings', JSON.stringify(settings));
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
    } catch (error) {
      console.error('Failed to save settings to backend', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const updateProfile = (field: string, value: string) => {
    onUpdateSettings({ ...settings, profile: { ...settings.profile, [field]: value } });
  };

  const updateAI = (field: string, value: string) => {
    onUpdateSettings({ ...settings, ai: { ...settings.ai, [field]: value } });
  };

  const updatePrompt = (field: string, value: string) => {
    onUpdateSettings({ ...settings, prompts: { ...settings.prompts, [field]: value } });
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
        if (file.size > 5 * 1024 * 1024) {
            alert("File size too large. Please upload an image under 5MB.");
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            const base64String = reader.result as string;
            updateProfile('avatarUrl', base64String);
        };
        reader.readAsDataURL(file);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-textMain">Settings</h2>
          <p className="text-textMuted">Manage your profile, AI configuration, and system behaviors.</p>
        </div>
        <Button onClick={handleSave} icon={<Save size={18} />} disabled={saving} className={isSaved ? 'bg-green-600 hover:bg-green-700' : ''}>
          {saving ? 'Saving...' : isSaved ? 'Saved!' : 'Save Changes'}
        </Button>
      </div>

      {/* 1. User Profile & Language */}
      <Card title="Profile & Preferences" subtitle="Customize your identity and interface language." action={<User className="text-textMuted" size={20} />}>
        <div className="flex flex-col md:flex-row gap-8">
            {/* Avatar Section */}
            <div className="flex flex-col items-center gap-3 shrink-0">
                <div 
                    className="relative w-24 h-24 rounded-full bg-surfaceHighlight border-2 border-dashed border-zinc-700 flex items-center justify-center cursor-pointer hover:border-primary transition-colors overflow-hidden group"
                    onClick={handleAvatarClick}
                >
                    {settings.profile.avatarUrl ? (
                        <img src={settings.profile.avatarUrl} alt="Avatar" className="w-full h-full object-cover" />
                    ) : (
                        <User className="text-zinc-600 group-hover:text-primary transition-colors" size={32} />
                    )}
                    
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Camera className="text-white" size={24} />
                    </div>
                </div>
                <button onClick={handleAvatarClick} className="text-xs text-primary hover:text-primaryHover font-medium flex items-center gap-1">
                    <Upload size={12} /> Change Avatar
                </button>
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    accept="image/png, image/jpeg, image/jpg"
                    onChange={handleFileChange}
                />
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
            <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Display Name</label>
                <input 
                type="text" 
                value={settings.profile.name}
                onChange={(e) => updateProfile('name', e.target.value)}
                className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none" 
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Role / Job Title</label>
                <input 
                type="text" 
                value={settings.profile.role}
                onChange={(e) => updateProfile('role', e.target.value)}
                className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none" 
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Interface Language</label>
                <select 
                value={settings.profile.language}
                onChange={(e) => updateProfile('language', e.target.value)}
                className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 appearance-none focus:ring-1 focus:ring-primary focus:outline-none"
                >
                <option value="en">English</option>
                <option value="zh-TW">繁體中文 (Traditional Chinese)</option>
                <option value="zh-CN">简体中文 (Simplified Chinese)</option>
                <option value="jp">日本語 (Japanese)</option>
                </select>
            </div>
            </div>
        </div>
      </Card>

      {/* 2. AI Provider Settings */}
      <Card title="AI Provider Configuration" subtitle="Configure connection to Ollama or other LLM providers." action={<Cpu className="text-textMuted" size={20} />}>
        <div className="space-y-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-start gap-3">
             <AlertCircle className="text-blue-400 shrink-0 mt-0.5" size={16} />
             <p className="text-xs text-blue-200">
               <strong>Security Note:</strong> API Keys are stored locally in your browser's LocalStorage. They are never sent to our servers, only directly to the AI provider.
             </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Provider</label>
                <select 
                  value={settings.ai.provider}
                  onChange={(e) => updateAI('provider', e.target.value)}
                  className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none"
                >
                  <option value="ollama">Ollama (Local/Cloud)</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                </select>
             </div>
             <div>
                <label className="block text-xs font-medium text-textMuted mb-1.5">Model Name</label>
                <input 
                  type="text" 
                  value={settings.ai.model}
                  onChange={(e) => updateAI('model', e.target.value)}
                  placeholder="e.g. llama3, gpt-4o"
                  className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none" 
                />
             </div>
             <div className="md:col-span-2">
                <label className="block text-xs font-medium text-textMuted mb-1.5">API Key / Base URL</label>
                <div className="relative">
                  <input 
                    type={showKey ? "text" : "password"} 
                    value={settings.ai.apiKey}
                    onChange={(e) => updateAI('apiKey', e.target.value)}
                    placeholder={settings.ai.provider === 'ollama' ? 'http://localhost:11434' : 'sk-...'}
                    className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg pl-3 pr-10 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none font-mono" 
                  />
                  <button 
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-3 top-2.5 text-textMuted hover:text-textMain"
                  >
                    {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                <p className="text-[10px] text-textMuted mt-1">
                  For Ollama, enter the Base URL (default: http://localhost:11434). For others, enter the API Key.
                </p>
             </div>
          </div>
        </div>
      </Card>

      {/* 3. System Prompts Configuration */}
      <Card title="AI Prompts Configuration" subtitle="Fine-tune the personality and instructions for the AI models." action={<Terminal className="text-textMuted" size={20} />}>
        <div className="space-y-6">
          
          {/* Global Prompt */}
          <div>
            <div className="flex justify-between mb-1.5">
               <label className="block text-xs font-medium text-textMain">Global System Prompt</label>
               <span className="text-[10px] text-textMuted bg-zinc-800 px-2 py-0.5 rounded">Applied to all contexts</span>
            </div>
            <textarea 
              rows={3}
              value={settings.prompts.global}
              onChange={(e) => updatePrompt('global', e.target.value)}
              className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none resize-y"
            />
          </div>

          {/* Interview Suggestions Prompt */}
          <div>
            <div className="flex justify-between mb-1.5">
               <label className="block text-xs font-medium text-textMain">Interview Suggestions Prompt</label>
               <span className="text-[10px] text-textMuted bg-zinc-800 px-2 py-0.5 rounded">Used in Analysis view</span>
            </div>
            <textarea 
              rows={3}
              value={settings.prompts.interviewSuggestions}
              onChange={(e) => updatePrompt('interviewSuggestions', e.target.value)}
              className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none resize-y"
            />
          </div>

          {/* Coach Chat Prompt */}
          <div>
            <div className="flex justify-between mb-1.5">
               <label className="block text-xs font-medium text-textMain">Coach Chat Prompt</label>
               <span className="text-[10px] text-textMuted bg-zinc-800 px-2 py-0.5 rounded">Used in Chat interface</span>
            </div>
            <textarea 
              rows={3}
              value={settings.prompts.coachChat}
              onChange={(e) => updatePrompt('coachChat', e.target.value)}
              className="w-full bg-surfaceHighlight border border-border text-textMain text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none resize-y"
            />
          </div>
          
        </div>
      </Card>

    </div>
  );
};