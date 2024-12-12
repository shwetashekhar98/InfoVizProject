from dash import Dash, dash_table, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import os

# CSV File Path
csv_file_path = "stock_sparkline.csv"

def load_and_update_data():
    try:
        if os.path.exists(csv_file_path):
            return pd.read_csv(csv_file_path)

        # Define time periods
        today = datetime.today()
        time_periods = {
            "1 Year": today - timedelta(days=365),
            "Yesterday": today - timedelta(days=2),
        }
        # List of company tickers
        companies = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']

        # Initialize an empty list to store data
        data = []

        # Fetch data for each company and time period
        for ticker in companies:
            stock = yf.Ticker(ticker)
            sector = stock.info.get('sector', 'Unknown')

            for period_name, start_date in time_periods.items():
                end_date = today if period_name != "Yesterday" else start_date + timedelta(days=2)
                hist = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

                if not hist.empty:
                    for date, row in hist.iterrows():
                        data.append({
                            'Time Period': period_name,
                            'Date': date.strftime('%Y-%m-%d'),
                            'Symbol': ticker,
                            'Sector': sector,
                            'Open': row['Open'],
                            'Close': row['Close'],
                            'High': row['High'],
                            'Low': row['Low'],
                            'Volume': row['Volume'],
                            '52 Week Change %': stock.info.get('52WeekChange', None),
                        })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Save to CSV file
        df.to_csv(csv_file_path, index=False)
        return df

    except Exception as e:
        if os.path.exists(csv_file_path):
            return pd.read_csv(csv_file_path, parse_dates=['Date'])
        else:
            return pd.DataFrame()

# Load the data
df = load_and_update_data()

# Filter data for "Yesterday" and "1 Year"
yesterday_data = df[df['Time Period'] == 'Yesterday']
one_year_data = df[df['Time Period'] == '1 Year']

# Create Dash app
app = Dash(__name__)

# Define Dash layout
app.layout = html.Div([
    # DataTable
    dash_table.DataTable(
    id='stock-table',
    columns=[{"name": col, "id": col} for col in yesterday_data.columns] + [{"name": "Analyst Decision", "id": "Analyst Decision"}],
    data=[],
    row_selectable='single',
    style_table={
    'overflowY': 'scroll',  # Enables vertical scrolling
    'margin': '20px',
    'width': '100%',
    'maxHeight': '100%',  # Set a maximum height for the table
    'tableLayout': 'fixed',  # Ensures table columns are constrained to fit within the width
    },
    style_cell={
        'textAlign': 'center',
        'padding': '10px',
        'whiteSpace': 'normal',
    },
    style_header={
        'backgroundColor': 'black',
        'color': 'white',
        'fontWeight': 'bold'
    },
    style_data_conditional=[
        {
            'if': {'filter_query': '{52 Week Change %} < 0', 'column_id': '52 Week Change %'},
            'backgroundColor': 'red',
            'color': 'white'
        }
    ],
    ),


    # Sparkline Container
    html.Div(
        id='sparkline-container',
        style={
            'marginTop': '20px',
            'padding': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'display': 'block',
            'width': '100%',
        },
        children=[
            html.Div("Select a row to display the sparkline.", style={
                'textAlign': 'center', 'color': 'gray', 'fontSize': '16px'
            })
        ]
    ),

    # Insights Section
    html.Div(
        id='insights-section',
        style={
            'marginTop': '20px',
            'padding': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'width': '100%',
            'backgroundColor': '#222',
            'color': 'white',
        },
        children=[
            html.Div("Insights and conclusions will be displayed here.", style={
                'textAlign': 'center', 'fontSize': '16px'
            })
        ]
    ),
], style={
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif',
    'maxWidth': '1400px',
    'margin': '0 auto',
})


def create_sparkline_graph(symbol_data, ticker):
    fig = go.Figure()

    # Add the trace for the Close price
    fig.add_trace(go.Scatter(
        x=symbol_data["Date"],
        y=symbol_data["Close"],
        mode='lines+markers',
        line=dict(color='blue'),
        marker=dict(size=8, symbol='circle'),
        name="Close",
    ))

    # Add frames for animation
    frames = [
        dict(
            data=[go.Scatter(
                x=symbol_data.iloc[:k + 1]["Date"],
                y=symbol_data.iloc[:k + 1]["Close"],
                mode='lines+markers',
                line=dict(color='blue'),
                marker=dict(size=8),
            )],
        )
        for k in range(len(symbol_data))
    ]
    fig.frames = frames

    # Layout settings for animation
    fig.update_layout(
        title=f"Trend for: {ticker}",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_white",
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]),
                ],
            )
        ],
    )
    return fig

@app.callback(
    [Output('stock-table', 'data'),
     Output('sparkline-container', 'children'),
     Output('insights-section', 'children')],
    [Input('stock-table', 'selected_rows')]
)
def update_table_and_content(selected_rows):
    # Adding Analyst Decision directly into the table
    df_with_decision = yesterday_data.copy()
    df_with_decision["Analyst Decision"] = df_with_decision.apply(
        lambda row: "Consider Buying" if row.get("52 Week Change %", 0) > 0.05 else "Consider Holding",
        axis=1
    )

    if not selected_rows:
        return (
            df_with_decision.to_dict('records'),
            html.Div(
                "Select a row to see the sparkline.",
                style={'textAlign': 'center', 'color': 'gray', 'fontSize': '16px'}
            ),
            html.Div("No data available for insights and conclusion.")
        )

    selected_row = df_with_decision.iloc[selected_rows[0]]
    symbol = selected_row['Symbol']
    symbol_data = one_year_data[one_year_data['Symbol'] == symbol].copy()

    if symbol_data.empty:
        return (
            df_with_decision.to_dict('records'),
            html.Div(
                "No data available for sparkline.",
                style={'textAlign': 'center', 'color': 'gray', 'fontSize': '16px'}
            ),
            html.Div("No data available for insights and conclusion.")
        )

    # Generate sparkline graph
    figure = create_sparkline_graph(symbol_data, ticker=symbol)

    # Calculate insights
    highest_close = symbol_data['Close'].max()
    lowest_close = symbol_data['Close'].min()
    avg_close = symbol_data['Close'].mean()
    total_volume = symbol_data['Volume'].sum()
    percentage_change = ((symbol_data['Close'].iloc[-1] - symbol_data['Close'].iloc[0]) / symbol_data['Close'].iloc[0]) * 100

    insights = html.Div([
        html.H4(f"Key Insights for {symbol}", style={'marginTop': '20px', 'color': 'white'}),
        html.Ul([
            html.Li(f"Highest Closing Price: ${highest_close:.2f}", style={'color': 'white'}),
            html.Li(f"Lowest Closing Price: ${lowest_close:.2f}", style={'color': 'white'}),
            html.Li(f"Average Closing Price: ${avg_close:.2f}", style={'color': 'white'}),
            html.Li(f"Total Trading Volume: {total_volume:,}", style={'color': 'white'}),
            html.Li(f"Percentage Change Over Period: {percentage_change:.2f}%", style={'color': 'white'})
        ], style={'fontSize': '16px', 'color': 'white'}),
        html.H4("Conclusion", style={'marginTop': '20px', 'color': 'white'}),
        html.P(
            f"The stock {symbol} showed a {'positive' if percentage_change > 0 else 'negative'} trend over the past year, "
            f"with a highest closing price of ${highest_close:.2f} and a lowest closing price of ${lowest_close:.2f}. "
            f"The average closing price during this period was ${avg_close:.2f}.",
            style={'fontSize': '16px', 'color': 'white'}
        )
    ])

    return (
        df_with_decision.to_dict('records'),
        dcc.Graph(
            figure=figure,
            config={'displayModeBar': True},
            style={'height': '500px', 'width': '100%'}
        ),
        insights
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8062)
