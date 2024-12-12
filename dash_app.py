from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

# List of company tickers
companies = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']

# Define time periods
today = datetime.today()
time_periods = {"Yesterday": today - timedelta(days=2)}

# Initialize an empty list to store data
data = []

# Fetch data for each company and time period
for ticker in companies:
    stock = yf.Ticker(ticker)
    sector = stock.info.get('sector', 'Unknown')  # Dynamically fetch the sector

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
                    '52 Week Change %': stock.info.get('52WeekChange', 0),
                })

# Convert to DataFrame
df = pd.DataFrame(data)

# Add derived columns for "6 Months Change %" and "3 Months Change %"
df["6 Months Change %"] = df["52 Week Change %"] * 0.6
df["3 Months Change %"] = df["52 Week Change %"] * 0.3

# Filter data for "Yesterday"
filtered_data = df[df['Time Period'] == 'Yesterday']
def create_grouped_bar_chart(dataframe):
    fig = go.Figure()

    # Add 1 Year Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['52 Week Change %'],
        name='1 Year Change %',
        marker_color='blue',
        text=dataframe['52 Week Change %'].round(2),
        textposition='outside',
        insidetextanchor='start',
        textfont=dict(size=12)  # Increased font size for better visibility
    ))

    # Add 6 Months Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['6 Months Change %'],
        name='6 Months Change %',
        marker_color='green',
        text=dataframe['6 Months Change %'].round(2),
        textposition='outside',
        insidetextanchor='start',
        textfont=dict(size=12)
    ))

    # Add 3 Months Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['3 Months Change %'],
        name='3 Months Change %',
        marker_color='orange',
        text=dataframe['3 Months Change %'].round(2),
        textposition='outside',
        insidetextanchor='start',
        textfont=dict(size=12)
    ))

    fig.update_layout(
        title="Changes by Time Period (Grouped)",
        xaxis_title="Company Symbol",
        yaxis_title="Percentage Change (%)",
        barmode='group',
        template="plotly_white",
        height=650,  # Increased height for better text spacing
        margin=dict(l=50, r=50, t=70, b=100),  # Increased bottom and top margins
        yaxis=dict(
            range=[-1.1, 1.1],  # Expanded range slightly for better spacing
            dtick=0.2,  # Control y-axis ticks
            gridcolor="gray",
        ),
        xaxis=dict(
            tickangle=-45,  # Rotate labels for better readability
        ),
        legend=dict(
            title="Time Periods",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    # Prevent text from being clipped
    fig.update_traces(
        marker_line_width=1.5,
        marker_line_color='black',
        cliponaxis=False  # Ensure text is not clipped
    )

    return fig






# Initialize Dash app
app = Dash(__name__)

# Define Dash layout
app.layout = html.Div([
    html.Br(),
    html.H2("Percentage change metric vs Time", style={'textAlign': 'center'}),
    dcc.Graph(
        id='grouped-bar-chart',
        figure=create_grouped_bar_chart(filtered_data)
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8066)


