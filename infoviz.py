import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import plotly.express as px
import subprocess
import os
from threading import Thread
import time

import llm_chat
st.set_page_config(layout="wide")
def run_dash_app():
    subprocess.Popen(["python", "dash_app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_sparklines_app():
    subprocess.Popen(["python", "dash_sparklines.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_parallel_coordinates_app():
    subprocess.Popen(["python", "dash_parallel_coordinates.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def run_dash_risk_return_matrix_app():
    subprocess.Popen(["python", "dash_risk_return_matrix.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_bar_chart_race_app():
    subprocess.Popen(["python", "dash_bar_chart_race.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dash_bubble_chart_animation_app():
    subprocess.Popen(["python", "dash_bubble_chart_animation.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Start all Dash apps in the background
run_dash_app()
run_dash_sparklines_app()
run_dash_parallel_coordinates_app()
run_dash_risk_return_matrix_app()
run_dash_bar_chart_race_app()
run_dash_bubble_chart_animation_app()

# Wait for Dash apps to start
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import time
from sklearn.preprocessing import MinMaxScaler
import requests
from bs4 import BeautifulSoup

@st.cache_data
def fetch_stock_data():
    csv_file_path = "stock_trend_data.csv"
    companies = ['CVX', 'BA', 'GM', 'C', 'BAC', 'T', 'CAT', 'F', 'DIS', 'DE']
    today = datetime.today()
    time_periods = {
        "1 Year": today - timedelta(days=365),
        "6 Months": today - timedelta(days=182),
        "3 Months": today - timedelta(days=91),
        "Yesterday": today - timedelta(days=1),
    }

    data = []
    data_fetched = False

    for ticker in companies:
        try:
            # Attempt to fetch data from API
            stock = yf.Ticker(ticker)
            info = stock.info if stock.info else {}
            sector = info.get('sector', 'Unknown')

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
                            'Open': row.get('Open', None),
                            'Close': row.get('Close', None),
                            'High': row.get('High', None),
                            'Low': row.get('Low', None),
                            'Volume': row.get('Volume', None),
                            'Price to Earnings Ratio': info.get('trailingPE', None),
                            'Market Cap': info.get('marketCap', None),
                            'Dividend Yield %': info.get('dividendYield', None),
                            '52 Week Change %': info.get('52WeekChange', None),
                            'Debt to Equity': info.get('debtToEquity', None),
                            'Revenue Growth': info.get('revenueGrowth', None),
                            'Profit Margin': info.get('profitMargins', None),
                        })
            data_fetched = True
            time.sleep(5)  # Wait to prevent hitting rate limit

        except Exception as e:
            st.warning(f"Rate limit hit or other error for {ticker}: {e}. Attempting to scrape data...")

            # Fallback to web scraping
            try:
                url = f"https://finance.yahoo.com/quote/{ticker}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Scrape specific fields
                open_price = soup.find('td', {'data-test': 'OPEN-value'}).text if soup.find('td', {'data-test': 'OPEN-value'}) else None
                close_price = soup.find('td', {'data-test': 'PREV_CLOSE-value'}).text if soup.find('td', {'data-test': 'PREV_CLOSE-value'}) else None
                volume = soup.find('td', {'data-test': 'TD_VOLUME-value'}).text.replace(",", "") if soup.find('td', {'data-test': 'TD_VOLUME-value'}) else None
                high = soup.find('td', {'data-test': 'DAYS_RANGE-value'}).text.split('-')[-1] if soup.find('td', {'data-test': 'DAYS_RANGE-value'}) else None
                low = soup.find('td', {'data-test': 'DAYS_RANGE-value'}).text.split('-')[0] if soup.find('td', {'data-test': 'DAYS_RANGE-value'}) else None
                dividend_yield = soup.find('td', {'data-test': 'DIVIDEND_AND_YIELD-value'}).text.split(' ')[0] if soup.find('td', {'data-test': 'DIVIDEND_AND_YIELD-value'}) else None
                week_change = soup.find('td', {'data-test': '52_WEEK_CHANGE-value'}).text if soup.find('td', {'data-test': '52_WEEK_CHANGE-value'}) else None
                debt_to_equity = soup.find('td', {'data-test': 'DEBT_EQUITY_RATIO-value'}).text if soup.find('td', {'data-test': 'DEBT_EQUITY_RATIO-value'}) else None
                revenue_growth = soup.find('td', {'data-test': 'REVENUE_GROWTH_QTRLY_YOY-value'}).text if soup.find('td', {'data-test': 'REVENUE_GROWTH_QTRLY_YOY-value'}) else None
                profit_margin = soup.find('td', {'data-test': 'PROFIT_MARGIN-value'}).text if soup.find('td', {'data-test': 'PROFIT_MARGIN-value'}) else None

                # Append scraped data
                data.append({
                    'Time Period': 'Scraped',
                    'Date': today.strftime('%Y-%m-%d'),
                    'Symbol': ticker,
                    'Sector': 'Unknown',  # Cannot scrape sector
                    'Open': open_price,
                    'Close': close_price,
                    'High': high,
                    'Low': low,
                    'Volume': volume,
                    'Price to Earnings Ratio': info.get('trailingPE', None),
                    'Market Cap': info.get('marketCap', None),
                    'Dividend Yield %': dividend_yield,
                    '52 Week Change %': week_change,
                    'Debt to Equity': debt_to_equity,
                    'Revenue Growth': revenue_growth,
                    'Profit Margin': profit_margin,
                })
                data_fetched = True
            except Exception as scrape_error:
                st.error(f"Scraping failed for {ticker}: {scrape_error}")

    if data_fetched:
        df = pd.DataFrame(data)
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df.dropna(subset=required_columns, inplace=True)
        df.to_csv(csv_file_path, index=False)
        st.success(f"Data successfully fetched and saved to {csv_file_path}")
        return df
    else:
        if os.path.exists(csv_file_path):
            st.info(f"Using existing data from {csv_file_path}")
            return pd.read_csv(csv_file_path)
        else:
            st.error(f"No data available and no existing CSV file found at {csv_file_path}")
            return pd.DataFrame()




# Normalize metrics for balanced comparison
def normalize_metrics(df, metrics):
    scaler = MinMaxScaler()
    df[metrics] = scaler.fit_transform(df[metrics])
    return df
def highlight_open_close(row):
    styles = []
    for col in row.index:
        if col == 'Close':
            if row['Close'] > row['Open']:
                styles.append('color: green;')
            elif row['Close'] < row['Open']:
                styles.append('color: red;')
            else:
                styles.append('color: black;')
        else:
            styles.append('')
    return styles


# Main Streamlit app


def main():

    
    st.markdown(
    """
    <style>
    .title {
        text-align: center;  /* Center-align the title */
        font-size: 28px;  /* Adjust font size */
        font-weight: bold;  /* Make it bold */
        margin-bottom: 20px;  /* Add spacing below */
        color: white;  /* Ensure good contrast */
        background-color: #222;  /* Background for distinction */
        padding: 10px;  /* Add padding around the title */
        border-radius: 8px;  /* Rounded corners for aesthetics */
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st.markdown('<div class="title">Stock Market Visualization Dashboard</div>', unsafe_allow_html=True)

    # Check for existing CSV file
    csv_file_path = 'stock_trend_data.csv'
    
    if os.path.exists(csv_file_path):
        # Load data from existing CSV file
        #st.info("Loading data from existing CSV file.")
        df = pd.read_csv(csv_file_path)
    else:
        # If no CSV file exists, fetch data
        st.info("Fetching data from API and scraping fallback.")
        df = fetch_stock_data()
        
        if not df.empty:
            df.to_csv(csv_file_path, index=False)
            st.success(f"Data saved to {csv_file_path}")
    
    # Initialize chatbot state
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ✅ Define `df_sample` only if df is properly initialized
    df_sample = df.sample(n=min(100, len(df)))  # Avoid errors if df has <100 rows
    data_json = df_sample.to_json(orient='records')

    # Sidebar Chat History
    with st.sidebar.expander("💬 Chat with AI"):
        for msg in st.session_state.chat_history:
            st.markdown(msg)

        user_input = st.text_input("Ask me anything:")
        if st.button("Send"):
            if user_input:
                st.session_state.chat_history.append(f"**You:** {user_input}")
                llm_response = llm_chat.getResponse(data_json, user_input)  
                st.session_state.chat_history.append(f"🤖 AI: {llm_response}")
                st.rerun()

    # Sidebar for dynamic filters
    tab_selection = st.sidebar.radio("Select Tab", ["Dataset Viewer", "Trend Analysis", "Trend Analysis At A Glance", "Stock Percentage Change Metrics", "Risk Return", "PE Ratio vs Volatility Comparison"])

    if tab_selection == "Dataset Viewer":
        st.header("Filter and View Stock Dataset")
        
        # Filters
        time_period_filter = st.sidebar.selectbox("Select Time Period", ["All"] + list(df["Time Period"].unique()))
        sector_filter = st.sidebar.selectbox("Select Sector", ["All"] + list(df["Sector"].unique()))
        symbol_filter = st.sidebar.multiselect("Select Stock Symbols", df["Symbol"].unique())

        # Apply filters
        filtered_df = df.copy()
        
        if time_period_filter != "All":
            filtered_df = filtered_df[filtered_df["Time Period"] == time_period_filter]
        
        if sector_filter != "All":
            filtered_df = filtered_df[filtered_df["Sector"] == sector_filter]
        
        if symbol_filter:
            filtered_df = filtered_df[filtered_df["Symbol"].isin(symbol_filter)]

        # Display DataFrame with conditional formatting
        styled_df = filtered_df.style.apply(highlight_open_close, axis=1)
        st.dataframe(styled_df)

        # Add a tooltip/explanation below the table
        st.markdown("""
            ### Legend 
            - **Green (Close):** Indicates the stock price closed higher than it opened, signaling an increase in value.
            - **Red (Close):** Indicates the stock price closed lower than it opened, signaling a decrease in value.
            - **Neutral (Close):** Indicates the stock price closed at the same level it opened.
        """)
        
        # Download button for filtered dataset
        st.download_button("Download Dataset", filtered_df.to_csv(index=False), "stock_data.csv")



        
        
                
        

     

    elif tab_selection == "Trend Analysis":
        st.header("Interactive Stock Candlestick Chart for Trend Analysis")
        st.markdown(
            """
          <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 0 auto; 
        padding: 20px;
    ">
        <div style="
            background: linear-gradient(to right, #6a11cb, #2575fc); 
            color: white; 
            padding: 60px; 
            border-radius: 12px; 
            text-align: center; 
            font-size: 26px; 
            font-weight: bold; 
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 1200px; /* Matches iframe's visual area */
            width: 100%;
        ">
            📊 <span style="font-size: 28px;">What are the key trends, price movements, and volatility of the selected stock over the chosen time period, and how can these insights guide investment decisions?💡
        </div>
    </div>
    """,
            unsafe_allow_html=True
        )


        # Sidebar Filters
        st.sidebar.header("Trend Analysis Filters")
        # Check for CSV file
        csv_file_path = 'stock_trend_data.csv'
        if os.path.exists(csv_file_path):
            #st.info("Loading data from existing CSV file.")
            df = pd.read_csv(csv_file_path)
        else:
            #st.info("Fetching data from API and scraping fallback.")
            df = fetch_stock_data()
    
            if not df.empty:
                df.to_csv(csv_file_path, index=False)
                st.success(f"Data saved to {csv_file_path}")
        
        available_tickers = df["Symbol"].unique()  # Unique stock symbols
        ticker = st.sidebar.selectbox("Select Stock Ticker", available_tickers, index=0)
        # Filter out "Yesterday" from available periods
        available_periods = [period for period in df["Time Period"].unique() if period != "Yesterday"]
        period = st.sidebar.selectbox("Select Data Period", available_periods, index=0)

        
       
        
        include_rangeslider = st.sidebar.checkbox("Include Rangeslider", value=True)
        ma_period = st.sidebar.slider("Select Moving Average Period (days)", min_value=5, max_value=50, value=20, step=5)
        
        # Filter the DataFrame for the selected ticker and time period
        filtered_data = df[(df["Symbol"] == ticker) & (df["Time Period"] == period)].copy()
        
        # Check if the filtered data is empty
        if filtered_data.empty:
            st.error(f"No data available for {ticker} in the selected time period ({period}).")
        else:
            try:
                # Ensure 'Date' is sorted and in datetime format
                # Convert 'Date' to datetime format
                filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])
                
                # Sort values by 'Date' and reassign
                filtered_data = filtered_data.sort_values("Date")
                
                # Ensure the 'Close' column is numeric and handle missing values
                filtered_data["Close"] = pd.to_numeric(filtered_data["Close"], errors='coerce')
                
                # Forward-fill missing values in 'Close' and reassign
                filtered_data["Close"] = filtered_data["Close"].ffill()

        
                # Ensure enough data points for rolling calculation
                if len(filtered_data) < ma_period:
                    st.error(f"Not enough data points to calculate a {ma_period}-day moving average.")
                else:
                    # Calculate the moving average
                    filtered_data["Trend"] = filtered_data["Close"].rolling(window=ma_period, min_periods=1).mean()
        
                    # Create candlestick chart
                    fig = go.Figure()
        
                    fig.add_trace(go.Candlestick(
                        x=filtered_data["Date"],
                        open=filtered_data["Open"],
                        high=filtered_data["High"],
                        low=filtered_data["Low"],
                        close=filtered_data["Close"],
                        increasing=dict(line_color='green'),
                        decreasing=dict(line_color='red'),
                        name="Candlestick"
                    ))
        
                    # Add moving average line
                    fig.add_trace(go.Scatter(
                        x=filtered_data["Date"],
                        y=filtered_data["Trend"],
                        mode="lines",
                        line=dict(color="yellow", width=2),
                        name=f"{ma_period}-Day Moving Average"
                    ))
        
                    # Customize layout
                    fig.update_layout(
                        title=f"{ticker} Stock Candlestick Chart with Trend Line ({period})",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        xaxis_rangeslider_visible=include_rangeslider,
                        template="plotly_white",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
        
                    # Display the chart
                    st.plotly_chart(fig)
        
                    # Dynamically calculate insights
                    highest_price = filtered_data["High"].max()
                    lowest_price = filtered_data["Low"].min()
                    avg_close_price = filtered_data["Close"].mean()
                    price_difference = highest_price - lowest_price
                    time_range = f"{filtered_data['Date'].min().strftime('%b %d, %Y')} to {filtered_data['Date'].max().strftime('%b %d, %Y')}"
                    ma_trend = f"{ma_period}-Day Moving Average"
        
                    # Display Key Insights
                    st.markdown(f"""
                    <div style="background-color: #f0f8ff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); margin-bottom: 20px; line-height: 1.6;">
                        <h3 style="color: #333;">📊 Key Insights</h3>
                        <ul style="color: #555; font-size: 16px;">
                            <li>📈 The stock <b>{ticker}</b> recorded a <b>highest price</b> of <b>${highest_price:.2f}</b> during the period <b>{time_range}</b>.</li>
                            <li>📉 The <b>lowest price</b> during this period was <b>${lowest_price:.2f}</b>, indicating potential buying opportunities.</li>
                            <li>💵 The <b>average closing price</b> was <b>${avg_close_price:.2f}</b>, reflecting the stock's typical market behavior.</li>
                            <li>🔄 The <b>price difference</b> of <b>${price_difference:.2f}</b> demonstrates the stock's volatility.</li>
                            <li>📊 The <b>{ma_trend}</b> shows the stock's overall trend, smoothing out short-term fluctuations.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    import base64
        
                    # Add Candlestick Explanation Image
                    with open("assets/candlestick_image.png", "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode()
        
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); margin-bottom: 20px; line-height: 1.6;">
                        <h3 style="color: #333;">📘 Understanding Candlestick Charts</h3>
                        <img src="data:image/png;base64,{encoded_image}" alt="Candlestick Chart Explanation" style="width:50%; border-radius:10px; margin-bottom:10px;">
                        <p style="color: #555;">Candlestick charts show <b>four key data points</b>:</p>
                        <ul style="color: #555; font-size: 16px;">
                            <li>📈 <b>High:</b> The highest price reached during the session.</li>
                            <li>📉 <b>Low:</b> The lowest price during the session.</li>
                            <li>🟢 <b>Open:</b> The price at the start of the session.</li>
                            <li>🔴 <b>Close:</b> The price at the end of the session.</li>
                        </ul>
                        <p style="color: #555;">A <b>green candlestick</b> signals bullish movement (closing higher), while a <b>red candlestick</b> signals bearish movement (closing lower).</p>
                    </div>
                    """, unsafe_allow_html=True)
        
                    # Display Conclusion
                    st.markdown(f"""
                    <div style="background-color: #f4f4f9; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); margin-bottom: 20px; line-height: 1.6;">
                        <h3 style="color: #333;">📌 Conclusion</h3>
                        <p style="color: #555;">The candlestick chart of <b>{ticker}</b> during <b>{time_range}</b> highlights key performance indicators:</p>
                        <ul style="color: #555; font-size: 16px;">
                            <li>🚀 <b>Highest Price:</b> Indicates potential moments of peak interest.</li>
                            <li>📉 <b>Lowest Price:</b> Reflects opportunities for value-focused investors.</li>
                            <li>💡 <b>Price Difference:</b> Helps gauge volatility, critical for risk assessment.</li>
                        </ul>
                        <p style="color: #555;">This dynamic tool helps investors spot trends, evaluate risks, and make data-driven decisions.</p>
                    </div>
                    """, unsafe_allow_html=True)
        
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
                    
        
  
    
        
    elif tab_selection == "Trend Analysis At A Glance":
        
        st.markdown(
    """
    <div style="
        display: flex;
        justify-content: center;
        margin: 20px auto;  /* Center the card within its parent */
        align-items: center;
        width: 100%;
        padding: 20px;
        position:sticky;
    ">
        <div style="
            background: linear-gradient(to right, #6a11cb, #2575fc); 
            color: white; 
            padding: 40px; 
            border-radius: 12px; 
            text-align: center; 
            font-size: 24px; 
            font-weight: bold; 
            box-shadow: 0px 6px 8px rgba(0, 0, 0, 0.15);
            margin: 0 auto,
            max-width: 80%;
            width: 80%;
        ">
            📊 <span style="font-size: 28px;">How has the closing price of the selected stock evolved over the past year?</span> <br> 
            Discover Key Trends and Insights! 🚀
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

        
        


        st.components.v1.iframe(src="http://localhost:8062", width=1500, height=3000)
    # elif tab_selection == "Bubble Chart":
        
    #     st.header("Interactive Bubble Chart: Dash App Embedded")
    #     st.components.v1.iframe(src="http://localhost:8055", width=1400, height=800)
    elif tab_selection == "PE Ratio vs Volatility Comparison":
        
        # Parallel Coordinates Chart Header
        # Key Metrics Definitions Section
        st.markdown(
        """
        <div style="
        display: flex;
        justify-content: flex-start; 
        align-items: center;
        width: 100%;
        margin-left: 55%; 
        padding: 20px;
        ">
            <div style="
                background: linear-gradient(to right, #6a11cb, #2575fc); 
                color: white; 
                padding: 60px; 
                border-radius: 12px; 
                text-align: center; 
                font-size: 26px; 
                font-weight: bold; 
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 100%; 
                width: 80%; /* Ensure consistent alignment */
            ">
                📊 <span style="font-size: 28px;">How do selected stocks compare across key financial metrics such as P/E Ratio, Volatility, Market Cap, and YTD Performance?</span> <br> 
                Analyze and discover meaningful patterns across multiple dimensions! 🚀
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
      

        
        # Embed Parallel Coordinates Dash App
        st.components.v1.iframe(src="http://localhost:8056", width=2500, height=2200)
        
        # Add a horizontal separator
        st.markdown("---")  # Separator for clarity
        
        # Bubble Chart Animation Header
        st.markdown(
            """
            <div style="
            display: flex;
            justify-content: flex-start;
            align-items: center;
            width: 100%;
            margin-left: 55%; 
            padding: 20px;
            ">
                <div style="
                    background: linear-gradient(to right, #ff7e5f, #feb47b); 
                    color: white; 
                    padding: 60px; 
                    border-radius: 12px; 
                    text-align: center; 
                    font-size: 26px; 
                    font-weight: bold; 
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                    max-width: 100%; 
                    width: 100%;
                ">
                    📊 <span style="font-size: 28px;">How do stocks evolve over time in terms of valuation (P/E Ratio) and risk (Volatility)?</span> <br> 
                    Visualize dynamic trends and balance between risk and reward! 🚀
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Embed Bubble Chart Animation Dash App
        st.components.v1.iframe(src="http://localhost:8059", width=2500, height=1900)

        
       

        
    elif tab_selection == "Risk Return":
        st.markdown(
        """
        <div style="
            display: flex;
            justify-content: left; 
            align-items: center;
            margin-left: 0; /* Remove unnecessary left margin */
            width: 100%;
            padding: 5px;
        ">
            <div style="
                background: linear-gradient(to right, #6a11cb, #2575fc); 
                color: white; 
                padding: 5px; 
                border-radius: 12px; 
                text-align: center; 
                font-size: 18px; 
                font-weight: bold; 
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 90%; 
                line-height: 1.6;
                margin: 20px auto;
            ">
                <h3 style="color: white; font-size: 26px; margin-bottom: 10px;">📊 What is the trade-off between risk (volatility) and return for selected stocks?</h3>
                <p style="color: #f0f0f0; font-size: 18px; margin-bottom: 10px;">
                    The Risk-Return Bubble Matrix visualizes the relationship between annual returns and volatility (risk)
                    for selected stocks. It helps investors identify opportunities based on their risk tolerance and financial goals.
                </p>
                <p style="color: #f0f0f0; font-size: 18px;">
                    This tool highlights stocks with the highest returns, the lowest risk, or the best risk-return balance 
                    to support better investment decisions. Explore and align your portfolio with your investment strategy!
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
        )
    
        # Embed Risk-Return Bubble Matrix Dash App
        st.components.v1.iframe(src="http://localhost:8057", width=2500, height=1500)
    

        
    elif tab_selection == "Stock Percentage Change Metrics":

    
        # Embed the iframe for the Dash application
        st.components.v1.iframe(src="http://localhost:8061", width=2500, height=2500)

        
   


    
           

          
if __name__ == "__main__":
    main()
