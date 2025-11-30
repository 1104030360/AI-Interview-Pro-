import React, { useState, useEffect } from 'react';
import { ArrowRight, Video, Target, ShieldCheck, Zap, Activity, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Spinner } from '../components/ui/Spinner';
import { useToast } from '../components/ui/Toast';
import { Page } from '../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
  AreaChart
} from 'recharts';
import { apiClient, PerformanceTrendResponse, SummaryResponse } from '../services/api';

// Mock Data Generation for Trend Chart (fallback when not authenticated)
const generateTrendData = (days: number, baseValue: number) => {
  const data = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: Math.min(100, Math.max(0, baseValue + (Math.random() * 20 - 10))),
      value2: Math.min(100, Math.max(0, baseValue - 10 + (Math.random() * 20 - 10)))
    });
  }
  return data;
};

const MOCK_TREND_DATA = {
  '1W': generateTrendData(7, 80),
  '1M': generateTrendData(30, 82),
  '3M': generateTrendData(90, 85),
  'All': generateTrendData(120, 88),
};

const MOCK_SUMMARY = {
  sessionsCompleted: 12,
  avgClarityScore: 84,
  practiceTimeHours: 5,
  currentLevel: 'A-'
};

type TimeRange = '1W' | '1M' | '3M' | 'All';
type MetricType = 'Tone' | 'Professionalism' | 'Technical';

export const Overview: React.FC<{ onNavigate: (page: Page) => void }> = ({ onNavigate }) => {
  const toast = useToast();
  const [timeRange, setTimeRange] = useState<TimeRange>('1W');
  const [metric, setMetric] = useState<MetricType>('Professionalism');
  const [trendData, setTrendData] = useState<Array<{date: string; value: number}>>(MOCK_TREND_DATA['1W']);
  const [summary, setSummary] = useState(MOCK_SUMMARY);
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    setIsAuthenticated(apiClient.isAuthenticated());
  }, []);

  // Load analytics data when authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      // Use mock data when not authenticated
      setTrendData(MOCK_TREND_DATA[timeRange]);
      setSummary(MOCK_SUMMARY);
      return;
    }

    // Load real data
    const loadAnalytics = async () => {
      setIsLoading(true);
      try {
        // Load trend and summary in parallel
        const [trendRes, summaryRes] = await Promise.all([
          apiClient.getPerformanceTrend(timeRange, metric),
          apiClient.getSummary()
        ]);

        setTrendData(trendRes.data);
        setSummary(summaryRes);
      } catch (error) {
        console.error('Failed to load analytics:', error);
        toast.warning('Data Unavailable', 'Using sample data. Login to see your real performance.');
        // Fallback to mock data on error
        setTrendData(MOCK_TREND_DATA[timeRange]);
        setSummary(MOCK_SUMMARY);
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalytics();
  }, [isAuthenticated, timeRange, metric]);

  const currentData = trendData;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-zinc-900 to-background border border-zinc-800 p-10 md:p-16 text-center md:text-left">
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/5 to-transparent pointer-events-none" />
        
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-6 border border-primary/20">
            <Zap size={12} />
            <span>AI Model 4.0 Active</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-textMain mb-4 tracking-tight">
            Master your next <br/>
            <span className="text-primary">Technical Interview</span>
          </h1>
          <p className="text-lg text-textMuted mb-8 leading-relaxed">
            Advanced behavioral analysis and real-time feedback for engineering professionals. 
            Identify blind spots in your communication before your high-stakes interview.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button size="lg" onClick={() => onNavigate(Page.Record)} icon={<Video size={18} />}>
              Start Assessment
            </Button>
            <Button size="lg" variant="outline" onClick={() => onNavigate(Page.History)}>
              View History
            </Button>
          </div>
        </div>
        
        {/* Abstract decorative element simulating 3D */}
        <div className="hidden md:block absolute top-1/2 -right-12 transform -translate-y-1/2 opacity-30">
          <svg width="400" height="400" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <path fill="#06b6d4" d="M45.7,-51.3C59.3,-39.7,70.3,-24.7,73.5,-8.4C76.6,8,71.9,25.7,61.5,40.1C51.1,54.5,35,65.7,17.8,68.9C0.6,72.1,-17.7,67.3,-33.8,56.6C-50,45.9,-63.9,29.3,-66.3,11.1C-68.7,-7.1,-59.6,-26.9,-47.6,-39.3C-35.7,-51.7,-20.9,-56.7,-5.3,-56.1C10.3,-55.5,20.7,-49.3,32.1,-63" transform="translate(100 100)" />
          </svg>
        </div>
      </div>

      {/* Trend Chart Section (New Request) */}
      <Card className="border border-border bg-surface/50 backdrop-blur-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
             <h3 className="text-lg font-semibold text-textMain flex items-center gap-2">
               <Activity size={20} className="text-primary" /> Performance Trend
             </h3>
             <p className="text-sm text-textMuted">Track your improvement over time across key metrics.</p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3">
             {/* Metric Selector */}
             <div className="bg-surfaceHighlight border border-border rounded-lg p-1 flex">
                {(['Tone', 'Professionalism', 'Technical'] as MetricType[]).map((m) => (
                  <button
                    key={m}
                    onClick={() => setMetric(m)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                      metric === m 
                      ? 'bg-primary text-white shadow-sm' 
                      : 'text-textMuted hover:text-textMain'
                    }`}
                  >
                    {m}
                  </button>
                ))}
             </div>
             
             {/* Time Range Selector */}
             <div className="bg-surfaceHighlight border border-border rounded-lg p-1 flex">
                {(['1W', '1M', '3M', 'All'] as TimeRange[]).map((range) => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                      timeRange === range
                      ? 'bg-zinc-700 text-textMain shadow-sm' 
                      : 'text-textMuted hover:text-textMain'
                    }`}
                  >
                    {range}
                  </button>
                ))}
             </div>
          </div>
        </div>

        <div className="h-[300px] w-full relative">
           {isLoading && (
             <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
               <Spinner size="lg" />
             </div>
           )}
           <ResponsiveContainer width="100%" height="100%">
             <AreaChart data={currentData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
               <defs>
                 <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                   <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                   <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                 </linearGradient>
               </defs>
               <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
               <XAxis 
                  dataKey="date" 
                  stroke="#71717a" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                  minTickGap={30}
               />
               <YAxis 
                  stroke="#71717a" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                  domain={[0, 100]} 
               />
               <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                  itemStyle={{ color: '#f4f4f5' }}
                  labelStyle={{ color: '#a1a1aa', marginBottom: '0.5rem' }}
               />
               <Area 
                  type="monotone" 
                  dataKey="value" 
                  name={metric}
                  stroke="#06b6d4" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorValue)" 
               />
             </AreaChart>
           </ResponsiveContainer>
        </div>
      </Card>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:border-primary/50 transition-colors group cursor-pointer">
          <div className="w-12 h-12 bg-zinc-900 rounded-lg flex items-center justify-center mb-4 border border-zinc-800 group-hover:border-primary/30">
            <Video className="text-textMain group-hover:text-primary transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-textMain mb-2">Dual-Camera Mode</h3>
          <p className="text-textMuted text-sm">Simulate real remote pair programming or system design interviews with split-screen analysis.</p>
        </Card>
        <Card className="hover:border-primary/50 transition-colors group cursor-pointer">
          <div className="w-12 h-12 bg-zinc-900 rounded-lg flex items-center justify-center mb-4 border border-zinc-800 group-hover:border-primary/30">
            <Target className="text-textMain group-hover:text-primary transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-textMain mb-2">Precision Metrics</h3>
          <p className="text-textMuted text-sm">Track clarity, confidence, and empathy scores. Get actionable insights on body language.</p>
        </Card>
        <Card className="hover:border-primary/50 transition-colors group cursor-pointer">
          <div className="w-12 h-12 bg-zinc-900 rounded-lg flex items-center justify-center mb-4 border border-zinc-800 group-hover:border-primary/30">
            <ShieldCheck className="text-textMain group-hover:text-primary transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-textMain mb-2">Role-Based Scenarios</h3>
          <p className="text-textMuted text-sm">Curated questions for Frontend, Backend, PM, and Data Science roles with difficulty tiers.</p>
        </Card>
      </div>

      {/* Simple Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-zinc-800 pt-8">
         <div>
            <p className="text-3xl font-bold text-textMain">{summary.sessionsCompleted}</p>
            <p className="text-xs text-textMuted uppercase tracking-wider mt-1">Sessions Completed</p>
         </div>
         <div>
            <p className="text-3xl font-bold text-textMain">{summary.avgClarityScore}%</p>
            <p className="text-xs text-textMuted uppercase tracking-wider mt-1">Avg. Clarity Score</p>
         </div>
         <div>
            <p className="text-3xl font-bold text-textMain">{summary.practiceTimeHours}h</p>
            <p className="text-xs text-textMuted uppercase tracking-wider mt-1">Practice Time</p>
         </div>
         <div>
            <p className="text-3xl font-bold text-textMain">{summary.currentLevel}</p>
            <p className="text-xs text-textMuted uppercase tracking-wider mt-1">Current Level</p>
         </div>
      </div>
    </div>
  );
};