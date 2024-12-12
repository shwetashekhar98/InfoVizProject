import dash
from dash import dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
import os
import random
import time

# Cache file path
cache_file = "bubble_chart_stock_data.csv"

# Fetch and cache stock data
def fetch_stock_data():
    if os.path.exists(cache_file):
        # Load cached data and ensure Date column is parsed as datetime
        df = pd.read_csv(cache_file)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure proper datetime conversion
    else:
        # Fetch new data
        tickers = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']
        all_data = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                time.sleep(random.uniform(1, 3))  # Randomized delay to avoid rate limits
                hist = stock.history(period="1y")
                if not hist.empty:
                    hist['Ticker'] = ticker
                    hist['Date'] = hist.index
                    hist['Daily Return'] = hist['Close'].pct_change()
                    hist['Volatility'] = hist['Daily Return'].rolling(window=20).std()
                    hist['Market Cap'] = stock.info.get('marketCap', np.nan)
                    hist['P/E Ratio'] = stock.info.get('trailingPE', np.nan)
                    hist['YTD Performance'] = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                    all_data.append(hist[['Date', 'Ticker', 'Close', 'Volatility', 'Market Cap', 'P/E Ratio', 'YTD Performance']])
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")

        # Combine data and cache it
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv(cache_file, index=False)
        else:
            df = pd.DataFrame()

    return df

# Load data
df = fetch_stock_data()

# Ensure Date column is datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Prepare data for animation
df = df.dropna(subset=['Volatility', 'P/E Ratio', 'Market Cap'])  # Drop rows with missing key metrics

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.Div([
        
        html.P(
            "🔍 Explore how stocks perform across time in terms of risk (volatility) and valuation (P/E Ratio). "
            "Use this animation to identify which stocks strike the right balance between market cap, performance, "
            "and risk.",
            style={
                'text-align': 'center',
                'font-size': '18px',
                'color': '#ffffff',
                'padding': '10px',
                'margin': '10px 0',
            }
        )
    ], style={'background-color': '#2e3b4e', 'border-radius': '10px', 'padding': '20px', 'margin-left': '55%'}),

    html.Div([
        dcc.Dropdown(
            id='ticker-filter',
            options=[{'label': ticker, 'value': ticker} for ticker in df['Ticker'].unique()],
            value=df['Ticker'].unique().tolist(),
            multi=True,
            placeholder="Select one or more stocks",
            style={"width": "50%", "margin": "20px auto"}
        ),
        dcc.Graph(
            id='bubble-chart-animation',
            config={'displayModeBar': False}  # Disable the mode bar for a cleaner look
        )
    ]),

    html.Div(id='key-insights', style={
        'margin': '20px',
        'padding': '20px',
        'background': '#f9f9f9',
        'border-radius': '10px',
        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)',
        'font-size': '16px',
        'color': '#333'
    })
])

@app.callback(
    [Output('bubble-chart-animation', 'figure'),
     Output('key-insights', 'children')],
    Input('ticker-filter', 'value')
)
def render_bubble_chart(selected_tickers):
    # Filter data based on selected tickers
    filtered_df = df[df['Ticker'].isin(selected_tickers)]
    
    if filtered_df.empty:
        return {}, html.Div("No data available for the selected tickers.", style={'color': 'red', 'text-align': 'center'})

    # Create Bubble Chart Animation
    fig = px.scatter(
        filtered_df,
        x='P/E Ratio',
        y='Volatility',
        size='Market Cap',
        color='YTD Performance',
        hover_name='Ticker',
        text='Ticker',
        animation_frame=filtered_df['Date'].dt.strftime('%Y-%m-%d'),  # Format as YYYY-MM-DD
        title="How Do Stocks Compare in Valuation (P/E Ratio) and Risk (Volatility) Over Time?",
        labels={
            'P/E Ratio': 'Price-to-Earnings Ratio',
            'Volatility': 'Volatility (Risk)',
            'Market Cap': 'Market Capitalization',
            'YTD Performance': 'YTD Performance (%)'
        },
        size_max=50,
        color_continuous_scale='Viridis',
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_title="Price-to-Earnings (P/E) Ratio",
        yaxis_title="Volatility (Risk)",
        coloraxis_colorbar=dict(title="YTD Performance (%)"),
        hovermode="closest"
    )

    fig.update_traces(
        textposition='middle center',
        marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey'))
    )

    # Generate Dynamic Insights
    latest_date = filtered_df['Date'].max()
    latest_data = filtered_df[filtered_df['Date'] == latest_date]

    highest_performance_stock = latest_data.loc[latest_data['YTD Performance'].idxmax()]
    largest_market_cap_stock = latest_data.loc[latest_data['Market Cap'].idxmax()]
    lowest_risk_stock = latest_data.loc[latest_data['Volatility'].idxmin()]

    insights = [
        html.H3("📌 Key Insights", style={'color': '#333', 'margin-bottom': '10px'}),
        html.Ul([
            html.Li(f"🚀 Stock with the highest YTD performance: {highest_performance_stock['Ticker']} "
                    f"({highest_performance_stock['YTD Performance']:.2f}%)"),
            html.Li(f"💰 Stock with the largest market capitalization: {largest_market_cap_stock['Ticker']} "
                    f"(${largest_market_cap_stock['Market Cap']:,})"),
            html.Li(f"🛡️ Stock with the lowest volatility (risk): {lowest_risk_stock['Ticker']} "
                    f"(Volatility: {lowest_risk_stock['Volatility']:.2f})")
        ])
    ]

    return fig, insights


if __name__ == '__main__':
    app.run_server(debug=True, port=8059)
