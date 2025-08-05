import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from backend.db.models.company import Company
from backend.db.models.provider import Provider
from backend.db.models.mapping import RawDataEntry, ValueType, PeriodType
from backend.db.models.price import PriceData, PricePeriodType

class FinancialDataService:
    """
    Service that fetches financial data from Yahoo Finance and stores it in the database.
    Migrated from the original FinancialDataDef.py logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.yahoo_provider = self._get_or_create_yahoo_provider()
    
    def _get_or_create_yahoo_provider(self) -> Provider:
        """Get or create Yahoo Finance provider"""
        provider = self.db.query(Provider).filter(Provider.name == "Yahoo Finance").first()
        if not provider:
            provider = Provider(name="Yahoo Finance")
            self.db.add(provider)
            self.db.commit()
            self.db.refresh(provider)
        return provider
    
    def fetch_and_store_company_data(self, ticker: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Fetch comprehensive financial data for a company and store in database.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            Dictionary containing processed financial data
        """
        try:
            # Get or create company
            company = self._get_or_create_company(ticker)
            
            # Fetch data from Yahoo Finance
            yf_ticker = yf.Ticker(ticker)
            
            # Get financial statements
            income_stmt = yf_ticker.financials.transpose() if not yf_ticker.financials.empty else pd.DataFrame()
            balance_sheet = yf_ticker.balance_sheet.transpose() if not yf_ticker.balance_sheet.empty else pd.DataFrame()
            cash_flow = yf_ticker.cashflow.transpose() if not yf_ticker.cashflow.empty else pd.DataFrame()
            
            # Get price data
            price_data = yf_ticker.history(start=start_date, end=end_date)
            
            # Store raw financial data
            self._store_financial_statements(company, income_stmt, balance_sheet, cash_flow)
            
            # Store price data
            self._store_price_data(company, price_data)
            
            # Calculate derived metrics (similar to original logic)
            processed_data = self._calculate_financial_metrics(
                company, income_stmt, balance_sheet, cash_flow, price_data
            )
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            raise
    
    def _get_or_create_company(self, ticker: str) -> Company:
        """Get or create a company record"""
        company = self.db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            # Try to get company info from Yahoo Finance
            try:
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info
                
                company = Company(
                    ticker=ticker,
                    name=info.get('longName', ticker),
                    country=info.get('country', 'Unknown'),
                    currency=info.get('currency', 'USD')
                )
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
            except Exception:
                # Fallback if Yahoo Finance info is not available
                company = Company(
                    ticker=ticker,
                    name=ticker,
                    country='Unknown',
                    currency='USD'
                )
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
        
        return company
    
    def _store_financial_statements(self, company: Company, income_stmt: pd.DataFrame, 
                                   balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame):
        """Store financial statement data as raw entries"""
        
        # Helper function to store a dataframe
        def store_dataframe(df: pd.DataFrame, statement_type: str):
            if df.empty:
                return
                
            for date_index, row in df.iterrows():
                fiscal_date = date_index.date() if hasattr(date_index, 'date') else date_index
                
                for field_name, value in row.items():
                    if pd.isna(value):
                        continue
                    
                    # Determine value type
                    if isinstance(value, (int, float)) and not pd.isna(value):
                        value_type = ValueType.NUMBER
                        stored_value = float(value)
                    else:
                        value_type = ValueType.STRING
                        stored_value = str(value)
                    
                    # Create raw data entry
                    raw_entry = RawDataEntry(
                        provider_id=self.yahoo_provider.id,
                        company_id=company.id,
                        fiscal_period=fiscal_date,
                        period_type=PeriodType.ANNUAL,  # Yahoo Finance typically provides annual data
                        raw_field_name=f"{statement_type}_{field_name}",
                        value_type=value_type,
                        value=stored_value
                    )
                    self.db.add(raw_entry)
        
        # Store each statement type
        store_dataframe(income_stmt, "income_statement")
        store_dataframe(balance_sheet, "balance_sheet") 
        store_dataframe(cash_flow, "cash_flow")
        
        self.db.commit()
    
    def _store_price_data(self, company: Company, price_df: pd.DataFrame):
        """Store historical price data"""
        if price_df.empty:
            return
        
        for date_index, row in price_df.iterrows():
            price_date = date_index.date() if hasattr(date_index, 'date') else date_index
            
            price_entry = PriceData(
                company_id=company.id,
                provider_id=self.yahoo_provider.id,
                date=price_date,
                period_type=PricePeriodType.DAILY,
                open=float(row.get('Open', 0)) if not pd.isna(row.get('Open')) else None,
                close=float(row.get('Close', 0)) if not pd.isna(row.get('Close')) else None,
                adj_close=float(row.get('Adj Close', 0)) if not pd.isna(row.get('Adj Close')) else None,
                volume=int(row.get('Volume', 0)) if not pd.isna(row.get('Volume')) else None
            )
            self.db.add(price_entry)
        
        self.db.commit()
    
    def _calculate_financial_metrics(self, company: Company, income_stmt: pd.DataFrame,
                                   balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame,
                                   price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate financial metrics similar to the original FinancialDataDef logic.
        This replicates the enterprise value and cash flow calculations.
        """
        if any(df.empty for df in [income_stmt, balance_sheet, cash_flow, price_data]):
            return {}
        
        try:
            # Get the most recent data
            latest_financials = {}
            
            # Extract key financial metrics (using the latest available data)
            if not income_stmt.empty:
                latest_income = income_stmt.iloc[0]
                latest_financials.update({
                    'net_income': float(latest_income.get('Net Income', 0)),
                    'total_revenue': float(latest_income.get('Total Revenue', 0)),
                    'operating_income': float(latest_income.get('Operating Income', 0)),
                    'ebit': float(latest_income.get('EBIT', latest_income.get('Operating Income', 0))),
                    'interest_expense': float(latest_income.get('Interest Expense', 0)),
                    'income_before_tax': float(latest_income.get('Pretax Income', 0))
                })
            
            if not balance_sheet.empty:
                latest_balance = balance_sheet.iloc[0]
                latest_financials.update({
                    'total_assets': float(latest_balance.get('Total Assets', 0)),
                    'total_liabilities': float(latest_balance.get('Total Liab', 0)),
                    'total_equity': float(latest_balance.get('Total Stockholder Equity', 0)),
                    'cash': float(latest_balance.get('Cash', 0)),
                    'long_term_debt': float(latest_balance.get('Long Term Debt', 0)),
                    'current_assets': float(latest_balance.get('Total Current Assets', 0)),
                    'current_liabilities': float(latest_balance.get('Total Current Liabilities', 0)),
                    'working_capital': float(latest_balance.get('Total Current Assets', 0)) - 
                                     float(latest_balance.get('Total Current Liabilities', 0))
                })
            
            if not cash_flow.empty:
                latest_cash_flow = cash_flow.iloc[0]
                latest_financials.update({
                    'operating_cash_flow': float(latest_cash_flow.get('Total Cash From Operating Activities', 0)),
                    'capital_expenditures': float(latest_cash_flow.get('Capital Expenditures', 0)),
                    'depreciation': float(latest_cash_flow.get('Depreciation', 0))
                })
            
            # Calculate EBITDA (similar to original logic)
            ebitda = latest_financials.get('ebit', 0) + latest_financials.get('depreciation', 0)
            latest_financials['ebitda'] = ebitda
            
            # Calculate Enterprise Value metrics
            if not price_data.empty:
                latest_price = float(price_data['Close'].iloc[-1])
                
                # Get shares outstanding (would need to be fetched separately or estimated)
                shares_outstanding = 1000000  # Placeholder - should be fetched from company info
                
                market_cap = latest_price * shares_outstanding
                total_debt = latest_financials.get('long_term_debt', 0)
                excess_cash = max(latest_financials.get('cash', 0) - latest_financials.get('working_capital', 0), 0)
                
                enterprise_value = market_cap + total_debt - excess_cash
                
                latest_financials.update({
                    'market_cap': market_cap,
                    'enterprise_value': enterprise_value,
                    'ev_ebitda': enterprise_value / ebitda if ebitda != 0 else 0,
                    'price_to_earnings': latest_price / (latest_financials.get('net_income', 1) / shares_outstanding) if latest_financials.get('net_income', 0) != 0 else 0
                })
            
            return latest_financials
            
        except Exception as e:
            print(f"Error calculating financial metrics: {e}")
            return {}