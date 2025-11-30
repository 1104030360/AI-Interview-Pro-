export enum Page {
  Overview = 'overview',
  Record = 'record',
  Analysis = 'analysis',
  History = 'history',
  Coach = 'coach',
  QuestionBank = 'question_bank',
  Settings = 'settings',
}

export interface InterviewRecord {
  id: string;
  date: string;
  scenario: string;
  mode: 'Single' | 'Dual';
  score: number;
  duration: string;
  tags: string[];
}

export interface Question {
  id: string;
  text: string;
  type: 'Behavioral' | 'Technical' | 'Situational';
  difficulty: 'Junior' | 'Mid' | 'Senior';
  role: string;
}

export interface AnalysisData {
  overallScore: number;
  clarity: number;
  confidence: number;
  knowledge: number;
  structure: number;
  empathy: number;
  history: { date: string; score: number }[];
}

// --- Settings & AI Types ---

export interface UserProfile {
  name: string;
  role: string;
  language: 'en' | 'zh-TW' | 'zh-CN' | 'jp';
  avatarUrl?: string; // Added avatarUrl
}

export interface AIConfig {
  provider: 'ollama' | 'openai' | 'anthropic';
  apiKey: string;
  model: string;
}

export interface SystemPrompts {
  global: string;
  interviewSuggestions: string;
  coachChat: string;
}

export interface AppSettings {
  profile: UserProfile;
  ai: AIConfig;
  prompts: SystemPrompts;
}

// --- System Capability Types ---

export interface SystemCapabilities {
  browserSupported: boolean;
  hasMicrophone: boolean;
  cameraCount: number;
  backendOnline: boolean;
}

// --- API Response Types ---

export interface PaginationMeta {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

// --- Interview Types ---

export interface Interview {
  id: string;
  userId: string;
  scenario: string;
  mode: 'Single' | 'Dual';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  duration: number;
  startedAt: string;
  completedAt?: string;
  candidateName?: string;
  interviewerName?: string;
  videoUrls?: string[];
  score?: number;
}

// --- Analysis Types ---

export interface PerformanceHistoryPoint {
  name: string;
  score: number;
  date?: string;
}

export interface SkillRadarPoint {
  subject: string;
  A: number;
  fullMark: number;
}

export interface BenchmarkPoint {
  name: string;
  you: number;
  avg: number;
}

export interface DetailedAnalysisData {
  overallScore: number;
  performanceHistory?: PerformanceHistoryPoint[];
  skillsRadar?: SkillRadarPoint[];
  benchmark?: BenchmarkPoint[];
  strengths?: string[];
  improvements?: string[];
  technicalScore?: number;
  behavioralScore?: number;
}

// --- Coach Types ---

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface CoachResponse {
  conversationId: string;
  reply: string;
  suggestions?: string[];
}

// --- Question Bank Types ---

export interface QuestionFilters {
  page?: number;
  limit?: number;
  type?: string;
  difficulty?: string;
  keyword?: string;
}

export interface GenerateQuestionsRequest {
  role: string;
  difficulty: string;
  type: string;
  count: number;
}
