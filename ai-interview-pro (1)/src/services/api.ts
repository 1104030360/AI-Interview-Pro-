/**
 * API Client for AI Interview Pro Backend
 *
 * Provides type-safe methods for interacting with Flask RESTful API
 * Base URL: http://localhost:5001/api
 */

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001/api';

// Type definitions
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  userId: string;
  email: string;
  name: string;
  role?: string;
  accessToken: string;
  refreshToken: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
}

/**
 * API Client Class
 * Handles all HTTP requests to the backend with automatic token management
 */
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic request helper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        // Handle API errors
        const error = data as ApiError;
        throw new Error(error.error?.message || `HTTP error! status: ${response.status}`);
      }

      return data as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get authorization header with current access token
   */
  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // ========================================
  // Authentication API
  // ========================================

  /**
   * Register a new user
   * @param data User registration data
   * @returns Auth response with tokens
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Store tokens in localStorage
    localStorage.setItem('auth_token', response.accessToken);
    localStorage.setItem('refresh_token', response.refreshToken);
    localStorage.setItem('user_id', response.userId);

    return response;
  }

  /**
   * Login with email and password
   * @param data Login credentials
   * @returns Auth response with tokens
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Store tokens in localStorage
    localStorage.setItem('auth_token', response.accessToken);
    localStorage.setItem('refresh_token', response.refreshToken);
    localStorage.setItem('user_id', response.userId);

    return response;
  }

  /**
   * Refresh access token using refresh token
   * @returns New access token
   */
  async refreshToken(): Promise<{ accessToken: string }> {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.request<{ accessToken: string }>('/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
      },
    });

    // Update access token
    localStorage.setItem('auth_token', response.accessToken);

    return response;
  }

  /**
   * Get current user information
   * @returns User object
   */
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'GET',
      headers: this.getAuthHeader(),
    });
  }

  /**
   * Logout user (clear local storage)
   */
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
  }

  /**
   * Check if user is authenticated
   * @returns Boolean indicating authentication status
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  // ========================================
  // System API
  // ========================================

  /**
   * Health check endpoint
   * @returns Health status
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/health', {
      method: 'GET',
    });
  }

  // ========================================
  // Future API endpoints (placeholder)
  // ========================================

  // Settings API
  // async saveSettings(settings: AppSettings) { ... }
  // async getSettings() { ... }

  // Interview API
  // async startInterview(data: InterviewStartRequest) { ... }
  // async uploadRecording(sessionId: string, file: File) { ... }

  // Analysis API
  // async getAnalysis(analysisId: string) { ... }

  // History API
  // async getHistory(page: number, limit: number) { ... }

  // Questions API
  // async getQuestions(filters: QuestionFilters) { ... }

  // Coach API
  // async sendCoachMessage(message: string, context?: any) { ... }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export default for convenience
export default apiClient;
