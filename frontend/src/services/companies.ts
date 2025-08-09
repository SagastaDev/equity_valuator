import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

export interface Company {
  id: string;
  ticker: string;
  name: string;
  country: string;
  currency: string;
  industry_id?: number;
}

export interface CompanySummary {
  company: Company;
  price_data_summary: {
    earliest_date?: string;
    latest_date?: string;
  };
  latest_price?: number;
  price_change_1d?: number;
  price_change_1w?: number;
  total_records: number;
}

export interface PriceData {
  date: string;
  open?: number;
  close?: number;
  adj_close?: number;
  volume?: number;
  provider_name: string;
}

export interface DataIngestionRequest {
  tickers: string[];
  provider_type: string;
  start_date?: string;
  end_date?: string;
}

export interface DataIngestionResponse {
  successful_tickers: string[];
  failed_tickers: Array<{ ticker: string; error: string }>;
  records_inserted: number;
  date_range?: {
    start_date?: string;
    end_date?: string;
  };
  errors: string[];
}

export const companiesService = {
  async getCompanies(skip = 0, limit = 100, search?: string): Promise<Company[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    
    if (search) {
      params.append('search', search);
    }

    const response = await axios.get<Company[]>(`${API_BASE_URL}/api/companies/?${params}`);
    return response.data;
  },

  async getCompany(companyId: string): Promise<CompanySummary> {
    const response = await axios.get<CompanySummary>(`${API_BASE_URL}/api/companies/${companyId}`);
    return response.data;
  },

  async getCompanyByTicker(ticker: string): Promise<CompanySummary> {
    const response = await axios.get<CompanySummary>(`${API_BASE_URL}/api/companies/ticker/${ticker}`);
    return response.data;
  },

  async getCompanyPrices(
    companyId: string,
    options: {
      start_date?: string;
      end_date?: string;
      limit?: number;
      provider?: string;
    } = {}
  ): Promise<PriceData[]> {
    const params = new URLSearchParams();
    
    if (options.start_date) params.append('start_date', options.start_date);
    if (options.end_date) params.append('end_date', options.end_date);
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.provider) params.append('provider', options.provider);

    const response = await axios.get<PriceData[]>(
      `${API_BASE_URL}/api/companies/${companyId}/prices?${params}`
    );
    return response.data;
  },

  async getCompanyPricesByTicker(
    ticker: string,
    options: {
      start_date?: string;
      end_date?: string;
      limit?: number;
      provider?: string;
    } = {}
  ): Promise<PriceData[]> {
    const params = new URLSearchParams();
    
    if (options.start_date) params.append('start_date', options.start_date);
    if (options.end_date) params.append('end_date', options.end_date);
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.provider) params.append('provider', options.provider);

    const response = await axios.get<PriceData[]>(
      `${API_BASE_URL}/api/companies/ticker/${ticker}/prices?${params}`
    );
    return response.data;
  },

  async createCompany(companyData: {
    ticker: string;
    name: string;
    country?: string;
    currency?: string;
    industry_id?: number;
  }): Promise<Company> {
    const response = await axios.post<Company>(`${API_BASE_URL}/api/companies/`, {
      ...companyData,
      country: companyData.country || 'Unknown',
      currency: companyData.currency || 'USD',
    });
    return response.data;
  },

  async updateCompany(
    companyId: string,
    companyData: {
      name?: string;
      country?: string;
      currency?: string;
      industry_id?: number;
    }
  ): Promise<Company> {
    const response = await axios.put<Company>(`${API_BASE_URL}/api/companies/${companyId}`, companyData);
    return response.data;
  },

  async ingestData(request: DataIngestionRequest): Promise<DataIngestionResponse> {
    const response = await axios.post<DataIngestionResponse>(
      `${API_BASE_URL}/api/companies/ingest/sync`,
      request
    );
    return response.data;
  },

  async getAvailableProviders(): Promise<{ providers: Record<string, any> }> {
    const response = await axios.get(`${API_BASE_URL}/api/companies/providers`);
    return response.data;
  },

  // Helper functions for data formatting
  formatPrice(price?: number): string {
    if (price === undefined || price === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  },

  formatPercentage(value?: number): string {
    if (value === undefined || value === null) return 'N/A';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  },

  formatVolume(volume?: number): string {
    if (volume === undefined || volume === null) return 'N/A';
    
    if (volume >= 1000000000) {
      return `${(volume / 1000000000).toFixed(1)}B`;
    } else if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    
    return volume.toLocaleString();
  },

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },
};