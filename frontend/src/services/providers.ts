import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export interface Provider {
  id: number;
  name: string;
}

export interface CreateProviderRequest {
  name: string;
}

export const providersService = {
  async getAllProviders(): Promise<Provider[]> {
    const response = await axios.get<Provider[]>(`${API_BASE_URL}/api/providers/`);
    return response.data;
  },

  async getProvider(id: number): Promise<Provider> {
    const response = await axios.get<Provider>(`${API_BASE_URL}/api/providers/${id}`);
    return response.data;
  },

  async createProvider(provider: CreateProviderRequest): Promise<Provider> {
    const response = await axios.post<Provider>(`${API_BASE_URL}/api/providers/`, provider);
    return response.data;
  }
};