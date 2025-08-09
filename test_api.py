#!/usr/bin/env python3
"""Simple test script to verify API functionality."""

import requests
import json

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "admin@test.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Auth failed: {response.status_code} - {response.text}")
        return None

def test_companies_endpoint():
    """Test the companies endpoint."""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get list of companies
    response = requests.get(f"{BASE_URL}/api/companies/", headers=headers)
    print(f"Companies list: {response.status_code}")
    if response.status_code == 200:
        companies = response.json()
        print(f"Found {len(companies)} companies:")
        for company in companies:
            print(f"  - {company['ticker']}: {company['name']}")
    else:
        print(f"Error: {response.text}")
    
    # Test price data for a test company
    if response.status_code == 200 and companies:
        test_ticker = companies[0]['ticker']
        print(f"\nTesting price data for {test_ticker}:")
        
        price_response = requests.get(
            f"{BASE_URL}/api/companies/ticker/{test_ticker}/prices", 
            headers=headers
        )
        print(f"Price data: {price_response.status_code}")
        if price_response.status_code == 200:
            prices = price_response.json()
            print(f"Found {len(prices)} price records")
        else:
            print(f"Error: {price_response.text}")
    
    # Test AAPL specifically
    print(f"\nTesting AAPL specifically:")
    aapl_response = requests.get(f"{BASE_URL}/api/companies/ticker/AAPL/prices", headers=headers)
    print(f"AAPL price data: {aapl_response.status_code}")
    if aapl_response.status_code != 200:
        print(f"AAPL Error: {aapl_response.text}")

if __name__ == "__main__":
    test_companies_endpoint()