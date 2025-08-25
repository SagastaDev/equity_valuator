# Getting Started with the Equity Valuation System

## Overview

This tutorial will guide you through setting up and using the Equity Valuation System for the first time. By the end of this tutorial, you will have a fully functional valuation system running locally and will have performed your first equity valuation analysis.

## What You'll Accomplish

- Set up the complete development environment
- Start all system components using Docker
- Create your user account and log in
- Explore sample financial data for major companies
- Perform your first equity valuation calculation
- Understand the data transformation pipeline

## Prerequisites

Before starting this tutorial, ensure you have:

- **Docker Desktop** installed and running
- **Git** for cloning the repository
- **Basic understanding** of financial concepts (optional but helpful)
- **Web browser** (Chrome, Firefox, Safari, or Edge)
- **8GB+ RAM** available for running all containers

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Docker**: Version 20.10 or later
- **Available Ports**: 3000 (frontend), 8000 (backend), 5432 (database)

## Step 1: Clone and Setup the Repository

### Clone the Repository
```bash
# Clone the repository
git clone https://github.com/your-org/equity_valuator.git
cd equity_valuator

# Verify you have all required files
ls -la
```

You should see the following key files and directories:
- `docker-compose.yml` - Container orchestration
- `backend/` - FastAPI backend application
- `frontend/` - React frontend application
- `Documentation/` - System documentation

### Environment Configuration
```bash
# Create environment file for backend
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@db:5432/equity_valuation
SECRET_KEY=your-super-secret-key-change-this-in-production
ENVIRONMENT=development
EOF

# Create environment file for frontend
cat > frontend/.env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
EOF
```

## Step 2: Start the Application

### Launch All Services
```bash
# Start all containers (this may take 5-10 minutes on first run)
docker-compose up --build

# Wait for all services to be healthy
# You should see logs from frontend, backend, and database
```

### Verify Services Are Running
Open multiple browser tabs to check each service:

1. **Frontend**: http://localhost:3000
   - You should see the login page
2. **Backend API**: http://localhost:8000/docs  
   - You should see the FastAPI documentation
3. **Health Check**: http://localhost:8000/health
   - Should return `{"status": "healthy"}`

If any service fails to start, check the Docker logs:
```bash
# Check specific service logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db
```

## Step 3: Create Your User Account

### Register a New User

1. **Navigate to the frontend**: http://localhost:3000
2. **Click "Sign Up"** (or similar registration link)
3. **Fill in your information**:
   - Username: `analyst1`
   - Email: `your-email@example.com`
   - Password: `SecurePassword123!`
4. **Click "Register"**

### Log In
1. **Use your credentials** to log in
2. **You should be redirected** to the main dashboard

If registration fails, you can create a user directly via the API:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst1",
    "email": "analyst1@example.com", 
    "password": "SecurePassword123!"
  }'
```

## Step 4: Explore Sample Data

### View Available Companies
1. **Navigate to the Companies page** (usually in the main navigation)
2. **You should see sample companies** loaded automatically:
   - Apple Inc. (AAPL)
   - Microsoft Corporation (MSFT)
   - Alphabet Inc. (GOOGL)
   - NVIDIA Corporation (NVDA)
   - Lockheed Martin (LMT)

If no companies are visible, the sample data may not have loaded. Check the backend logs:
```bash
docker-compose logs backend | grep -i "kaggle"
```

### Explore Price Data
1. **Click on a company** (e.g., Apple Inc.)
2. **View the price chart** showing historical stock prices
3. **Try different date ranges** (1 month, 6 months, 1 year)
4. **Notice the volume data** displayed below the price chart

### Understanding the Data Pipeline
The sample data flows through our system as follows:
1. **Raw Data**: CSV files from Kaggle dataset
2. **Data Provider**: Kaggle provider processes the files
3. **Database Storage**: Standardized data stored in PostgreSQL
4. **API Layer**: FastAPI serves data to the frontend
5. **Visualization**: React/Chart.js displays interactive charts

## Step 5: Examine Data Providers

### View Configured Providers
1. **Navigate to the Providers page**
2. **You should see the Kaggle provider** configured and enabled:
   - Name: "Kaggle Stock Data Provider"
   - Type: Kaggle
   - Status: Active
   - Data Quality: Medium

### Test Provider Connection
1. **Click the "Test Connection" button** for the Kaggle provider
2. **Verify the test passes** - you should see a success message
3. **Check available tickers** - the provider should report ~500+ available stocks

If the connection test fails, check the data directory:
```bash
# Verify sample data exists
docker-compose exec backend ls -la /app/data/kaggle/
```

## Step 6: Perform Your First Valuation

### Basic Financial Ratio Calculation

1. **Navigate to the Valuations page**
2. **Select a company** (e.g., Apple Inc.)
3. **Choose a valuation date** (use a recent date)
4. **Enter basic valuation metrics**:

```json
{
  "pe_ratio": 28.5,
  "price_to_book": 6.2,
  "debt_to_equity": 0.31,
  "current_ratio": 1.07,
  "methodology": "Basic Ratio Analysis"
}
```

5. **Click "Save Valuation"**

### View Valuation Results
1. **Your valuation should appear** in the results table
2. **Click to view details** and see all calculated metrics
3. **Compare with historical valuations** if available

### Understanding Valuation Data
The valuation results are stored as flexible JSON, allowing for:
- **Custom Metrics**: Add any financial ratios or calculations
- **Methodology Tracking**: Record which valuation method was used
- **Historical Comparison**: Compare valuations over time
- **User Attribution**: Track who performed each valuation

## Step 7: Explore Data Transformations

### View Field Mappings
1. **Navigate to the Transformations page**
2. **Click "View Field Mappings"**
3. **You should see mappings** between:
   - Raw provider fields (e.g., "Close")
   - Canonical system fields (e.g., "closing_price")

### Understand the Transformation Pipeline
```
Raw Data → Field Mapping → Transform Engine → Canonical Fields → Database
```

Example transformation:
```json
{
  "raw_field": "Close",
  "canonical_field": "closing_price", 
  "transformation": {
    "op": "multiply",
    "args": [
      {"field": "Close"},
      {"value": 1.0}
    ]
  }
}
```

## Step 8: Advanced Features

### Create Custom Field Mapping
1. **Go to Transformations → Field Mappings**
2. **Click "Add New Mapping"**
3. **Configure a simple mapping**:
   - Provider: Kaggle Stock Data Provider
   - Raw Field: Volume
   - Canonical Field: trading_volume
   - Transformation: Direct mapping (multiply by 1.0)

### View Transformation Results
1. **Save the mapping**
2. **The system will apply** the transformation to historical data
3. **Check the results** in the Companies → Price Data view

## Troubleshooting Common Issues

### Services Won't Start
```bash
# Check if ports are in use
netstat -an | grep -E "3000|8000|5432"

# Stop any conflicting services
docker-compose down

# Restart with fresh containers
docker-compose up --build --force-recreate
```

### Database Connection Issues
```bash
# Check database container status
docker-compose ps

# View database logs
docker-compose logs db

# Reset database if needed
docker-compose down -v  # WARNING: This deletes all data
docker-compose up --build
```

### Sample Data Not Loading
```bash
# Check if Kaggle data directory exists
docker-compose exec backend ls -la /app/data/

# Manually trigger data load
docker-compose exec backend python -c "
from backend.db.session import get_db
from backend.main import load_kaggle_sample_data
import asyncio
db = next(get_db())
asyncio.run(load_kaggle_sample_data(db))
"
```

### Frontend Build Errors
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend container
docker-compose build frontend --no-cache
docker-compose up frontend
```

## Summary

Congratulations! You have successfully:

✅ **Set up the complete Equity Valuation System** using Docker  
✅ **Created a user account** and logged in  
✅ **Explored sample financial data** for major companies  
✅ **Viewed interactive price charts** with historical data  
✅ **Performed your first valuation** with basic financial ratios  
✅ **Understood the data transformation pipeline** from raw data to canonical fields  
✅ **Tested data provider connections** and availability

## What's Next?

Now that you have the system running, consider these next steps:

1. **Tutorial: Creating Custom Data Providers** - Learn to integrate additional data sources
2. **Tutorial: Building Valuation Models** - Implement sophisticated valuation methodologies
3. **How-To Guide: Configure Field Mappings** - Customize data transformations
4. **How-To Guide: Add New Data Source** - Integrate with external APIs

## Need Help?

- **Documentation**: Explore the complete documentation in the `Documentation/` folder
- **API Reference**: Visit http://localhost:8000/docs for interactive API documentation
- **Support**: Check the repository issues or create a new issue for support
- **Community**: Join discussions and share experiences with other users

You're now ready to start building sophisticated equity valuation analyses with the system!