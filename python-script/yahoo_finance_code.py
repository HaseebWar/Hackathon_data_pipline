import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_sp500_symbols(limit=10):
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    symbols = []

    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text.strip()
        symbol = symbol.replace('.', '-')  # Yahoo Finance format
        symbols.append(symbol)
        if len(symbols) == limit:
            break

    return symbols

def fetch_minute_data(ticker, interval='1m', period='7d', save_dir='data'):
    try:
        data = yf.download(ticker, interval=interval, period=period, progress=False)
        if not data.empty:
            # Select only OHLCV columns
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, f"{ticker}.csv")
            data.to_csv(file_path)
            return f"Save the data for {ticker}"
        else:
            return f"⚠️ No data for {ticker}"
    except Exception as e:
        return f"❌ Error fetching {ticker}: {e}"

def main():
    symbols = get_sp500_symbols(limit=10)
    print(f"📈 Fetching data for {len(symbols)} S&P 500 symbols...\n")

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_minute_data, symbol): symbol for symbol in symbols}
        for future in as_completed(future_to_ticker):
            result = future.result()
            print(result)
    
    print("All downloads complete.")

if __name__ == "__main__":
    main()