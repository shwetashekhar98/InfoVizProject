import diskcache as dc
import yfinance as yf
import pandas as pd

# Initialize the shared cache
cache = dc.Cache('./cache')

def fetch_stock_data(tickers, period="1y", interval="1d"):
    data = []
    for ticker in tickers:
        cache_key = f"{ticker}_{period}_{interval}"
        if cache_key in cache:
            hist = cache[cache_key]
        else:
            try:
                hist = yf.download(ticker, period=period, interval=interval)
                cache[cache_key] = hist
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                continue

        if not hist.empty:
            hist['Ticker'] = ticker
            hist['Date'] = hist.index
            data.append(hist.reset_index())

    return pd.concat(data) if data else pd.DataFrame()
