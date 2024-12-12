# Save this as dash_bubble_chart.py
import dash
from dash import dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Fetch stock data
stocks = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']
data = []

for stock in stocks:
    ticker = yf.Ticker(stock)
    info = ticker.info
    hist = ticker.history(period="ytd")

    # Calculate metrics
    hist['Daily Return'] = hist['Close'].pct_change()
    volatility = hist['Daily Return'].std() * np.sqrt(252)  # Annualized volatility
    ytd_performance = (hist['Close'][-1] / hist['Close'][0] - 1) * 100 if not hist.empty else np.nan

    data.append({
        'Ticker': stock,
        'PE_Ratio': info.get('trailingPE', np.nan),
        'Volatility': volatility,
        'Market_Cap': info.get('marketCap', np.nan),
        'YTD_Performance': ytd_performance
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Interactive Stock Analysis Dashboard", style={'text-align': 'center'}),

    dcc.Dropdown(
        id='stock-filter',
        options=[{'label': stock, 'value': stock} for stock in stocks] + [{'label': 'All Stocks', 'value': 'ALL'}],
        value='ALL',
        multi=True,
        placeholder="Select one or more stocks",
        style={"width": "50%", "margin": "auto"}
    ),

    dcc.Graph(id='bubble-chart'),
])

# Callback to update bubble chart
@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('stock-filter', 'value')]
)
def update_chart(selected_stocks):
    if not selected_stocks or 'ALL' in selected_stocks:
        filtered_df = df
    else:
        filtered_df = df[df['Ticker'].isin(selected_stocks)]

    fig = px.scatter(
        filtered_df,
        x='PE_Ratio',
        y='Volatility',
        size='Market_Cap',
        color='YTD_Performance',
        hover_name='Ticker',
        labels={"PE_Ratio": "P/E Ratio", "Volatility": "Annualized Volatility"},
        title="P/E Ratio vs Volatility",
        color_continuous_scale='Viridis',
        size_max=60
    )

    fig.update_layout(
        xaxis_title="P/E Ratio",
        yaxis_title="Annualized Volatility",
        coloraxis_colorbar=dict(title="YTD Performance (%)", ticksuffix="%"),
        template="plotly_white"
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8055)
