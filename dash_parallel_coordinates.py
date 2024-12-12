import dash
from dash import dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
import os
import time
import random

# Fetch stock data
stocks = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']
data = []

# Cache file path
cache_file = "stock_data_cache.csv"

# Check if cached data exists
if os.path.exists(cache_file):
    df = pd.read_csv(cache_file)
else:
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            time.sleep(random.uniform(1, 3))  # Randomized delay to avoid rate limits
            info = ticker.info
            hist = ticker.history(period="1y")

            # Calculate metrics
            if not hist.empty:
                hist['Daily Return'] = hist['Close'].pct_change()
                volatility = hist['Daily Return'].std() * np.sqrt(252)  # Annualized volatility
                ytd_performance = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100

                data.append({
                    'Ticker': stock,
                    'PE_Ratio': info.get('trailingPE', np.nan),
                    'Volatility': volatility,
                    'Market_Cap': info.get('marketCap', np.nan),
                    'YTD_Performance': ytd_performance
                })
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")

    # Combine data into DataFrames and save cache
    df = pd.DataFrame(data)
    df.to_csv(cache_file, index=False)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Stock Analytics Dashboard", style={'text-align': 'center'}),

    # Key Metrics Definitions Section
    html.Div([
        html.H2("Key Metrics Definitions", style={'text-align': 'center'}),
        html.Div([
            html.Div([
                html.A(
                    html.Img(src="/assets/pe_ratio.png", style={'width': '50px', 'margin-bottom': '10px'}),
                    href="/assets/pe_ratio.png",
                    target="_blank"
                ),
                html.H3("P/E Ratio", style={'text-align': 'center', 'margin-bottom': '10px'}),
                html.P("""
                The P/E ratio (Price-to-Earnings ratio) is a financial metric used to assess a company's valuation 
                by comparing its stock price to its earnings.
                """, style={'text-align': 'center', 'font-size': '14px'}),
                html.P("Formula: Market Price per Share / Earnings per Share (EPS).", style={'text-align': 'center', 'font-size': '14px'})
            ], style={'border': '1px solid #ccc', 'padding': '15px', 'margin': '10px', 'background-color': '#f7f7f7',
                      'border-radius': '10px'}),
            html.Div([
                html.A(
                    html.Img(src="/assets/market_cap.png", style={'width': '50px', 'margin-bottom': '10px'}),
                    href="/assets/market_cap.png",
                    target="_blank"
                ),
                html.H3("Market Cap", style={'text-align': 'center', 'margin-bottom': '10px'}),
                html.P("""
                Market cap represents the total value of a company’s outstanding shares.
                """, style={'text-align': 'center', 'font-size': '14px'}),
                html.P("Formula: Stock Price × Total Outstanding Shares.", style={'text-align': 'center', 'font-size': '14px'})
            ], style={'border': '1px solid #ccc', 'padding': '15px', 'margin': '10px', 'background-color': '#f7f7f7',
                      'border-radius': '10px'}),
            html.Div([
                html.A(
                    html.Img(src="/assets/ytd_performance.png", style={'width': '50px', 'margin-bottom': '10px'}),
                    href="/assets/ytd_performance.png",
                    target="_blank"
                ),
                html.H3("YTD Performance", style={'text-align': 'center', 'margin-bottom': '10px'}),
                html.P("""
                YTD performance measures the stock's price change from the beginning of the year to the current date.
                """, style={'text-align': 'center', 'font-size': '14px'}),
                html.P("Formula: (Current Price - Start of Year Price) / Start of Year Price × 100.", style={'text-align': 'center', 'font-size': '14px'})
            ], style={'border': '1px solid #ccc', 'padding': '15px', 'margin': '10px', 'background-color': '#f7f7f7',
                      'border-radius': '10px'}),
        ], style={'display': 'flex', 'justify-content': 'center', 'flex-wrap': 'wrap'})
    ]),

    # Parallel Coordinates Chart Section
    html.Div([
        html.H2("Parallel Coordinates", style={'text-align': 'center'}),
        dcc.Dropdown(
            id='parallel-stock-filter',
            options=[{'label': stock, 'value': stock} for stock in stocks],
            value=stocks,
            multi=True,
            placeholder="Select one or more stocks",
            style={"width": "50%", "margin": "20px auto"}
        ),
        dcc.Graph(id='parallel-coordinates-chart', style={'margin': '20px auto', 'width': '90%'}),
        html.Div(id='dynamic-insights', style={
            'margin': '20px auto',
            'padding': '20px',
            'background-color': '#f7f7f7',
            'border-radius': '10px',
            'box-shadow': '2px 2px 8px rgba(0,0,0,0.1)',
            'width': '90%',
            'font-size': '16px',
            'line-height': '1.6'
        })
    ])
])

# Callback for Parallel Coordinates Chart and Insights
@app.callback(
    [Output('parallel-coordinates-chart', 'figure'),
     Output('dynamic-insights', 'children')],
    Input('parallel-stock-filter', 'value')
)
def update_parallel_chart(selected_stocks):
    filtered_df = df[df['Ticker'].isin(selected_stocks)]

    # Parallel Coordinates Chart
    fig = px.parallel_coordinates(
        filtered_df,
        dimensions=['PE_Ratio', 'Volatility', 'Market_Cap', 'YTD_Performance'],
        color='YTD_Performance',
        labels={
            'PE_Ratio': 'P/E Ratio',
            'Volatility': 'Annualized Volatility',
            'Market_Cap': 'Market Cap',
            'YTD_Performance': 'YTD Performance (%)'
        },
        color_continuous_scale=px.colors.diverging.RdYlGn
    )

    # Dynamic Insights
    insights = []
    if filtered_df.empty:
        insights.append(html.Div("No stocks selected. Please select stocks to view insights.", style={'color': 'red'}))
    else:
        for _, row in filtered_df.iterrows():
            insights.append(html.Div([
                html.H4(row['Ticker'], style={'text-align': 'center', 'color': '#4CAF50'}),
                html.P(f"P/E Ratio: {row['PE_Ratio']:.2f}" if not pd.isna(row['PE_Ratio']) else "P/E Ratio: N/A"),
                html.P(f"Volatility: {row['Volatility']:.2f}" if not pd.isna(row['Volatility']) else "Volatility: N/A"),
                html.P(f"Market Cap: {row['Market_Cap']:,} USD" if not pd.isna(row['Market_Cap']) else "Market Cap: N/A"),
                html.P(f"YTD Performance: {row['YTD_Performance']:.2f}%" if not pd.isna(row['YTD_Performance']) else "YTD Performance: N/A"),
            ], style={
                'border': '1px solid #ccc',
                'border-radius': '10px',
                'padding': '15px',
                'margin': '10px',
                'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)',
                'background-color': '#ffffff',
                'width': '30%',
                'display': 'inline-block',
                'vertical-align': 'top'
            }))

    return fig, html.Div(insights, style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center'})

if __name__ == '__main__':
    app.run_server(debug=True, port=8056)
