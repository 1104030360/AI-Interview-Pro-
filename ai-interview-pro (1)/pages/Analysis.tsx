import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar
} from 'recharts';
import { ArrowUpRight, ArrowDownRight, Download, Share2, User, Users } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { VideoPlayer } from '../components/VideoPlayer';
import { apiClient } from '../services/api';

interface AnalysisProps {
  interviewId?: string;
}

export const Analysis: React.FC<AnalysisProps> = ({ interviewId }) => {
  const toast = useToast();
  const [viewMode, setViewMode] = useState<'Candidate' | 'Interviewer'>('Candidate');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [analysisStatus, setAnalysisStatus] = useState<{
    status: string;
    progress: number;
    message: string;
  } | null>(null);

  // Default mock data for fallback
  const defaultDataHistory = [
    { name: 'Session 1', score: 65 },
    { name: 'Session 2', score: 72 },
    { name: 'Session 3', score: 68 },
    { name: 'Session 4', score: 85 },
    { name: 'Session 5', score: 82 },
    { name: 'Current', score: 88 },
  ];

  const defaultDataSkills = [
    { subject: 'Confidence', A: 88, fullMark: 100 },
    { subject: 'Clarity', A: 75, fullMark: 100 },
    { subject: 'Tech Depth', A: 92, fullMark: 100 },
    { subject: 'Body Lang', A: 65, fullMark: 100 },
    { subject: 'Empathy', A: 85, fullMark: 100 },
    { subject: 'Structure', A: 70, fullMark: 100 },
  ];

  const defaultDataComparison = [
    { name: 'Q1', you: 80, avg: 70 },
    { name: 'Q2', you: 65, avg: 75 },
    { name: 'Q3', you: 90, avg: 72 },
    { name: 'Q4', you: 85, avg: 78 },
  ];

  useEffect(() => {
    if (interviewId) {
      checkAnalysisStatus();
    } else {
      setLoading(false);
    }
  }, [interviewId]);

  async function checkAnalysisStatus() {
    console.log('📊 [Analysis] Checking analysis status...');
    setLoading(true);
    setError(null);

    try {
      // Check status first
      const status = await apiClient.getAnalysisStatus(interviewId!);
      console.log('📊 [Analysis] Status:', status);

      setAnalysisStatus(status);

      if (status.status === 'completed') {
        // Analysis done, load report
        console.log('✅ [Analysis] Analysis completed, loading report...');
        await loadAnalysisReport();
      } else if (status.status === 'pending' || status.status === 'processing') {
        // Still processing, poll again after 3 seconds
        console.log(`⏳ [Analysis] Status: ${status.status}, polling again in 3s...`);
        setTimeout(checkAnalysisStatus, 3000);
      } else if (status.status === 'failed') {
        setError('Analysis failed. Please try recording again.');
        setLoading(false);
      } else {
        setError(`Analysis not started yet (status: ${status.status})`);
        setLoading(false);
      }
    } catch (err) {
      console.error('❌ [Analysis] Failed to check status:', err);
      setError('Failed to check analysis status.');
      setLoading(false);
    }
  }

  async function loadAnalysisReport() {
    try {
      const data = await apiClient.getAnalysisReport(interviewId!);
      console.log('✅ [Analysis] Report loaded:', data);
      setAnalysisData(data);
      setLoading(false);
    } catch (err) {
      console.error('❌ [Analysis] Failed to load report:', err);
      setError('Failed to load analysis report.');
      setLoading(false);
    }
  }

  async function handleExportReport() {
    if (!interviewId) {
      toast.warning('Export Unavailable', 'No interview ID available for export.');
      return;
    }

    try {
      const blob = await apiClient.exportAnalysis(interviewId, 'pdf');

      // Download PDF
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis-${interviewId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Export Complete', 'Your report has been downloaded.');
    } catch (error) {
      console.error('Failed to export report', error);
      toast.error('Export Failed', 'Could not export the report. Please try again.');
    }
  }

  async function handleShare() {
    if (!interviewId) {
      toast.warning('Share Unavailable', 'No interview ID available for sharing.');
      return;
    }

    const shareUrl = `${window.location.origin}/analysis/${interviewId}`;

    try {
      if (navigator.share) {
        await navigator.share({
          title: 'Interview Analysis Report',
          text: 'Check out my interview analysis!',
          url: shareUrl
        });
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(shareUrl);
        toast.success('Link Copied', 'The share link has been copied to your clipboard.');
      }
    } catch (error) {
      console.error('Failed to share', error);
      toast.error('Share Failed', 'Could not share the report.');
    }
  }

  // Transform backend data to frontend chart format
  // Map emotion timeline to performance history chart
  const dataHistory = analysisData?.emotionData?.emotion_timeline
    ? analysisData.emotionData.emotion_timeline
        .filter((_: any, i: number) => i % 3 === 0) // Sample every 3rd point for readability
        .slice(0, 10) // Limit to 10 points
        .map((point: any, index: number) => ({
          name: `${Math.round(point.timestamp)}s`,
          score: point.emotionCategory === 'positive' ? 85 :
                 point.emotionCategory === 'neutral' ? 65 : 45,
          emotion: point.emotion
        }))
    : defaultDataHistory;

  // Map score fields to radar chart format
  const dataSkills = analysisData ? [
    { subject: 'Confidence', A: analysisData.confidenceScore || 0, fullMark: 100 },
    { subject: 'Clarity', A: analysisData.clarityScore || 0, fullMark: 100 },
    { subject: 'Tech Depth', A: analysisData.technicalScore || 0, fullMark: 100 },
    { subject: 'Empathy', A: analysisData.empathyScore || 0, fullMark: 100 },
    { subject: 'Overall', A: analysisData.overallScore || 0, fullMark: 100 },
  ] : defaultDataSkills;

  // Map emotion stats to comparison chart (you vs average)
  const dataComparison = analysisData?.emotionData?.emotion_stats ? [
    { name: 'Positive', you: Math.round(analysisData.emotionData.emotion_stats.positive_percentage * 100), avg: 50 },
    { name: 'Neutral', you: Math.round(analysisData.emotionData.emotion_stats.neutral_percentage * 100), avg: 35 },
    { name: 'Negative', you: Math.round(analysisData.emotionData.emotion_stats.negative_percentage * 100), avg: 15 },
  ] : defaultDataComparison;

  const overallScore = analysisData?.overallScore || 88;
  const suggestions = analysisData?.suggestions || [];

const CustomGauge = ({ score }: { score: number }) => {
    const radius = 80;
    const stroke = 12;
    const normalizedRadius = radius - stroke * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (score / 100) * circumference;
    // semi-circle calculation usually different, but full circle looks modern too
    
    return (
        <div className="relative flex items-center justify-center w-48 h-48 mx-auto">
            <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
                <circle
                    stroke="#27272a"
                    strokeWidth={stroke}
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                <circle
                    stroke="#06b6d4"
                    strokeWidth={stroke}
                    strokeDasharray={circumference + ' ' + circumference}
                    style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease-in-out' }}
                    strokeLinecap="round"
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-textMain">{score}</span>
                <span className="text-sm text-textMuted uppercase tracking-wider">Overall</span>
            </div>
        </div>
    )
}

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center max-w-md">
                    <LoadingState
                        title={analysisStatus?.status === 'processing' ? 'Analyzing Your Interview' : 'Loading Analysis'}
                        description={analysisStatus?.message || 'Please wait while we process your interview...'}
                    />

                    {analysisStatus && (
                        <div className="mt-4 max-w-xs mx-auto">
                            <div className="w-full bg-surfaceHighlight rounded-full h-2 mb-2">
                                <div
                                    className="bg-primary h-2 rounded-full transition-all duration-500"
                                    style={{ width: `${analysisStatus.progress}%` }}
                                />
                            </div>
                            <p className="text-xs text-textMuted">
                                {analysisStatus.progress}% complete
                            </p>
                        </div>
                    )}

                    <p className="text-xs text-textMuted mt-6">
                        This may take 1-2 minutes depending on video length
                    </p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <ErrorState
                title="Analysis Unavailable"
                message={error}
                onRetry={checkAnalysisStatus}
            />
        );
    }

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-10">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-xs font-medium">
                            {analysisData?.status === 'completed' ? 'Analysis Complete' : 'Analysis Pending'}
                        </span>
                        <span className="text-textMuted text-xs">
                            {analysisData?.createdAt
                                ? new Date(analysisData.createdAt).toLocaleString()
                                : 'Processing...'}
                        </span>
                    </div>
                    <h2 className="text-2xl font-bold text-textMain">Interview Analysis Report</h2>
                    <p className="text-textMuted text-sm mt-1">
                        Overall Score: {Math.round(overallScore)}% | Status: {analysisData?.status || 'unknown'}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                     <Button variant="outline" size="sm" icon={<Share2 size={16}/>} onClick={handleShare}>Share</Button>
                     <Button variant="outline" size="sm" icon={<Download size={16}/>} onClick={handleExportReport}>Report</Button>
                </div>
            </div>

            {/* Tabs for View Mode */}
            <div className="border-b border-border">
                <div className="flex gap-6">
                    <button 
                        onClick={() => setViewMode('Candidate')}
                        className={`pb-3 text-sm font-medium border-b-2 transition-colors ${viewMode === 'Candidate' ? 'border-primary text-primary' : 'border-transparent text-textMuted hover:text-textMain'}`}
                    >
                        Candidate Analysis
                    </button>
                    <button 
                         onClick={() => setViewMode('Interviewer')}
                         className={`pb-3 text-sm font-medium border-b-2 transition-colors ${viewMode === 'Interviewer' ? 'border-primary text-primary' : 'border-transparent text-textMuted hover:text-textMain'}`}
                    >
                        Interviewer Analysis
                    </button>
                </div>
            </div>

            {/* Top Stats Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-1 flex flex-col justify-center">
                    <CustomGauge score={overallScore} />
                    <div className="mt-6 text-center">
                        <p className="text-textMuted text-sm">
                            {overallScore >= 80 ? 'Excellent Performance!' :
                             overallScore >= 60 ? 'Good Progress' : 'Keep Practicing'}
                        </p>
                        <div className="mt-4 flex justify-center gap-4">
                             <div className="text-center">
                                <div className="text-lg font-semibold text-textMain">
                                    {analysisData?.technicalScore ? Math.round(analysisData.technicalScore) : '--'}%
                                </div>
                                <div className="text-[10px] text-textMuted uppercase">Technical</div>
                             </div>
                             <div className="w-px bg-border h-8" />
                             <div className="text-center">
                                <div className="text-lg font-semibold text-textMain">
                                    {analysisData?.empathyScore ? Math.round(analysisData.empathyScore) : '--'}%
                                </div>
                                <div className="text-[10px] text-textMuted uppercase">Empathy</div>
                             </div>
                        </div>
                    </div>
                </Card>

                <Card title="Radar Skills Analysis" className="lg:col-span-1">
                     <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={dataSkills}>
                                <PolarGrid stroke="#3f3f46" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#a1a1aa', fontSize: 10 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                <Radar
                                    name="Candidate"
                                    dataKey="A"
                                    stroke="#06b6d4"
                                    fill="#06b6d4"
                                    fillOpacity={0.3}
                                />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                    itemStyle={{ color: '#f4f4f5' }}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                     </div>
                </Card>

                <Card title="Key Insights" className="lg:col-span-1">
                    <div className="space-y-4">
                        <div>
                            <h4 className="text-sm font-medium text-cyan-400 mb-2 flex items-center gap-2">
                                <ArrowUpRight size={16} /> AI Suggestions
                            </h4>
                            <ul className="space-y-2">
                                {suggestions.length > 0 ? (
                                    suggestions.map((suggestion: string, index: number) => (
                                        <li key={index} className="text-sm text-textMuted pl-4 border-l-2 border-cyan-400/20">
                                            {suggestion}
                                        </li>
                                    ))
                                ) : (
                                    <>
                                        <li className="text-sm text-textMuted pl-4 border-l-2 border-cyan-400/20">No suggestions available yet.</li>
                                    </>
                                )}
                            </ul>
                        </div>
                        {analysisData?.emotionData?.emotion_stats && (
                            <div>
                                <h4 className="text-sm font-medium text-amber-400 mb-2 flex items-center gap-2">
                                    <ArrowDownRight size={16} /> Emotion Summary
                                </h4>
                                <ul className="space-y-2">
                                    <li className="text-sm text-textMuted pl-4 border-l-2 border-amber-400/20">
                                        Positive emotions: {Math.round(analysisData.emotionData.emotion_stats.positive_percentage * 100)}%
                                    </li>
                                    <li className="text-sm text-textMuted pl-4 border-l-2 border-amber-400/20">
                                        Neutral emotions: {Math.round(analysisData.emotionData.emotion_stats.neutral_percentage * 100)}%
                                    </li>
                                    <li className="text-sm text-textMuted pl-4 border-l-2 border-amber-400/20">
                                        Frames analyzed: {analysisData.emotionData.total_frames_analyzed || 0}
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>
                </Card>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Performance History">
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={dataHistory}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                <XAxis dataKey="name" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                    itemStyle={{ color: '#06b6d4' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="score"
                                    stroke="#06b6d4"
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#09090b', strokeWidth: 2 }}
                                    activeDot={{ r: 6, fill: '#06b6d4' }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card title="Answer Structure vs Benchmark">
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={dataComparison}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                <XAxis dataKey="name" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                     cursor={{fill: '#27272a'}}
                                     contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                />
                                <Bar dataKey="you" fill="#06b6d4" radius={[4, 4, 0, 0]} name="You" />
                                <Bar dataKey="avg" fill="#3f3f46" radius={[4, 4, 0, 0]} name="Avg" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            {/* Video Playback Section */}
            <div className="mt-6">
                <h3 className="text-lg font-semibold text-textMain mb-4">Interview Recording</h3>
                <VideoPlayer
                    cam0={analysisData?.videos?.cam0}
                    cam1={analysisData?.videos?.cam1}
                    onTimeUpdate={(time) => {
                        // Could be used to sync with emotion timeline in the future
                        console.log('Video time:', time);
                    }}
                />
            </div>
        </div>
    );
};