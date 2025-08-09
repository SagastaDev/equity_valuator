import React, { useState, useEffect } from 'react';
import { providersService, Provider } from '../services/providers';

const Providers: React.FC = () => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const data = await providersService.getAllProviders();
        setProviders(data);
      } catch (err) {
        setError('Failed to load providers');
        console.error('Error fetching providers:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProviders();
  }, []);

  const getProviderDescription = (name: string) => {
    const descriptions: { [key: string]: string } = {
      'Yahoo Finance': 'Real-time financial data and price information',
      'FinStack Global (Test)': 'Global financial data provider - Test environment',
      'AlphaFinance Pro (Test)': 'Professional-grade financial analytics - Test environment',
      'MarketInsight Analytics (Test)': 'Advanced market insights and analytics - Test environment',
      'DataStream Financial (Test)': 'Comprehensive financial data streams - Test environment',
      'Sample Data (Kaggle)': 'Sample financial datasets for testing',
      'Kaggle Stock Market Data': 'Historical stock market data from Kaggle'
    };
    return descriptions[name] || 'Financial data provider';
  };

  if (loading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white transition-colors">Data Providers</h1>
          <p className="text-gray-600 dark:text-gray-300 transition-colors">Manage financial data source providers</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow transition-colors p-6">
          <p className="text-gray-600 dark:text-gray-300">Loading providers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white transition-colors">Data Providers</h1>
        <p className="text-gray-600 dark:text-gray-300 transition-colors">Manage financial data source providers</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow transition-colors">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center transition-colors">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white transition-colors">
            Active Providers ({providers.length})
          </h2>
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Provider
          </button>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {providers.map((provider) => (
              <div key={provider.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white transition-colors">
                      {provider.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors">
                      {getProviderDescription(provider.name)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      provider.name === 'Yahoo Finance' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' 
                        : provider.name.includes('(Test)') 
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                    }`}>
                      {provider.name === 'Yahoo Finance' ? 'Active' : provider.name.includes('(Test)') ? 'Test' : 'Sample'}
                    </span>
                    <button className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors">
                      Configure
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Providers;