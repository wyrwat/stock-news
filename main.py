import requests
from datetime import date
from datetime import timedelta
from twilio.rest import Client
import os

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

ALPHA_API_KEY = os.environ.get("ALPHA_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_API_KEY = os.environ.get("TWILIO_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

today = date.today()
weekday = today.weekday()
if weekday == 0:
    yesterday = str(today - timedelta(days=3))
    day_before_yesterday = str(today - timedelta(days=4))
elif weekday == 1:
    yesterday = str(today - timedelta(days=1))
    day_before_yesterday = str(today - timedelta(days=4))
else:
    yesterday = str(today - timedelta(days=1))
    day_before_yesterday = str(today - timedelta(days=2))


stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": ALPHA_API_KEY
}
response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()

yesterday_stock_price = float(data["Time Series (Daily)"][yesterday]['4. close'])
day_before_yesterday_stock_price = data["Time Series (Daily)"][day_before_yesterday]['4. close']
stock_price_difference = float(yesterday_stock_price) - float(day_before_yesterday_stock_price)

up_down = None
percentage_difference = (stock_price_difference/yesterday_stock_price) * 100
if percentage_difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

if percentage_difference > 5:

    news_params = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME
    }

    response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    response.raise_for_status()
    news_data = response.json()

    articles = news_data["articles"][:3]
    formatted_news = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in articles]

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages
    for article in formatted_news:
        message.create(
            body= f"TSLA: {up_down} {abs(percentage_difference)} \n {article}" ,
            from_='+12673949286',
            to='+48576701013'
        )
