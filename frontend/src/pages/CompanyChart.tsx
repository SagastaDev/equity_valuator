import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { companiesService, CompanySummary, PriceData } from '../services/companies';
import PriceChart from '../components/PriceChart';

const CompanyChart: React.FC = () => {
  const { ticker } = useParams<{ ticker: string }>();
  const [company, setCompany] = useState<CompanySummary | null>(null);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('1Y');
  const [chartType, setChartType] = useState<'line' | 'candlestick'>('line');

  useEffect(() => {
    if (ticker) {
      loadCompanyData();
    }
  }, [ticker, timeRange]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadCompanyData = async () => {
    if (!ticker) return;

    try {
      setLoading(true);
      
      // Load company summary
      const companySummary = await companiesService.getCompanyByTicker(ticker);
      setCompany(companySummary);

      // Calculate date range based on selection
      const endDate = new Date();
      const startDate = new Date();
      
      switch (timeRange) {
        case '1M':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case '3M':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case '6M':
          startDate.setMonth(endDate.getMonth() - 6);
          break;
        case '1Y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        case 'ALL':
          // No start date for all data
          break;
      }

      // Load price data
      const prices = await companiesService.getCompanyPricesByTicker(ticker, {
        start_date: timeRange === 'ALL' ? undefined : startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        limit: 2000
      });

      // Sort by date (oldest first for chart)
      const sortedPrices = prices.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      setPriceData(sortedPrices);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load company data');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    if (priceData.length === 0) return null;

    const prices = priceData.map(d => d.close || d.adj_close || 0).filter(p => p > 0);
    if (prices.length === 0) return null;

    const currentPrice = prices[prices.length - 1];
    const previousPrice = prices[prices.length - 2] || currentPrice;
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;

    const priceChange = currentPrice - previousPrice;
    const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0;

    return {
      currentPrice,
      priceChange,
      priceChangePercent,
      minPrice,
      maxPrice,
      avgPrice,
      totalVolume: priceData.reduce((sum, d) => sum + (d.volume || 0), 0),
      dataPoints: prices.length
    };
  };

  const getPriceChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const stats = calculateStats();

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
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
        <Link 
          to="/companies" 
          className="text-blue-600 hover:text-blue-800 underline"
        >
          ← Back to Companies
        </Link>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-xl text-gray-500 mb-4">Company not found</p>
          <Link 
            to="/companies" 
            className="text-blue-600 hover:text-blue-800 underline"
          >
            ← Back to Companies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <Link 
              to="/companies" 
              className="text-blue-600 hover:text-blue-800 underline mb-2 inline-block"
            >
              ← Back to Companies
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {company.company.ticker} - {company.company.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {company.company.country} • {company.company.currency}
            </p>
          </div>
          
          {stats && (
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {companiesService.formatPrice(stats.currentPrice)}
              </div>
              <div className={`text-lg font-semibold ${getPriceChangeColor(stats.priceChange)}`}>
                {stats.priceChange >= 0 ? '+' : ''}{companiesService.formatPrice(stats.priceChange)} 
                ({stats.priceChangePercent >= 0 ? '+' : ''}{stats.priceChangePercent.toFixed(2)}%)
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        {/* Time Range Selector */}
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {range}
            </button>
          ))}
        </div>

        {/* Chart Type Selector */}
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              chartType === 'line'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Line
          </button>
          <button
            onClick={() => setChartType('candlestick')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              chartType === 'candlestick'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Candlestick
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">High</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {companiesService.formatPrice(stats.maxPrice)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">Low</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {companiesService.formatPrice(stats.minPrice)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">Average</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {companiesService.formatPrice(stats.avgPrice)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">Data Points</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {stats.dataPoints.toLocaleString()}
            </div>
          </div>
        </div>
      )}

      {/* Price Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Price History
          </h3>
          {priceData.length > 0 && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {priceData.length} data points • {companiesService.formatDate(priceData[priceData.length - 1].date)} - {companiesService.formatDate(priceData[0].date)}
            </p>
          )}
        </div>
        <PriceChart 
          priceData={priceData} 
          chartType={chartType}
          height={400}
        />
      </div>

      {/* Recent Price Data Table */}
      {priceData.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Price Data (Last 10 Days)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Open
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Close
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Volume
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Provider
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {priceData.slice(-10).reverse().map((price, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {companiesService.formatDate(price.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right">
                      {companiesService.formatPrice(price.open)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right font-medium">
                      {companiesService.formatPrice(price.close || price.adj_close)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right">
                      {companiesService.formatVolume(price.volume)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                      {price.provider_name}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompanyChart;