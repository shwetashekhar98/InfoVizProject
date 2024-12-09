import numpy as np

def calculate_risk_return(df):
    df['Daily Return'] = df.groupby('Ticker')['Close'].pct_change()
    df['Volatility'] = df.groupby('Ticker')['Daily Return'].transform(lambda x: np.std(x) * np.sqrt(252))
    df['Annual Return'] = df.groupby('Ticker')['Close'].transform(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    return df[['Ticker', 'Annual Return', 'Volatility']].drop_duplicates()

def prepare_sparkline_data(df, ticker):
    return df[df['Ticker'] == ticker][['Date', 'Close']].sort_values(by='Date')
