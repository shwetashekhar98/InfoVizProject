together_ai_api = "21003311b33c7dddadb89d6c0c7b42e81d8e39c866f672692b15a404e32351e6"

import os
from together import Together

client = Together(api_key=together_ai_api)

# stockStatsPrompt = f'''You are provided with a variable named `data_json` which contains an array of JSON objects representing stock data. Each object corresponds to a stock's performance over different time periods (e.g., 1 Year, 6 Months) and contains the following key attributes: `Symbol`, `Sector`, `Open`, `Close`, `High`, `Low`, `Volume`, `Price to Earnings Ratio`, `Market Cap`, `Dividend Yield %`, `52 Week Change %`, `Debt to Equity`, `Revenue Growth`, and `Profit Margin`.

# Your task is to process `data_json` and produce a JSON object that includes the following information:
# *************************************
# data_json: {data_json}
# *************************************
# 1. **Percentage Change**: For each stock (`Symbol`), calculate the percentage change in the `Close` price over the given time period.
# 2. **Top Performer**: Identify the stock with the highest `52 Week Change %`.
# 3. **Most Stable Stock**: Determine the stock with the least volatility, calculated based on the difference between `High` and `Low` values.
# 4. **Best Overall Stock**: Evaluate and determine the best stock by considering a combination of `52 Week Change %`, `Revenue Growth`, `Profit Margin`, and `Debt to Equity` (favoring lower debt-to-equity ratios).

# Return your results strictly in valid JSON format with the following structure:
# {{ "percentage_change": {{ "<Symbol>": <calculated_percentage>, ... }}, "top_performer": "<Symbol>", "most_stable": "<Symbol>", "best_overall": "<Symbol>" }}
# Do Not returdn anything other than the JSON object.'''


# user_question = "What is the best stock to invest in?"



def getResponse(data_json, user_question):

    stockQuestionPrompt = f'''ou are provided with a variable named `data_json` which contains an array of JSON objects representing stock data. Each object corresponds to a stock's performance over different time periods (e.g., 1 Year, 6 Months) and contains the following key attributes: `Symbol`, `Sector`, `Open`, `Close`, `High`, `Low`, `Volume`, `Price to Earnings Ratio`, `Market Cap`, `Dividend Yield %`, `52 Week Change %`, `Debt to Equity`, `Revenue Growth`, and `Profit Margin`.

        Your task is to process `data_json` and produce a JSON object that includes the following information:
        *************************************
        data_json: {data_json}
        *************************************
        Based on this dataset, answer the following question of the user: {user_question}
        Always give a concise answer.'''

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "system", "content": "You are an expert in the analysis of Stocks."},
            {"role": "user", "content": stockQuestionPrompt},
            ],
        max_tokens=1000,
    )
    # print(response)
    return response.choices[0].message.content
# print(response.choices[0].message.content)