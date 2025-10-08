import { apiClient } from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    email: string;
    full_name: string;
    is_superuser: boolean;
  };
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const response = await apiClient.post<AuthResponse>(
      '/auth/login/access-token',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response;
  },

  async register(userData: RegisterData): Promise<AuthResponse> {
    return await apiClient.post<AuthResponse>('/auth/register', userData);
  },

  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    return await apiClient.post('/auth/refresh-token', { refresh_token: refreshToken });
  },

  async getCurrentUser(): Promise<AuthResponse['user']> {
    return await apiClient.get('/users/me');
  },

  async logout(): Promise<void> {
    // Clear tokens from storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Call backend logout if needed
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  },

  // Password reset methods
  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/reset-password', { token, new_password: newPassword });
  },
};
