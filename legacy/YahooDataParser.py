import pandas as pd
import numpy as np
import datetime as dt
import time

def yahoo_data_parser(ticker, start, end):
    data = pd.DataFrame()
    # data = web.get_data_yahoo(ticker).dropna()
    start_year = start[0]
    start_month = start[1]
    start_day = start[2]

    end_year = end[0]
    end_month = end[1]
    end_day = end[2]


    period1 = int(time.mktime(dt.datetime(start_year, start_month, start_day).timetuple()))
    period2 = int(time.mktime(dt.datetime(end_year, end_month, end_day).timetuple()))
    interval = '1d'  # 1d, 1m
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    data = pd.read_csv(query_string).dropna()

    data['Close'] = data['Adj Close']
    data.drop(['Adj Close'], axis=1)

    # Calculates the log returns of the stock (i.e., the benchmark investment).
    data['Returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data.dropna(inplace=True)

    # Calculates the annualized volatility for the strategy and the benchmark investment.
    data['Volatility'] = data['Returns'].rolling(252).std() * 252 ** 0.5

    #     data['Date'] = data['Date'].astype(str)

    data['Date'] = pd.to_datetime(data['Date'], format="%Y/%m/%d", errors='coerce')

    data['Month'] = data['Date'].dt.month
    data['Year'] = data['Date'].dt.year
    #     data['Date'] = data.index
    data['Avg_month_price'] = data.groupby([(data.Year), (data.Month)])['Adj Close'].transform('mean')
    data['Avg_month_volatility'] = data.groupby([(data.Year), (data.Month)])['Volatility'].transform('mean')
    return data