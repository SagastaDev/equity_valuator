import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ScriptableContext,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format, parseISO } from 'date-fns';
import { PriceData } from '../services/companies';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PriceChartProps {
  priceData: PriceData[];
  chartType: 'line' | 'candlestick';
  height?: number;
}

const PriceChart: React.FC<PriceChartProps> = ({ 
  priceData, 
  chartType, 
  height = 400 
}) => {
  const chartData = useMemo(() => {
    // Sort data by date (oldest first for chart display)
    const sortedData = [...priceData].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    const labels = sortedData.map(d => format(parseISO(d.date), 'MMM dd, yyyy'));
    
    if (chartType === 'line') {
      // Use closing prices for line chart
      const prices = sortedData.map(d => d.close || d.adj_close || 0);
      
      return {
        labels,
        datasets: [
          {
            label: 'Close Price',
            data: prices,
            borderColor: 'rgb(59, 130, 246)', // Blue-500
            backgroundColor: (context: ScriptableContext<'line'>) => {
              const ctx = context.chart.ctx;
              const gradient = ctx.createLinearGradient(0, 0, 0, height);
              gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
              gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)');
              return gradient;
            },
            fill: true,
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 4,
            borderWidth: 2,
          },
        ],
      };
    }
    
    // For candlestick, we'll use a line chart with OHLC visualization using multiple datasets
    const opens = sortedData.map(d => d.open || 0);
    const highs = sortedData.map(d => Math.max(d.open || 0, d.close || 0, d.adj_close || 0));
    const lows = sortedData.map(d => Math.min(d.open || 0, d.close || 0, d.adj_close || 0));
    const closes = sortedData.map(d => d.close || d.adj_close || 0);
    
    return {
      labels,
      datasets: [
        {
          label: 'High',
          data: highs,
          borderColor: 'rgba(34, 197, 94, 0.6)', // Green-500
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: false,
          tension: 0.1,
          pointRadius: 0,
          pointHoverRadius: 3,
          borderWidth: 1,
        },
        {
          label: 'Close',
          data: closes,
          borderColor: 'rgb(59, 130, 246)', // Blue-500
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: false,
          tension: 0.1,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2,
        },
        {
          label: 'Open',
          data: opens,
          borderColor: 'rgba(156, 163, 175, 0.8)', // Gray-400
          backgroundColor: 'rgba(156, 163, 175, 0.1)',
          fill: false,
          tension: 0.1,
          pointRadius: 0,
          pointHoverRadius: 3,
          borderWidth: 1,
        },
        {
          label: 'Low',
          data: lows,
          borderColor: 'rgba(239, 68, 68, 0.6)', // Red-500
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: false,
          tension: 0.1,
          pointRadius: 0,
          pointHoverRadius: 3,
          borderWidth: 1,
        },
      ],
    };
  }, [priceData, chartType, height]);

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(107, 114, 128)', // Gray-500
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.9)', // Gray-900
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(75, 85, 99, 0.5)', // Gray-600
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const price = context.parsed.y;
            return `${context.dataset.label}: $${price.toFixed(2)}`;
          },
        },
      },
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.2)', // Gray-400 with opacity
        },
        ticks: {
          color: 'rgb(107, 114, 128)', // Gray-500
          maxTicksLimit: 8,
        },
      },
      y: {
        display: true,
        position: 'right' as const,
        grid: {
          color: 'rgba(156, 163, 175, 0.2)', // Gray-400 with opacity
        },
        ticks: {
          color: 'rgb(107, 114, 128)', // Gray-500
          callback: function(value) {
            return `$${Number(value).toFixed(2)}`;
          },
        },
      },
    },
    elements: {
      line: {
        tension: 0.1,
      },
    },
  };

  if (priceData.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div className="text-center">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" 
                    d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <p className="text-lg text-gray-500 dark:text-gray-400">
            No price data available
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: `${height}px` }} className="relative">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default PriceChart;