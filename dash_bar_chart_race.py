from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

# List of company tickers
companies = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']

# Data for 10-year bar chart race
bar_chart_data = []
for ticker in companies:
    stock = yf.Ticker(ticker)
    sector = stock.info.get('sector', 'Unknown')
    hist = stock.history(period="10y")
    if not hist.empty:
        for date, row in hist.iterrows():
            bar_chart_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Symbol': ticker,
                'Sector': sector,
                'Open': row['Open'],
                'Close': row['Close'],
                'High': row['High'],
                'Low': row['Low'],
                'Volume': row['Volume'],
                'Daily Change %': ((row['Close'] - row['Open']) / row['Open']) * 100,
            })

bar_chart_df = pd.DataFrame(bar_chart_data)
bar_chart_df['Year'] = pd.to_datetime(bar_chart_df['Date']).dt.year
yearly_data = bar_chart_df.groupby(['Year', 'Symbol']).agg({
    'Daily Change %': 'mean'
}).reset_index()

def create_bar_chart_race(dataframe):
    fig = px.bar(
        dataframe,
        x='Daily Change %',
        y='Symbol',
        color='Symbol',
        animation_frame='Year',
        orientation='h',
        text='Daily Change %',
        title='10-Year Bar Chart Race: Percentage Change by Company',
        template="plotly_white"
    )
    fig.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside'
    )
    fig.update_layout(
        xaxis_title="Percentage Change (%)",
        yaxis_title="Company Symbol",
        xaxis=dict(range=[-1, 1]),
        height=600,
        margin=dict(l=50, r=50, t=70, b=100),
        font=dict(color='white'),
        plot_bgcolor='black',
        paper_bgcolor='black'
    )
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2000
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 1000
    return fig

# Data for 1-year stock price bar chart race
price_race_data = []
for ticker in companies:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    if not hist.empty:
        for date, row in hist.iterrows():
            price_race_data.append({'Date': date, 'Ticker': ticker, 'Close': row['Close']})

price_race_df = pd.DataFrame(price_race_data)
price_race_df['Date'] = pd.to_datetime(price_race_df['Date'])
date_range = pd.date_range(start=price_race_df['Date'].min(), end=price_race_df['Date'].max())

pivot_df = price_race_df.pivot(index='Date', columns='Ticker', values='Close').reindex(date_range)
pivot_df = pivot_df.ffill()

price_race_df = pivot_df.reset_index().melt(id_vars='index', value_name='Close', var_name='Ticker')
price_race_df.rename(columns={'index': 'Date'}, inplace=True)
price_race_df = price_race_df.sort_values(by=['Date', 'Close'], ascending=[True, False])
x_max = price_race_df['Close'].max() * 1.2

def create_price_bar_chart_race(dataframe):
    fig = px.bar(
        dataframe,
        x='Close',
        y='Ticker',
        color='Ticker',
        animation_frame=dataframe['Date'].dt.strftime('%Y-%m-%d'),
        labels={'Close': 'Stock Price', 'Ticker': 'Stock Ticker'},
        template="plotly_white",
        orientation='h',
        text='Close'
    )
    fig.update_layout(
        xaxis=dict(title="Stock Price", range=[0, x_max], tickformat=".2f"),
        yaxis_title="Stock Ticker",
        legend_title="Stock Ticker",
        showlegend=False,
        hovermode="closest",
        title_x=0.5
    )
    fig.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        cliponaxis=False,
        marker_line_width=0.5
    )
    return fig
    
csv_file_path = "grouped_bar_chart.csv"

# Check if the CSV file exists
if os.path.exists(csv_file_path):
    print("Reading data from CSV file...")
    df = pd.read_csv(csv_file_path)
else:
    # Additional logic for percentage changes over different time periods
    today = datetime.today()
    time_periods = {"Yesterday": today - timedelta(days=1)}
    
    data = []
    for ticker in companies:
        stock = yf.Ticker(ticker)
        sector = stock.info.get('sector', 'Unknown')
    
        for period_name, start_date in time_periods.items():
            end_date = today if period_name != "Yesterday" else start_date + timedelta(days=1)
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
    
    df = pd.DataFrame(data)
    
# Add derived columns for "6 Months Change %" and "3 Months Change %"
df["6 Months Change %"] = df["52 Week Change %"] * 0.6
df["3 Months Change %"] = df["52 Week Change %"] * 0.3

# Filter data for "Yesterday"
filtered_data = df[df['Time Period'] == 'Yesterday']

def create_grouped_bar_chart(dataframe):
    # Check if the dataframe is empty and handle missing data gracefully
    if dataframe.empty:
        print("Input dataframe is empty. Returning an empty figure.")
        return go.Figure()
    
    fig = go.Figure()
    
    # Add 1 Year Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['52 Week Change %'],
        name='1 Year Change %',
        marker_color='blue',
        text=dataframe['52 Week Change %'].round(2),
        textposition='outside'
    ))
    
    # Add 6 Months Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['6 Months Change %'],
        name='6 Months Change %',
        marker_color='green',
        text=dataframe['6 Months Change %'].round(2),
        textposition='outside'
    ))
    
    # Add 3 Months Change
    fig.add_trace(go.Bar(
        x=dataframe['Symbol'],
        y=dataframe['3 Months Change %'],
        name='3 Months Change %',
        marker_color='orange',
        text=dataframe['3 Months Change %'].round(2),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Changes by Time Period (Grouped)",
        xaxis_title="Company Symbol",
        yaxis_title="Percentage Change (%)",
        barmode='group',
        template="plotly_white",
        height=650,
        margin=dict(l=50, r=50, t=70, b=100),
        yaxis=dict(range=[-1.1, 1.1], dtick=0.2),
        xaxis=dict(tickangle=-45),
        legend=dict(title="Time Periods", orientation="h", yanchor="bottom", y=1.02),
        showlegend=True
    )
    
    return fig
# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
   html.H3("Stock Price Bar Chart Race", style={'textAlign': 'center'}),
   dcc.Graph(
       id='price-bar-chart-race',
       figure=create_price_bar_chart_race(price_race_df)
   ),
   html.H3("Bar Chart Race: Percentage Change", style={'textAlign': 'center'}),
   dcc.Graph(
       id='bar-chart-race',
       figure=create_bar_chart_race(yearly_data)
       
   ),
   html.Div([
   html.H3("📊 Insights on Stock Price Comparisons",
            style={"color": "white", "font-size": "26px", "margin-bottom": "10px"}),
   html.P("Do you think comparing the stock prices of one stock with another would give any insight?",
           style={"color": "#f0f0f0", "font-size": "18px", "margin-bottom": "10px"}),
   html.P("Here, it might seem as the stock with the higher price is a good stock when seen in the animated bar race, "
           "but in fact, stock price comparison does not tell about the performance of the stock.",
           style={"color": "#f0f0f0", "font-size": "18px", "margin-bottom": "10px"}),
   html.P("This chart works as a deceptive visualization, making us perceive that the higher the stock price, the better it is performing. "
           "However, to compare stock prices effectively, Percentage Change is a better and more accurate tool.",
           style={"color": "#f0f0f0", "font-size": "18px", "margin-bottom": "10px"}),
   html.P("Stock prices reflect absolute values and are influenced by share structures (e.g., splits), making them hard to compare across companies. "
           "Percentage changes normalize performance, showing relative growth or decline, and enable meaningful comparisons regardless of the stock's price or market size.",
           style={"color": "#f0f0f0", "font-size": "18px"})
], style={
    "background": "linear-gradient(to right, #ff7e5f, #feb47b)",
    "color": "white",
    "padding": "40px",
    "border-radius": "12px",
    "text-align": "center",
    "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
    "max-width": "80%",
    "margin": "20px auto",
    "line-height": "1.6"
}),

   

   
   html.H3("Percentage Changes by Time Period", style={'textAlign': 'center'}),
   dcc.Graph(
       id='grouped-bar-chart',
       figure=create_grouped_bar_chart(filtered_data)
   )
])

if __name__ == '__main__':
   app.run_server(debug=True, port=8061)
