"""
Create sample stock data for testing

This script creates realistic sample price data for our target companies.
This allows us to test the system without needing the full Kaggle dataset.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Companies we want to load
TARGET_COMPANIES = ["AAPL", "MSFT", "GOOGL", "NVDA", "LMT"]

def create_sample_data():
    """Create sample data for testing"""
    logger.info("Creating sample data for testing...")
    
    data_dir = Path("data/kaggle/sample")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample price data for each company
    for ticker in TARGET_COMPANIES:
        file_path = data_dir / f"{ticker}.csv"
        
        if file_path.exists():
            logger.info(f"Sample data already exists for {ticker}")
            continue
        
        # Generate 2 years of sample data
        start_date = datetime.now() - timedelta(days=730)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
        
        # Remove weekends (simple approximation)
        dates = [d for d in dates if d.weekday() < 5]
        
        # Generate realistic price data with different characteristics per company
        np.random.seed(hash(ticker) % 2**32)  # Consistent data per ticker
        
        # Different starting prices for each company
        company_prices = {
            "AAPL": 150,
            "MSFT": 300, 
            "GOOGL": 2800,
            "NVDA": 220,
            "LMT": 380
        }
        
        initial_price = company_prices.get(ticker, 100)
        prices = [initial_price]
        
        for i in range(1, len(dates)):
            # Random walk with slight upward trend
            change = np.random.normal(0.0005, 0.015)  # 0.05% daily trend, 1.5% volatility
            price = prices[-1] * (1 + change)
            prices.append(max(price, 1))  # Don't go below $1
        
        # Generate OHLC data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC
            daily_volatility = 0.008
            high_mult = 1 + np.random.uniform(0, daily_volatility)
            low_mult = 1 - np.random.uniform(0, daily_volatility)
            open_mult = 1 + np.random.uniform(-daily_volatility/2, daily_volatility/2)
            
            high = close * high_mult
            low = close * low_mult
            open_price = close * open_mult
            
            # Ensure OHLC constraints
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Volume varies by company
            base_volume = {
                "AAPL": 50000000,
                "MSFT": 30000000,
                "GOOGL": 1500000,
                "NVDA": 40000000,
                "LMT": 2000000
            }.get(ticker, 10000000)
            
            volume = int(np.random.uniform(base_volume * 0.5, base_volume * 1.5))
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': round(open_price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(close, 2),
                'Adj Close': round(close, 2),  # Simplified
                'Volume': volume
            })
        
        # Save to CSV
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        logger.info(f"Created sample data for {ticker}: {len(data)} records")
        
        # Show data preview
        logger.info(f"  {ticker} price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
        logger.info(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    logger.info(f"Sample data created in {data_dir}")
    return str(data_dir)

if __name__ == "__main__":
    create_sample_data()
    print("\nSample data creation complete!")
    print("Next step: Run the Kaggle data loading script to populate the database.")