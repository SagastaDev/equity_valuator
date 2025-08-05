import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  email: string;
  role: 'admin' | 'viewer';
}

export const authService = {
  async login(email: string, password: string): Promise<{ user: UserResponse; token: string }> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/token`, formData);
    const token = response.data.access_token;

    // Get user info
    const userResponse = await axios.get<UserResponse>(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    return { user: userResponse.data, token };
  },

  async getCurrentUser(): Promise<UserResponse> {
    const token = localStorage.getItem('token');
    const response = await axios.get<UserResponse>(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  async register(email: string, password: string, role: 'admin' | 'viewer' = 'viewer'): Promise<UserResponse> {
    const response = await axios.post<UserResponse>(`${API_BASE_URL}/auth/register`, {
      email,
      password,
      role
    });
    return response.data;
  }
};

// Add axios interceptor for auth
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);