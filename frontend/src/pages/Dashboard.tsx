import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to Equity Valuation System
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Hello, {user?.email}! You have {user?.role} access.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Valuations</h3>
              <p className="text-gray-600">View and manage company valuations</p>
              <div className="mt-4">
                <span className="text-2xl font-bold text-primary-600">0</span>
                <span className="text-sm text-gray-500 ml-1">Total Valuations</span>
              </div>
            </div>

            {user?.role === 'admin' && (
              <>
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Data Providers</h3>
                  <p className="text-gray-600">Manage data source providers</p>
                  <div className="mt-4">
                    <span className="text-2xl font-bold text-primary-600">1</span>
                    <span className="text-sm text-gray-500 ml-1">Active Providers</span>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Field Mappings</h3>
                  <p className="text-gray-600">Configure data transformations</p>
                  <div className="mt-4">
                    <span className="text-2xl font-bold text-primary-600">0</span>
                    <span className="text-sm text-gray-500 ml-1">Configured Mappings</span>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="mt-8 text-left">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Getting Started</h2>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">Quick Start Guide</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>1. Navigate to Valuations to view company analysis</li>
                {user?.role === 'admin' && (
                  <>
                    <li>2. Configure data providers in the Providers section</li>
                    <li>3. Set up field mappings in Transformations</li>
                    <li>4. Create custom formulas for calculations</li>
                  </>
                )}
                <li>{user?.role === 'admin' ? '5' : '2'}. Start analyzing equity valuations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;