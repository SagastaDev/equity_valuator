import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { companiesService, Company, CompanySummary } from '../services/companies';

const Companies: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCompany, setSelectedCompany] = useState<CompanySummary | null>(null);

  useEffect(() => {
    loadCompanies();
  }, [searchTerm]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const data = await companiesService.getCompanies(0, 100, searchTerm);
      setCompanies(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const loadCompanyDetails = async (companyId: string) => {
    try {
      const details = await companiesService.getCompany(companyId);
      setSelectedCompany(details);
    } catch (err: any) {
      console.error('Failed to load company details:', err);
    }
  };

  const getPriceChangeColor = (change?: number) => {
    if (!change) return 'text-gray-500';
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getPriceChangeIcon = (change?: number) => {
    if (!change) return null;
    return change >= 0 ? '↗' : '↘';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Companies
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Browse and analyze company financial data
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <input
            type="text"
            placeholder="Search companies by ticker or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Companies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map((company) => (
          <div
            key={company.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg 
                     border border-gray-200 dark:border-gray-700 transition-shadow duration-200"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">
                    {company.ticker}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                    {company.name}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full font-medium
                  ${company.currency === 'USD' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  }`}>
                  {company.currency}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Country:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {company.country}
                  </span>
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => loadCompanyDetails(company.id)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg 
                           text-sm font-medium transition-colors duration-200
                           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  View Details
                </button>
                <Link
                  to={`/companies/${company.ticker}/chart`}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 
                           text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg text-sm font-medium 
                           transition-colors duration-200 text-center
                           focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Price Chart
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {companies.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-24 w-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" 
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <p className="text-xl text-gray-500 dark:text-gray-400 mb-2">
            {searchTerm ? 'No companies found' : 'No companies available'}
          </p>
          <p className="text-gray-400 dark:text-gray-500">
            {searchTerm 
              ? 'Try adjusting your search terms' 
              : 'Companies will appear here once data is loaded'}
          </p>
        </div>
      )}

      {/* Company Details Modal */}
      {selectedCompany && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-90vh overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                    {selectedCompany.company.ticker}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {selectedCompany.company.name}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedCompany(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 
                           focus:outline-none focus:ring-2 focus:ring-gray-500 rounded-lg p-1"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Company Info */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Company Information
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Country:</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {selectedCompany.company.country}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Currency:</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {selectedCompany.company.currency}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Price Data Summary */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Price Data
                  </h3>
                  <div className="space-y-3">
                    {selectedCompany.latest_price && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Latest Price:</span>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {companiesService.formatPrice(selectedCompany.latest_price)}
                        </span>
                      </div>
                    )}
                    
                    {selectedCompany.price_change_1d !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">1D Change:</span>
                        <span className={`font-medium ${getPriceChangeColor(selectedCompany.price_change_1d)}`}>
                          {getPriceChangeIcon(selectedCompany.price_change_1d)} {companiesService.formatPercentage(selectedCompany.price_change_1d)}
                        </span>
                      </div>
                    )}

                    {selectedCompany.price_change_1w !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">1W Change:</span>
                        <span className={`font-medium ${getPriceChangeColor(selectedCompany.price_change_1w)}`}>
                          {getPriceChangeIcon(selectedCompany.price_change_1w)} {companiesService.formatPercentage(selectedCompany.price_change_1w)}
                        </span>
                      </div>
                    )}

                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Total Records:</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {selectedCompany.total_records.toLocaleString()}
                      </span>
                    </div>

                    {selectedCompany.price_data_summary.earliest_date && (
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Data Range:</span>
                        <span className="text-gray-900 dark:text-white font-medium text-sm">
                          {companiesService.formatDate(selectedCompany.price_data_summary.earliest_date)} - {' '}
                          {selectedCompany.price_data_summary.latest_date 
                            ? companiesService.formatDate(selectedCompany.price_data_summary.latest_date)
                            : 'Present'
                          }
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-8 flex justify-end space-x-3">
                <button
                  onClick={() => setSelectedCompany(null)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 
                           hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors duration-200
                           focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Close
                </button>
                <Link
                  to={`/companies/${selectedCompany.company.ticker}/chart`}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                           transition-colors duration-200 focus:outline-none focus:ring-2 
                           focus:ring-blue-500 focus:ring-offset-2"
                  onClick={() => setSelectedCompany(null)}
                >
                  View Chart
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Companies;