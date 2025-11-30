import React, { useState, useEffect } from 'react';
import { Search, Filter, PlayCircle, Eye } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { apiClient } from '../services/api';

export const History: React.FC = () => {
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    loadInterviews();
  }, [currentPage, searchKeyword]);

  async function loadInterviews() {
    setLoading(true);
    try {
      const response = await apiClient.getInterviews({
        page: currentPage,
        limit: 10,
        keyword: searchKeyword || undefined,
      });
      setHistoryData(response.items);
    } catch (error) {
      console.error('Failed to load interviews', error);
      // Fallback to empty array on error
      setHistoryData([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(interviewId: string) {
    if (!confirm('Are you sure you want to delete this interview?')) return;

    try {
      await apiClient.deleteInterview(interviewId);
      loadInterviews();
    } catch (error) {
      console.error('Failed to delete interview', error);
      alert('Failed to delete interview. Please try again.');
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-end">
            <h2 className="text-2xl font-bold text-textMain">Archive</h2>
            <div className="flex gap-3">
                 <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-textMuted" size={16} />
                    <input
                        type="text"
                        placeholder="Search sessions..."
                        value={searchKeyword}
                        onChange={(e) => setSearchKeyword(e.target.value)}
                        className="pl-10 pr-4 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain focus:outline-none focus:ring-1 focus:ring-primary w-64"
                    />
                 </div>
                 <Button variant="secondary" icon={<Filter size={16} />}>Filters</Button>
            </div>
        </div>

        <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-border bg-surfaceHighlight/30">
                            <th className="px-6 py-4 font-medium text-textMuted">Date</th>
                            <th className="px-6 py-4 font-medium text-textMuted">Scenario</th>
                            <th className="px-6 py-4 font-medium text-textMuted">Mode</th>
                            <th className="px-6 py-4 font-medium text-textMuted">Duration</th>
                            <th className="px-6 py-4 font-medium text-textMuted">Score</th>
                            <th className="px-6 py-4 font-medium text-textMuted text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                        {loading ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-12 text-center text-textMuted">
                                    Loading interviews...
                                </td>
                            </tr>
                        ) : historyData.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-12 text-center text-textMuted">
                                    No interviews found
                                </td>
                            </tr>
                        ) : historyData.map((item) => (
                            <tr key={item.id} className="hover:bg-surfaceHighlight/30 transition-colors group">
                                <td className="px-6 py-4 text-textMuted">{item.date}</td>
                                <td className="px-6 py-4">
                                    <div className="text-textMain font-medium">{item.title}</div>
                                    <div className="text-xs text-textMuted">{item.type}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className="px-2 py-1 bg-zinc-800 rounded text-xs text-textMuted border border-zinc-700">
                                        {item.mode}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-textMuted">{item.duration}</td>
                                <td className="px-6 py-4">
                                    <span className={`font-bold ${item.score >= 80 ? 'text-green-400' : item.score >= 70 ? 'text-amber-400' : 'text-red-400'}`}>
                                        {item.score} <span className="text-xs text-textMuted font-normal">({item.grade})</span>
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="flex justify-end gap-2 opacity-60 group-hover:opacity-100 transition-opacity">
                                        <button className="p-2 hover:bg-surfaceHighlight rounded text-textMain" title="View Analysis">
                                            <Eye size={16} />
                                        </button>
                                        <button className="p-2 hover:bg-primary/20 hover:text-primary rounded text-textMain" title="Play Recording">
                                            <PlayCircle size={16} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </Card>
    </div>
  );
};