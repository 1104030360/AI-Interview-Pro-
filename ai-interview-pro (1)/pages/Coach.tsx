import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { apiClient } from '../services/api';
import { useToast } from '../components/ui/Toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const Coach: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load suggestions on mount
  useEffect(() => {
    loadSuggestions();
  }, []);

  async function loadSuggestions() {
    try {
      const response = await apiClient.getCoachSuggestions();
      setSuggestions(response.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions', error);
      // Silent fail for suggestions - not critical
    }
  }

  async function handleSendMessage() {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await apiClient.sendCoachMessage(inputValue, {
        conversationId: conversationId || undefined
      });

      setConversationId(response.conversationId);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (response.suggestions && response.suggestions.length > 0) {
        setSuggestions(response.suggestions);
      }
    } catch (error: unknown) {
      console.error('Failed to send message', error);

      // Handle structured error response from API
      let errorMessage = 'Failed to send message. Please try again.';

      if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response?: { data?: { error?: { code?: string; message?: string } } } }).response;
        const errorData = response?.data?.error;

        if (errorData) {
          switch (errorData.code) {
            case 'AI_PROVIDER_NOT_CONFIGURED':
              errorMessage = 'AI provider not configured. Please set up your API key in Settings.';
              break;
            case 'AI_AUTH_ERROR':
              errorMessage = 'API key authentication failed. Please check your API key in Settings.';
              break;
            case 'AI_TIMEOUT':
              errorMessage = 'The AI service timed out. Please try again.';
              break;
            case 'AI_RATE_LIMIT':
              errorMessage = 'Rate limit exceeded. Please wait a moment before trying again.';
              break;
            case 'AI_CONNECTION_ERROR':
              errorMessage = 'Unable to connect to AI service. Please check your network.';
              break;
            default:
              errorMessage = errorData.message || errorMessage;
          }
        }
      }

      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  function handleSuggestionClick(suggestion: string) {
    setInputValue(suggestion);
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-textMain flex items-center gap-2">
        <Bot className="text-primary" /> AI Coach
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-surface border border-border rounded-xl overflow-hidden flex flex-col h-[500px]">
            {/* Header */}
            <div className="p-4 border-b border-border bg-surfaceHighlight/30 flex justify-between items-center">
              <span className="text-sm font-medium">Coach Chat</span>
              <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">Online</span>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {messages.length === 0 && (
                <div className="text-center text-textMuted py-12">
                  <Bot className="mx-auto mb-4 text-zinc-600" size={48} />
                  <p>Start a conversation with your AI coach!</p>
                </div>
              )}

              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'bg-primary/20 text-primary' : 'bg-zinc-700'}`}>
                    {msg.role === 'assistant' ? <Bot size={16}/> : <span className="text-xs">ME</span>}
                  </div>
                  <div className={`p-3 rounded-lg text-sm max-w-[80%] ${msg.role === 'assistant' ? 'bg-surfaceHighlight rounded-tl-none text-textMuted' : 'bg-primary/10 border border-primary/20 rounded-tr-none text-textMain'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                    <Bot size={16}/>
                  </div>
                  <div className="bg-surfaceHighlight p-3 rounded-lg rounded-tl-none text-sm text-textMuted">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-textMuted rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                      <div className="w-2 h-2 bg-textMuted rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                      <div className="w-2 h-2 bg-textMuted rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border">
              <div className="relative">
                <input
                  className="w-full bg-zinc-950 border border-border rounded-lg pl-4 pr-10 py-3 text-sm focus:outline-none focus:border-primary text-textMain"
                  placeholder="Ask the coach..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={loading}
                />
                <button
                  className="absolute right-2 top-2 p-1 text-primary hover:text-primaryHover disabled:opacity-50"
                  onClick={handleSendMessage}
                  disabled={loading || !inputValue.trim()}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card title="Quick Suggestions">
            <div className="space-y-2">
              {suggestions.map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left p-3 rounded border border-dashed border-zinc-700 hover:border-primary/50 transition-colors text-sm text-textMuted hover:text-textMain"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
