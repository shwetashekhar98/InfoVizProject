import dash
from dash import dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Risk and Return Data Preparation
stocks = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']
risk_return_data = []
for stock in stocks:
    ticker = yf.Ticker(stock)
    hist = ticker.history(period="1y")

    # Calculate returns and risk (volatility)
    annual_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
    volatility = hist['Close'].pct_change().std() * np.sqrt(252)

    risk_return_data.append({
        'Ticker': stock,
        'Annual Return': annual_return,
        'Volatility': volatility
    })

risk_return_df = pd.DataFrame(risk_return_data)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.Div([
       
        html.P(
            "🔍 Explore the trade-offs between risk and return for different stocks. "
            "Use this interactive tool to identify opportunities and align your portfolio with your financial goals.",
            style={
                'text-align': 'center',
                'font-size': '18px',
                'color': 'white',
                'padding': '10px 0',
                'margin': '10px 0',
            }
        )
    ]),

    html.Div([
        dcc.Dropdown(
            id='stock-filter',
            options=[{'label': stock, 'value': stock} for stock in stocks],
            value=[],
            multi=True,
            placeholder="Select one or more stocks to analyze 🔎",
            style={
                "width": "50%",
                "margin": "auto",
                'font-size': '16px',
                'padding': '5px'
            }
        ),

        dcc.Graph(id='risk-return-bubble-matrix')
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

# Callback to update Risk-Return Bubble Matrix
@app.callback(
    [Output('risk-return-bubble-matrix', 'figure'),
     Output('key-insights', 'children')],
    [Input('stock-filter', 'value')]
)
def update_risk_return_bubble_matrix(selected_stocks):
    if not selected_stocks:
        selected_stocks = stocks

    filtered_df = risk_return_df[risk_return_df['Ticker'].isin(selected_stocks)]

    # Create Bubble Matrix
    fig = px.scatter(
        filtered_df,
        x='Volatility',
        y='Annual Return',
        size='Volatility',  # Bubble size based on Volatility
        color='Annual Return',
        hover_name='Ticker',
        labels={
            'Volatility': 'Risk (Volatility)',
            'Annual Return': 'Return (%)'
        },
        title="Risk-Return Bubble Matrix",
        template="plotly_white",
        text=filtered_df['Ticker']  # Add Ticker inside the bubbles
    )

    fig.update_traces(
        marker=dict(opacity=0.8, sizemode='area'),
        textposition='middle center'  # Position text inside the bubble
    )

    # Generate dynamic insights
    if not filtered_df.empty:
        highest_return_stock = filtered_df.loc[filtered_df['Annual Return'].idxmax()]
        lowest_risk_stock = filtered_df.loc[filtered_df['Volatility'].idxmin()]
        balanced_stock = filtered_df.loc[(filtered_df['Annual Return'] / filtered_df['Volatility']).idxmax()]

        insights = [
            html.H3("📌 Key Insights", style={'color': '#333', 'margin-bottom': '10px'}),
            html.Ul([
                html.Li(f"🚀 Stock with the highest annual return: {highest_return_stock['Ticker']} "
                        f"({highest_return_stock['Annual Return']:.2f}%)"),
                html.Li(f"🛡️ Stock with the lowest risk: {lowest_risk_stock['Ticker']} "
                        f"(Volatility: {lowest_risk_stock['Volatility']:.2f})"),
                html.Li(f"⚖️ Stock with the best risk-return balance: {balanced_stock['Ticker']} "
                        f"(Return-to-Risk Ratio: {balanced_stock['Annual Return'] / balanced_stock['Volatility']:.2f})")
            ])
        ]
    else:
        insights = [html.P("No data available for the selected stocks.", style={'color': 'red'})]

    return fig, insights


if __name__ == '__main__':
    app.run_server(debug=True, port=8057)
