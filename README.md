# Advanced Information Visualization for Stock Market Analysis
Overview
This project collaboratively developed by Shweta Shekhar and Khwaab Thareja, aims to create a sophisticated information visualization tool for analyzing stock market data, focusing on the top 10 or top 20 stocks listed on the New York Stock Exchange (NYSE). It simplifies stock market analysis for the general public by providing clear and actionable insights, even for those without extensive financial knowledge.

# Drive Link for recordings , code and final project report
https://drive.google.com/drive/u/0/folders/1EewQwyZ2ykH8mg-uJzKBeBs2vHmGQ-C9

## The Proposed solution and ppt also added for reference
Refer to kt3180_ss19623_info_viz_submission.pptx
Refer to ss19623_kt3180_PriorSurvey.pdf

# Stock Market Analysis Dashboard Link 
https://mastersinfovizproject.streamlit.app/

## Description
An interactive dashboard for analyzing stock performance using **Streamlit** and **Dash**. Includes:
- Stock data visualization
- Risk-return analysis
- Bar chart races and more

## Features
- Centralized data caching for optimized performance
- Modularized Dash apps for specific analyses
- Configurable and reusable components

## Requirements
- Python 3.7+
- Install dependencies: mentioned in requirements.txt

## How to Run
1. Start the Streamlit app:
   ```bash
   streamlit run infoviz.py

## Objectives
Simplify stock market analysis for the general public.
Provide sentiment and analyst decision recommendations based on data-driven insights.
Explore and visualize various aspects of stock performance and market trends.
## Parameters for Analysis
The tool analyzes multiple stock parameters, including:

Market Open, Close, High, and Low prices
Stock Volume
Price-to-Earnings (P/E) Ratio
Market Cap
Dividend Yield
52-Week Change %
Debt-to-Equity Ratio
Revenue Growth
Profit Margin
Industry Trends

### Key Questions Addressed

Sentiment: Is the stock performing well (Good), moderately (Moderate), or poorly (Bad)?
Analyst Decision: Should the stock be bought or held?
Additional Areas of Analysis:

## Risk Assessment:
Volatility of NYSE stocks over time.
Correlation of stock price movements among major NYSE companies.

## Data Exploration:
Top 10 NYSE stocks by market cap.
Changes in stock prices over the past year.
Growth trends in NYSE sectors.

## Financial Performance:
Distribution of P/E ratios and dividend yields.
Companies with consistently increasing earnings over 4 years.

## Trend Analysis:
Stock performance during major market events.
Seasonal patterns in stock prices.
Correlation of stock prices with economic indicators.

## Comparative Analysis:
Value vs. growth stocks.
Performance of international vs. domestic NYSE-listed companies.
Techniques and Tools
Data Collection: Using the yfinance API for real-time and historical stock data.
Data Processing: Python for data cleaning and preprocessing.

## Visualization:
Static Visualizations: Matplotlib for bar charts, line graphs, scatter plots, and histograms.
Dynamic Visualizations: Bokeh for interactive, real-time exploration.
Advanced Visualizations: D3.js for complex, animated insights.

## Challenges
Data Quality and Availability: Ensuring accuracy and completeness of yfinance data.
Complexity of Visualizations: Implementing advanced, interactive designs with D3.js.
User Accessibility: Creating visualizations that are easy for non-experts to interpret.
Performance: Rendering large datasets in real-time efficiently.
Integration of Tools: Seamlessly coordinating Matplotlib, Bokeh, and D3.js.

## Conclusion
This project will deliver a comprehensive visualization tool that simplifies stock market analysis and provides clear investment recommendations. Combining advanced visualization techniques with actionable data insights, it empowers users to make informed decisions.

## Future Scope
Predictive analysis with machine learning models for stock forecasting.
Expansion to global stock markets for comprehensive insights.
User customization for tailored visualizations and investment parameters.
Integration of real-time financial news and sentiment analysis.
