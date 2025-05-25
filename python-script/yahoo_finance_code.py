import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import boto3
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('S3_BUCKET', 'data-hackathon-smit-yourname')
FOLDER_NAME = 'yfinance-data'
LIMIT = int(os.environ.get('SYMBOL_LIMIT', '10'))

def get_sp500_symbols(limit=10):
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    symbols = []

    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text.strip().replace('.', '-')
        symbols.append(symbol)
        if len(symbols) == limit:
            break
    return symbols

def fetch_minute_data(ticker, interval='1m', period='7d'):
    try:
        data = yf.download(ticker, interval=interval, period=period, progress=False)
        if not data.empty:
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            buffer = io.StringIO()
            data.to_csv(buffer)
            buffer.seek(0)

            filename = f"{FOLDER_NAME}/{ticker}.csv"
            s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=buffer.getvalue())
            return f"✅ Uploaded: {filename}"
        else:
            return f"⚠️ No data for {ticker}"
    except Exception as e:
        return f"❌ Error fetching {ticker}: {e}"

def lambda_handler(event, context):
    symbols = get_sp500_symbols(limit=LIMIT)
    print(f"📈 Fetching data for {len(symbols)} symbols...")

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_minute_data, sym): sym for sym in symbols}
        for future in as_completed(futures):
            result = future.result()
            print(result)
            results.append(result)

    return {
        'statusCode': 200,
        'body': {
            'message': 'All downloads complete',
            'details': results
        }
    }
