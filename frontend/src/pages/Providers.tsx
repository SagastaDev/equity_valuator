import React from 'react';

const Providers: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white transition-colors">Data Providers</h1>
        <p className="text-gray-600 dark:text-gray-300 transition-colors">Manage financial data source providers</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow transition-colors">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center transition-colors">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white transition-colors">Active Providers</h2>
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Add Provider
          </button>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white transition-colors">Yahoo Finance</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors">Financial data and price information</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                  <button className="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Providers;