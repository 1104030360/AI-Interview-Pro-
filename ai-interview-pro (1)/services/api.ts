/**
 * API Client Service
 *
 * Handles all backend API communications:
 * - Authentication (login, register, token refresh)
 * - Analytics (performance trends, summary statistics)
 * - Interviews management
 */

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

// Token management
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_ID_KEY = 'user_id';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  userId: string;
  email: string;
  name: string;
  accessToken: string;
  refreshToken: string;
}

export interface PerformanceTrendResponse {
  timeRange: string;
  metric: string;
  data: Array<{
    date: string;
    value: number;
  }>;
}

export interface SummaryResponse {
  sessionsCompleted: number;
  avgClarityScore: number;
  practiceTimeHours: number;
  currentLevel: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Helper: Get stored auth token
  private getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  // Helper: Set auth tokens
  private setTokens(accessToken: string, refreshToken: string, userId: string) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(USER_ID_KEY, userId);
  }

  // Helper: Clear auth tokens
  private clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ID_KEY);
  }

  // Helper: Authenticated fetch wrapper
  private async authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      headers,
    });

    // Handle 401 - token expired
    if (response.status === 401 && token) {
      // Try to refresh token
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        // Retry original request with new token
        headers['Authorization'] = `Bearer ${this.getToken()}`;
        return fetch(`${this.baseUrl}${url}`, { ...options, headers });
      } else {
        // Refresh failed, clear tokens
        this.clearTokens();
        throw new Error('Authentication expired. Please log in again.');
      }
    }

    return response;
  }

  // AUTH: Register new user
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Registration failed');
    }

    const result: AuthResponse = await response.json();
    this.setTokens(result.accessToken, result.refreshToken, result.userId);
    return result;
  }

  // AUTH: Login
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Login failed');
    }

    const result: AuthResponse = await response.json();
    this.setTokens(result.accessToken, result.refreshToken, result.userId);
    return result;
  }

  // AUTH: Refresh access token
  async refreshAccessToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) return false;

      const { accessToken } = await response.json();
      localStorage.setItem(TOKEN_KEY, accessToken);
      return true;
    } catch {
      return false;
    }
  }

  // AUTH: Get current user
  async getCurrentUser() {
    const response = await this.authFetch('/auth/me');

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return response.json();
  }

  // AUTH: Logout
  logout() {
    this.clearTokens();
  }

  // AUTH: Check if user is logged in
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // ANALYTICS: Get performance trend
  async getPerformanceTrend(
    timeRange: string = '1W',
    metric: string = 'Professionalism'
  ): Promise<PerformanceTrendResponse> {
    const response = await this.authFetch(
      `/analytics/performance-trend?timeRange=${timeRange}&metric=${metric}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch performance trend');
    }

    return response.json();
  }

  // ANALYTICS: Get user summary statistics
  async getSummary(): Promise<SummaryResponse> {
    const response = await this.authFetch('/analytics/summary');

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch summary');
    }

    return response.json();
  }

  // HEALTH: Check API health
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  // INTERVIEWS: Get interviews list with pagination and filters
  async getInterviews(params?: {
    page?: number;
    limit?: number;
    keyword?: string;
    mode?: 'Single' | 'Dual';
  }): Promise<{
    items: any[];
    pagination: {
      currentPage: number;
      totalPages: number;
      totalItems: number;
    };
  }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.keyword) queryParams.append('keyword', params.keyword);
    if (params?.mode) queryParams.append('mode', params.mode);

    const response = await this.authFetch(`/interviews?${queryParams}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch interviews');
    }

    return response.json();
  }

  // INTERVIEWS: Get single interview details
  async getInterviewDetail(interviewId: string): Promise<any> {
    const response = await this.authFetch(`/interviews/${interviewId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch interview details');
    }

    return response.json();
  }

  // INTERVIEWS: Create new interview session
  async createInterviewSession(data: {
    scenario: string;
    mode: 'Single' | 'Dual';
    plannedDuration: number;
    candidateName?: string;
  }): Promise<{ sessionId: string }> {
    // 映射前端參數到後端期望的格式
    const requestBody = {
      title: data.scenario,  // 後端期望 'title' 而不是 'scenario'
      status: 'pending'
    };

    const response = await this.authFetch('/interviews/sessions', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to create interview session');
    }

    return response.json();
  }

  // INTERVIEWS: Complete session and trigger analysis
  async completeSession(sessionId: string, data: {
    actualDuration: number;
    metadata?: any;
  }): Promise<{ interviewId: string }> {
    const response = await this.authFetch(`/interviews/sessions/${sessionId}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to complete session');
    }

    return response.json();
  }

  // INTERVIEWS: Delete interview record
  async deleteInterview(interviewId: string): Promise<void> {
    const response = await this.authFetch(`/interviews/${interviewId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to delete interview');
    }
  }

  // SETTINGS: Get user settings
  async getSettings(): Promise<any> {
    const response = await this.authFetch('/users/me/settings');

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch settings');
    }

    return response.json();
  }

  // SETTINGS: Update user settings
  async updateSettings(settings: any): Promise<any> {
    const response = await this.authFetch('/users/me/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to update settings');
    }

    return response.json();
  }

  // UPLOAD: Upload video file (simple, no progress)
  async uploadVideo(sessionId: string, camera: string, file: File | Blob): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sessionId', sessionId);
    formData.append('camera', camera);

    const token = this.getToken();
    const response = await fetch(`${this.baseUrl}/uploads/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type, let browser set it for FormData
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to upload video');
    }

    return response.json();
  }

  // UPLOAD: Upload video with progress tracking (XMLHttpRequest)
  async uploadVideoWithProgress(
    sessionId: string,
    camera: string,
    file: File | Blob,
    onProgress?: (percent: number) => void,
    onAbortRef?: (abort: () => void) => void
  ): Promise<{ url: string; taskId: string; analysisStatus: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sessionId', sessionId);
    formData.append('camera', camera);

    const token = this.getToken();

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Provide abort function to caller
      if (onAbortRef) {
        onAbortRef(() => xhr.abort());
      }

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch {
            reject(new Error('Invalid response format'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.error?.message || `Upload failed: ${xhr.status}`));
          } catch {
            reject(new Error(`Upload failed: ${xhr.status}`));
          }
        }
      };

      xhr.onerror = () => reject(new Error('Network error during upload'));
      xhr.ontimeout = () => reject(new Error('Upload timed out'));
      xhr.onabort = () => reject(new Error('Upload cancelled'));

      xhr.open('POST', `${this.baseUrl}/uploads/`);
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      xhr.timeout = 300000; // 5 minute timeout
      xhr.send(formData);
    });
  }

  // UPLOAD: Get video URL
  getVideoUrl(filename: string): string {
    return `${this.baseUrl}/uploads/${filename}`;
  }

  // ANALYSIS: Get analysis status
  async getAnalysisStatus(interviewId: string): Promise<{
    status: string;
    progress: number;
    message: string;
    startedAt?: string;
    completedAt?: string;
  }> {
    const response = await this.authFetch(`/analysis/${interviewId}/status`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch analysis status');
    }

    return response.json();
  }

  // ANALYSIS: Get analysis report
  async getAnalysisReport(interviewId: string): Promise<any> {
    const response = await this.authFetch(`/analysis/${interviewId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch analysis report');
    }

    return response.json();
  }

  // ANALYSIS: Export analysis report (JSON or PDF)
  async exportAnalysis(interviewId: string, format: 'json' | 'pdf' = 'json'): Promise<Blob> {
    const response = await this.authFetch(`/analysis/${interviewId}/export?format=${format}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to export analysis');
    }

    return response.blob();
  }

  // COACH: Send message to AI coach
  async sendCoachMessage(message: string, context?: {
    conversationId?: string;
    interviewId?: string;
  }): Promise<{
    conversationId: string;
    reply: string;
    suggestions: string[];
  }> {
    const response = await this.authFetch('/coach/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to send message');
    }

    return response.json();
  }

  // COACH: Get AI coach suggestions
  async getCoachSuggestions(): Promise<{ suggestions: string[] }> {
    const response = await this.authFetch('/coach/suggestions');

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to get suggestions');
    }

    return response.json();
  }

  // QUESTIONS: Get question bank list with filters
  async getQuestions(filters?: {
    type?: string;
    difficulty?: string;
    role?: string;
    page?: number;
    limit?: number;
  }): Promise<{
    items: any[];
    pagination: {
      currentPage: number;
      totalPages: number;
      totalItems: number;
    };
  }> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }

    const response = await this.authFetch(`/questions?${queryParams}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to fetch questions');
    }

    return response.json();
  }

  // QUESTIONS: AI generate questions
  async generateQuestions(criteria: {
    role: string;
    difficulty: string;
    type: string;
    count: number;
  }): Promise<{
    questions: any[];
  }> {
    const response = await this.authFetch('/questions/generate', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to generate questions');
    }

    return response.json();
  }

  // QUESTIONS: Import questions from JSON
  async importQuestions(questions: Array<{
    text: string;
    type?: string;
    difficulty?: string;
    role?: string;
    tags?: string[];
    exampleAnswer?: string;
  }>): Promise<{
    success: boolean;
    imported: number;
    skipped: number;
    errors: Array<{ index: number; error: string }>;
  }> {
    const response = await this.authFetch('/questions/import', {
      method: 'POST',
      body: JSON.stringify({ questions }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to import questions');
    }

    return response.json();
  }

  // QUESTIONS: Import questions from file (CSV or JSON)
  async importQuestionsFile(file: File): Promise<{
    success: boolean;
    imported: number;
    skipped: number;
    errors: Array<{ index: number; error: string }>;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const token = this.getToken();
    const response = await fetch(`${this.baseUrl}/questions/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to import questions');
    }

    return response.json();
  }

  // QUESTIONS: Export questions
  async exportQuestions(filters?: {
    type?: string;
    difficulty?: string;
    role?: string;
    format?: 'json' | 'csv';
  }): Promise<Blob | { questions: any[] }> {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }

    const response = await this.authFetch(`/questions/export?${queryParams}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to export questions');
    }

    if (filters?.format === 'csv') {
      return response.blob();
    }

    return response.json();
  }

  // COACH: Stream chat with AI coach (SSE)
  streamChat(
    message: string,
    context?: { conversationId?: string; history?: any[] },
    callbacks?: {
      onChunk?: (content: string) => void;
      onComplete?: (fullResponse: string) => void;
      onError?: (error: Error) => void;
    }
  ): () => void {
    const controller = new AbortController();
    const token = this.getToken();

    fetch(`${this.baseUrl}/coach/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message, context }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error?.message || 'Stream failed');
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response body');
        }

        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.error) {
                  callbacks?.onError?.(new Error(data.error.message || 'Stream error'));
                  return;
                }

                if (data.done) {
                  callbacks?.onComplete?.(data.full_response || fullResponse);
                } else if (data.content) {
                  fullResponse += data.content;
                  callbacks?.onChunk?.(data.content);
                }
              } catch {
                // Ignore parse errors
              }
            }
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          callbacks?.onError?.(error);
        }
      });

    // Return cancel function
    return () => controller.abort();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
