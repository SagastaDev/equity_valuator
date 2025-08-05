class FinancialData:
    def __init__(self, ticker, alt_ticker, start, end):

        import pandas as pd
        import numpy as np
        import math
        import pandas_datareader as web
        import yfinance as yf
        import datetime as dt
        import requests
        from YahooDataParser import yahoo_data_parser
        from pylab import mpl, plt

        plt.style.use('seaborn')
        mpl.rcParams['font.family'] = 'serif'
        pd.set_option('display.max_columns', None)
        pd.set_option('precision', 2)

        def Format_Table(final_table):
            pd.options.display.float_format = '{:,}'.format
            i = final_table.copy()
            i.style.format("{:,.0f}")
            i = i.round(decimals=2)
            return i

        """# Data gathering"""
        print("Starting with {}".format(ticker))
        data = pd.DataFrame()
        try:
            try:
                data = yahoo_data_parser(ticker, start, end).dropna()
            except:
                data = yahoo_data_parser(alt_ticker, start, end).dropna()

            data = Format_Table(data)

            data_prices = pd.DataFrame()
            data_prices['Year'] = data['Year']
            data_prices['Month'] = data['Month']
            data_prices['Avg_month_price'] = data['Avg_month_price']
            data_prices.reset_index(drop=True, inplace=True)
            data_prices = data_prices.drop_duplicates()
            company = yf.Ticker(ticker)
            cashflow_statement = pd.DataFrame()
            cashflow_statement = company.cashflow
            financials = pd.DataFrame()
            financials = company.financials
            balance_sheet = pd.DataFrame()
            balance_sheet = company.balance_sheet
            df = pd.DataFrame(list(company.info.items()), columns=['Key', 'Value'])

            # we need these dataframes transposed, so we have a single row by each time period
            # Except for earnings, which comes already transposed and with years instead of YYYMMMDDD.
            balance_sheet = balance_sheet.transpose()
            financials = financials.transpose()
            cashflow_statement = cashflow_statement.transpose()

            earnings = pd.DataFrame()
            earnings = company.earnings

            # Normalize dates columns so we can make a big join later
            financials['Date'] = financials.index
            cashflow_statement['Date'] = cashflow_statement.index
            earnings.index.names = ['Date']
            earnings['Year'] = earnings.index
            balance_sheet['Date'] = balance_sheet.index

            # Net Income gets dupped on financials, so we dropped to avoid having a "Net Income_y" table
            financials.drop('Net Income', inplace=True, axis=1)
            financials.drop('Minority Interest', inplace=True, axis=1)
            result = pd.merge(cashflow_statement, financials, on='Date')
            result = pd.merge(result, balance_sheet, on='Date')

            # Normalize datetime to years so we can add income table
            result['Year'] = pd.DatetimeIndex(result['Date']).year
            result['Month'] = pd.DatetimeIndex(result['Date']).month
            result = pd.merge(result, earnings, on='Year')
            col_name = 'Date'
            first_col = result.pop(col_name)
            result.insert(0, col_name, first_col)
            result['Working Capital'] = result['Total Current Assets'] - result['Total Current Liabilities']

            pd.set_option('float_format', '{:f}'.format)

            """## Get Shares"""





            shares_year_avg = pd.DataFrame()
            shares_year_avg['Year'] = result['Year'].copy()
            try:
                yshares = float(company.info.get('sharesOutstanding'))
            except:
                yshares = 0
            shares_year_avg['Shares'] = yshares

            # Use this line only if shares count is wrong
            # shares_year_avg['Shares'] = 340000000

            result = pd.merge(result, shares_year_avg, on='Year', how='left')
            statements_target_month = result['Month'].iloc[0].astype(int)
            statements_target_year = result['Year'].iloc[0].astype(int)

            avg_statement_month_prices = data_prices.copy()

            if statements_target_year > avg_statement_month_prices['Year'].iloc[-1]:
                print('Statement Year is bigger than avg price year')
                print(avg_statement_month_prices['Year'].iloc[-1])
            avg_statement_month_prices = avg_statement_month_prices.drop(
                avg_statement_month_prices[avg_statement_month_prices.Month != statements_target_month].index)
            avg_statement_month_prices = avg_statement_month_prices.drop(['Month'], axis=1)
            # print(avg_statement_month_prices)
            result = pd.merge(result, avg_statement_month_prices, on='Year', how='left')
            result = Format_Table(result)

            initial_fields = ['Date',
                              'Change To Liabilities',
                              'Total Cashflows From Investing Activities',
                              'Net Borrowings',
                              'Total Cash From Financing Activities',
                              'Change To Operating Activities',
                              'Net Income',
                              'Change In Cash',
                              'Repurchase Of Stock',
                              'Total Cash From Operating Activities',
                              'Depreciation',
                              'Other Cashflows From Investing Activities',
                              'Dividends Paid',
                              'Change To Inventory',
                              'Change To Account Receivables',
                              'Other Cashflows From Financing Activities',
                              'Change To Netincome',
                              'Capital Expenditures',
                              'Research Development',
                              'Effect Of Accounting Charges',
                              'Income Before Tax',
                              'Selling General Administrative',
                              'Gross Profit',
                              'Ebit',
                              'Operating Income',
                              'Other Operating Expenses',
                              'Interest Expense',
                              'Extraordinary Items',
                              'Non Recurring',
                              'Other Items',
                              'Income Tax Expense',
                              'Total Revenue',
                              'Total Operating Expenses',
                              'Cost Of Revenue',
                              'Total Other Income Expense Net',
                              'Discontinued Operations',
                              'Net Income From Continuing Ops',
                              'Net Income Applicable To Common Shares',
                              'Intangible Assets',
                              'Capital Surplus',
                              'Total Liab',
                              'Total Stockholder Equity',
                              'Minority Interest',
                              'Other Current Liab',
                              'Total Assets',
                              'Common Stock',
                              'Other Current Assets',
                              'Retained Earnings',
                              'Other Liab',
                              'Good Will',
                              'Treasury Stock',
                              'Other Assets',
                              'Cash',
                              'Total Current Liabilities',
                              'Deferred Long Term Asset Charges',
                              'Short Long Term Debt',
                              'Other Stockholder Equity',
                              'Property Plant Equipment',
                              'Total Current Assets',
                              'Long Term Investments',
                              'Net Tangible Assets',
                              'Net Receivables',
                              'Long Term Debt',
                              'Inventory',
                              'Accounts Payable',
                              'Year',
                              'Month',
                              'Revenue',
                              'Earnings',
                              'Working Capital',
                              'Shares',
                              'Avg_month_price']

            current_fields = []
            for i in result.columns:
              current_fields.append(i)
            for i in initial_fields:
              if i not in current_fields:
                # print(i, "Not here. Setting it up to zero")
                result[i] = 0

            # !!! IMPORTANT !!!
            # Yahoo data does not include amortisation. So EBITDA showed here is unaccurate.
            # Proper data source should be used here so we can have a df['Amortisation'] included
            # in the following sum.
            result = result.fillna(0)
            entreprise_value_sheet = pd.DataFrame()
            entreprise_value_sheet['Date'] = result['Date']
            entreprise_value_sheet['Year'] = entreprise_value_sheet['Date'].dt.year

            entreprise_value_sheet['EBITDA'] = result['Income Before Tax'] + result['Interest Expense'] + \
                                               result['Depreciation']

            # For the sole purpose of this script, we'll replace the original ebitda for
            # the EBITDA2 column, since this is a more close to reality number

            entreprise_value_sheet['EBITDA2'] = result['Ebit'] + result['Depreciation']

            entreprise_value_sheet['EBITDA'] = entreprise_value_sheet['EBITDA2']

            entreprise_value_sheet['Ebitda Growth'] = np.log(
                entreprise_value_sheet['EBITDA'].astype(float) / entreprise_value_sheet['EBITDA'].astype(float).shift(
                    -1))

            entreprise_value_sheet['Debt'] = result['Long Term Debt'] + np.where(result['Short Long Term Debt'],
                                                                                 result['Short Long Term Debt'], 0)

            # EXCESS CASH CALC.

            entreprise_value_sheet['Excess Cash'] = np.where((result['Cash'] - result['Working Capital']) > 0, \
                                                             (result['Cash'] - result['Working Capital']), 0)

            # Outstanding shares is not on this API. In the spirit of having the code working ASAP
            # I'll be hardcoding this variable for LMT. Because of this Market cap here is a
            # constant variable. But it should be a dynamic one. Where you do that number with
            # the same period (in this case Dec. from each year), SMA for the Close price of the given period
            # multiply by that same period outstanding shares

            entreprise_value_sheet['Shares'] = result['Shares']
            entreprise_value_sheet = pd.merge(entreprise_value_sheet, result[['Avg_month_price', 'Year']], on='Year',
                                              how='left')
            entreprise_value_sheet['Market Cap'] = entreprise_value_sheet['Shares'] * entreprise_value_sheet[
                'Avg_month_price']
            entreprise_value_sheet['Earnings_per_share'] = result['Net Income'] / result['Shares']
            entreprise_value_sheet['Price_to_earnings'] = entreprise_value_sheet['Avg_month_price'] / \
                                                          entreprise_value_sheet['Earnings_per_share']
            # This isn’t an exact calculation, because the amount of debt you carry over the course of the year can vary.
            # (If you want to be more precise, calculate the average amount of debt you carried for the year across all four quarters.)
            entreprise_value_sheet['Cost of debt'] = result['Interest Expense'] / result['Total Liab']

            entreprise_value_sheet['Entrerprise Value'] = entreprise_value_sheet['Market Cap'] + entreprise_value_sheet[
                'Debt'] - \
                                                          entreprise_value_sheet['Excess Cash']
            entreprise_value_sheet['Ev / Ebitda'] = entreprise_value_sheet['Entrerprise Value'] / \
                                                    entreprise_value_sheet['EBITDA']
            entreprise_value_sheet['Net Debt / Ebitda'] = entreprise_value_sheet['Debt'] / entreprise_value_sheet[
                'EBITDA']
            entreprise_value_sheet = Format_Table(entreprise_value_sheet)

            cash_flow_sheet = pd.DataFrame()

            cash_flow_sheet['Date'] = result['Date']
            cash_flow_sheet['Month'] = cash_flow_sheet['Date'].dt.month
            cash_flow_sheet['CFO'] = result['Total Cash From Operating Activities']
            cash_flow_sheet['CFO_change'] = np.log(cash_flow_sheet['CFO'] / cash_flow_sheet['CFO'].shift(-1))
            cash_flow_sheet['CAPEX'] = result['Capital Expenditures'] * (-1)
            cash_flow_sheet['CAPEX_change'] = np.log(cash_flow_sheet['CAPEX'] / cash_flow_sheet['CAPEX'].shift(-1))
            cash_flow_sheet['CAPEX_to_CFO_Ratio'] = cash_flow_sheet['CAPEX_change'] / cash_flow_sheet['CFO_change']
            cash_flow_sheet['Net Borrowings'] = result['Net Borrowings']
            cash_flow_sheet['WC'] = result['Working Capital']
            cash_flow_sheet['Change in WC'] = cash_flow_sheet['WC'] - cash_flow_sheet['WC'].shift(-1)
            cash_flow_sheet['FCFE'] = cash_flow_sheet['CFO'] - cash_flow_sheet['CAPEX'] + cash_flow_sheet[
                'Net Borrowings']
            cash_flow_sheet['Shares'] = entreprise_value_sheet['Shares']
            cash_flow_sheet['Shares Chg.'] = np.log(cash_flow_sheet['Shares'] / cash_flow_sheet['Shares'].shift(-1))
            cash_flow_sheet['FCFE/Shr'] = cash_flow_sheet['FCFE'] / cash_flow_sheet['Shares']
            cash_flow_sheet['Avg_month_price'] = result['Avg_month_price']
            cash_flow_sheet['FCFE Yield'] = cash_flow_sheet['FCFE/Shr'] / cash_flow_sheet['Avg_month_price']

            # The following Nopat, Invested Capital are just to compute ROIC. But it seems ROIC is being
            # Computed in a non-uniform way, since each data source on the internet have a different number for this value
            # This should be a point for further development with Damodaran method in the future

            cash_flow_sheet['Nopat'] = result['Total Cash From Operating Activities'] * (1 - 0.35)
            cash_flow_sheet['Invested Capital'] = result['Working Capital'] + result['Property Plant Equipment'] + \
                                                  result[
                                                      'Intangible Assets']
            cash_flow_sheet['ROIC'] = cash_flow_sheet['Nopat'] / cash_flow_sheet['Invested Capital']
            cash_flow_sheet['ROE'] = result['Net Income'] / (result['Total Assets'] - result['Total Liab'])
            cash_flow_sheet = Format_Table(cash_flow_sheet)

            self.entreprise_value_sheet = entreprise_value_sheet
            self.cash_flow_sheet = cash_flow_sheet
            self.result = result
            self.symbol = ticker
            print("{} finished".format(ticker))

        except:
            print("KeyError stage with {}".format(ticker))