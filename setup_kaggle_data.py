"""
Kaggle Dataset Setup Script

This script helps set up the Kaggle stock market dataset for our companies.
It provides multiple approaches to get the data:
1. Manual download instructions
2. API download (if configured)
3. Sample data creation for testing

Run from the project root directory.
"""

import os
import sys
from pathlib import Path
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import zipfile
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Companies we want to load
TARGET_COMPANIES = ["AAPL", "MSFT", "GOOGL", "NVDA", "LMT"]

def check_kaggle_api():
    """Check if Kaggle API is configured"""
    try:
        import kaggle
        kaggle.api.authenticate()
        logger.info("✅ Kaggle API is configured and authenticated")
        return True
    except Exception as e:
        logger.warning(f"❌ Kaggle API not configured: {e}")
        logger.info("To use Kaggle API:")
        logger.info("1. Create account at kaggle.com")
        logger.info("2. Go to Account > API > Create New Token")
        logger.info("3. Download kaggle.json to ~/.kaggle/ (or %USERPROFILE%/.kaggle/ on Windows)")
        logger.info("4. Run: pip install kaggle")
        return False

def download_via_api():
    """Download dataset via Kaggle API"""
    try:
        import kaggle
        
        data_dir = Path("data/kaggle")
        dataset_file = data_dir / "stock-market-data.zip"
        
        if dataset_file.exists():
            logger.info(f"✅ Dataset already exists at {dataset_file}")
            return str(dataset_file)
        
        logger.info("📥 Downloading Kaggle dataset via API...")
        kaggle.api.dataset_download_files(
            'paultimothymooney/stock-market-data',
            path=str(data_dir),
            unzip=False
        )
        
        if dataset_file.exists():
            logger.info(f"✅ Successfully downloaded to {dataset_file}")
            return str(dataset_file)
        else:
            logger.error("❌ Download completed but file not found")
            return None
            
    except Exception as e:
        logger.error(f"❌ API download failed: {e}")
        return None

def manual_download_instructions():
    """Provide manual download instructions"""
    logger.info("\n" + "="*60)
    logger.info("📋 MANUAL DOWNLOAD INSTRUCTIONS")
    logger.info("="*60)
    logger.info("1. Go to: https://www.kaggle.com/datasets/paultimothymooney/stock-market-data")
    logger.info("2. Click 'Download' button")
    logger.info("3. Save the ZIP file as: data/kaggle/stock-market-data.zip")
    logger.info("4. Re-run this script")
    logger.info("="*60)

def extract_dataset(zip_path: str):
    """Extract the dataset"""
    extract_path = Path("data/kaggle/extracted")
    
    if extract_path.exists() and any(extract_path.iterdir()):
        logger.info(f"✅ Dataset already extracted at {extract_path}")
        return str(extract_path)
    
    logger.info(f"📂 Extracting {zip_path}...")
    extract_path.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        logger.info(f"✅ Extracted to {extract_path}")
        
        # List contents to understand structure
        logger.info("📁 Dataset contents:")
        for item in sorted(extract_path.iterdir()):
            if item.is_dir():
                count = len(list(item.glob("*.csv")))
                logger.info(f"   📁 {item.name}/ ({count} CSV files)")
            else:
                logger.info(f"   📄 {item.name}")
        
        return str(extract_path)
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        return None

def find_company_files(extract_path: str):
    """Find CSV files for our target companies"""
    extract_dir = Path(extract_path)
    found_companies = {}
    
    # Common patterns for file locations
    search_patterns = [
        "*.csv",
        "stocks/*.csv", 
        "**/*.csv"
    ]
    
    logger.info(f"🔍 Searching for company files in {extract_path}")
    
    for pattern in search_patterns:
        for file_path in extract_dir.glob(pattern):
            # Extract ticker from filename
            ticker = file_path.stem.upper()
            
            # Check if this is one of our target companies
            if ticker in TARGET_COMPANIES:
                found_companies[ticker] = file_path
                logger.info(f"   ✅ Found {ticker}: {file_path}")
    
    # Report missing companies
    missing = set(TARGET_COMPANIES) - set(found_companies.keys())
    if missing:
        logger.warning(f"❌ Missing companies: {missing}")
        
        # Show available files for reference
        all_csvs = list(extract_dir.glob("**/*.csv"))
        logger.info(f"📄 Available CSV files (first 10): {[f.stem for f in all_csvs[:10]]}")
    
    return found_companies

def create_sample_data():
    """Create sample data for testing if no real data is available"""
    logger.info("🧪 Creating sample data for testing...")
    
    data_dir = Path("data/kaggle/sample")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample price data for each company
    for ticker in TARGET_COMPANIES:
        file_path = data_dir / f"{ticker}.csv"
        
        if file_path.exists():
            logger.info(f"   ✅ Sample data already exists for {ticker}")
            continue
        
        # Generate 2 years of sample data
        start_date = datetime.now() - timedelta(days=730)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
        
        # Remove weekends (simple approximation)
        dates = [d for d in dates if d.weekday() < 5]
        
        # Generate realistic price data
        np.random.seed(hash(ticker) % 2**32)  # Consistent data per ticker
        
        initial_price = np.random.uniform(50, 300)  # Random starting price
        prices = [initial_price]
        
        for i in range(1, len(dates)):
            # Random walk with slight upward trend
            change = np.random.normal(0.001, 0.02)  # 0.1% daily trend, 2% volatility
            price = prices[-1] * (1 + change)
            prices.append(max(price, 1))  # Don't go below $1
        
        # Generate OHLC data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC
            daily_volatility = 0.01
            high = close * (1 + np.random.uniform(0, daily_volatility))
            low = close * (1 - np.random.uniform(0, daily_volatility))
            open_price = close * (1 + np.random.uniform(-daily_volatility/2, daily_volatility/2))
            
            # Ensure OHLC constraints
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            volume = int(np.random.uniform(1000000, 50000000))  # Random volume
            
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
        logger.info(f"   ✅ Created sample data for {ticker}: {len(data)} records")
    
    logger.info(f"✅ Sample data created in {data_dir}")
    return str(data_dir)

def main():
    """Main setup function"""
    logger.info("🚀 Kaggle Dataset Setup")
    logger.info("="*50)
    
    # Check if we already have the dataset
    zip_path = Path("data/kaggle/stock-market-data.zip")
    extract_path = Path("data/kaggle/extracted")
    
    dataset_path = None
    
    # Try to find existing data
    if extract_path.exists() and any(extract_path.iterdir()):
        logger.info("✅ Found existing extracted dataset")
        dataset_path = str(extract_path)
    elif zip_path.exists():
        logger.info("✅ Found existing zip file, extracting...")
        dataset_path = extract_dataset(str(zip_path))
    else:
        # Try to download
        logger.info("📥 Dataset not found, attempting download...")
        
        if check_kaggle_api():
            downloaded_zip = download_via_api()
            if downloaded_zip:
                dataset_path = extract_dataset(downloaded_zip)
        
        if not dataset_path:
            logger.warning("❌ Could not download dataset automatically")
            manual_download_instructions()
            
            # Offer to create sample data
            response = input("\n🧪 Create sample data for testing? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                dataset_path = create_sample_data()
            else:
                logger.info("Please download the dataset manually and re-run this script.")
                return False
    
    if dataset_path:
        # Find our target companies
        logger.info("\n🎯 Looking for target companies...")
        found_companies = find_company_files(dataset_path)
        
        if found_companies:
            logger.info(f"\n✅ Ready to load data for {len(found_companies)} companies!")
            logger.info("Found companies:")
            for ticker, path in found_companies.items():
                # Quick peek at data
                try:
                    df = pd.read_csv(path)
                    logger.info(f"   📊 {ticker}: {len(df)} records ({df['Date'].min()} to {df['Date'].max()})")
                except:
                    logger.info(f"   📊 {ticker}: {path}")
            
            logger.info(f"\n🎯 Next step: Use the Kaggle provider to load this data into the database")
            logger.info(f"   Dataset path: {dataset_path}")
            return True
        else:
            logger.error("❌ No target companies found in dataset")
            return False
    else:
        logger.error("❌ Could not set up dataset")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("\n🎉 Kaggle dataset setup complete!")
        logger.info("Run the data loading script next to populate the database.")
    else:
        logger.error("❌ Setup failed. Please check the instructions above.")
        sys.exit(1)