import React, { useState, useEffect } from 'react';
import { Sparkles, Search, X, BookOpen, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useToast } from '../components/ui/Toast';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { apiClient } from '../services/api';
import { Page } from '../types';

interface Question {
  id: string;
  text: string;
  type: string;
  difficulty: string;
  role?: string;
}

interface QuestionBankProps {
  onNavigate: (page: Page, params?: any) => void;
}

export const QuestionBank: React.FC<QuestionBankProps> = ({ onNavigate }) => {
  const toast = useToast();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState<string>('');
  const [filterDifficulty, setFilterDifficulty] = useState<string>('');
  const [searchKeyword, setSearchKeyword] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // AI Generate Form
  const [generateForm, setGenerateForm] = useState({
    role: 'Software Engineer',
    difficulty: 'Mid',
    type: 'Technical',
    count: 5
  });

  useEffect(() => {
    loadQuestions();
  }, [currentPage, filterType, filterDifficulty]);

  async function loadQuestions() {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getQuestions({
        page: currentPage,
        limit: 12,
        type: filterType || undefined,
        difficulty: filterDifficulty || undefined
      });

      setQuestions(response.items);
      setTotalPages(response.pagination.totalPages);
    } catch (err) {
      console.error('Failed to load questions', err);
      setError('Failed to load questions. Please try again.');
      setQuestions([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateQuestions() {
    setGenerating(true);
    try {
      await apiClient.generateQuestions(generateForm);
      setShowGenerateModal(false);
      toast.success('Questions Generated', `Successfully generated ${generateForm.count} new questions.`);
      loadQuestions(); // Reload list
    } catch (err) {
      console.error('Failed to generate questions', err);
      toast.error('Generation Failed', 'Failed to generate questions. Please check your AI settings and try again.');
    } finally {
      setGenerating(false);
    }
  }

  function handlePracticeQuestion(question: Question) {
    onNavigate(Page.Record, { selectedQuestion: question });
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-textMain">Question Bank</h2>
        <Button
          icon={<Sparkles size={16} />}
          onClick={() => setShowGenerateModal(true)}
        >
          Generate New Questions
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-textMuted" size={16} />
          <input
            type="text"
            placeholder="Search questions..."
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain"
        >
          <option value="">All Types</option>
          <option value="Behavioral">Behavioral</option>
          <option value="Technical">Technical</option>
          <option value="System Design">System Design</option>
        </select>

        <select
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
          className="px-4 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain"
        >
          <option value="">All Levels</option>
          <option value="Junior">Junior</option>
          <option value="Mid">Mid</option>
          <option value="Senior">Senior</option>
        </select>
      </div>

      {/* Questions Grid */}
      {loading ? (
        <LoadingState message="Loading questions..." />
      ) : error ? (
        <ErrorState
          title="Failed to Load Questions"
          message={error}
          onRetry={loadQuestions}
        />
      ) : questions.length === 0 ? (
        <EmptyState
          icon={<BookOpen size={48} />}
          title="No Questions Yet"
          description="Generate some interview questions to get started with your practice."
          action={{
            label: "Generate Questions",
            onClick: () => setShowGenerateModal(true)
          }}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {questions.map((question) => (
              <Card
                key={question.id}
                className="hover:border-primary/40 transition-colors cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-3">
                  <span className={`text-[10px] px-2 py-0.5 rounded border ${
                    question.type === 'System Design' ? 'border-purple-500/30 text-purple-400' :
                    question.type === 'Technical' ? 'border-blue-500/30 text-blue-400' :
                    'border-green-500/30 text-green-400'
                  }`}>
                    {question.type}
                  </span>
                  <span className="text-[10px] text-textMuted">{question.difficulty}</span>
                </div>
                <h3 className="text-textMain font-medium mb-4 line-clamp-2 group-hover:text-primary transition-colors">
                  {question.text}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-auto"
                  onClick={() => handlePracticeQuestion(question)}
                >
                  Practice This
                </Button>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
              >
                Previous
              </Button>
              <span className="px-4 py-2 text-sm text-textMuted">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}

      {/* Generate Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-surface border border-border rounded-xl p-6 max-w-md w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-textMain">Generate Questions with AI</h3>
              <button onClick={() => setShowGenerateModal(false)} className="text-textMuted hover:text-textMain">
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-textMuted mb-1">Role</label>
                <select
                  value={generateForm.role}
                  onChange={(e) => setGenerateForm({...generateForm, role: e.target.value})}
                  className="w-full px-3 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain"
                >
                  <option>Software Engineer</option>
                  <option>Product Manager</option>
                  <option>Data Scientist</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-textMuted mb-1">Difficulty</label>
                <select
                  value={generateForm.difficulty}
                  onChange={(e) => setGenerateForm({...generateForm, difficulty: e.target.value})}
                  className="w-full px-3 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain"
                >
                  <option>Junior</option>
                  <option>Mid</option>
                  <option>Senior</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-textMuted mb-1">Type</label>
                <select
                  value={generateForm.type}
                  onChange={(e) => setGenerateForm({...generateForm, type: e.target.value})}
                  className="w-full px-3 py-2 bg-surfaceHighlight border border-border rounded-lg text-sm text-textMain"
                >
                  <option>Behavioral</option>
                  <option>Technical</option>
                  <option>System Design</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-textMuted mb-1">Count: {generateForm.count}</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={generateForm.count}
                  onChange={(e) => setGenerateForm({...generateForm, count: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowGenerateModal(false)}
                disabled={generating}
              >
                Cancel
              </Button>
              <Button
                className="flex-1"
                onClick={handleGenerateQuestions}
                disabled={generating}
              >
                {generating ? 'Generating...' : 'Generate'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
