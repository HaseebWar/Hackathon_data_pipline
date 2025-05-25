import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3
import io
import os

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("S3_BUCKET", "data-hackathon-smit-yourname")
FOLDER_NAME = "coinmarketcap"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape_coinmarketcap_top10():
    url = "https://coinmarketcap.com/"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    crypto_rows = soup.select("tbody tr")[:10]

    if not crypto_rows:
        raise Exception("❌ Failed to locate cryptocurrency rows. Website may have changed.")

    crypto_data = []
    for i, row in enumerate(crypto_rows, 1):
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        name_elem = cells[2].find("p")
        name = name_elem.get_text(strip=True) if name_elem else f"Crypto {i}"
        symbol_elem = cells[2].find_all("p")
        symbol = symbol_elem[1].get_text(strip=True) if len(symbol_elem) > 1 else "N/A"
        price = cells[3].get_text(strip=True)
        change_24h = cells[4].get_text(strip=True)
        market_cap = cells[7].get_text(strip=True)
        volume_24h = cells[8].get_text(strip=True)

        crypto_data.append({
            "Rank": i,
            "Name": name,
            "Symbol": symbol,
            "Price": price,
            "24h Change": change_24h,
            "Market Cap": market_cap,
            "24h Volume": volume_24h
        })

    return crypto_data

def lambda_handler(event, context):
    try:
        crypto_data = scrape_coinmarketcap_top10()

        df = pd.DataFrame(crypto_data)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        filename = f"{FOLDER_NAME}/top10_crypto.csv"
        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=buffer.getvalue())

        return {
            "statusCode": 200,
            "body": f"✅ Top 10 cryptocurrencies uploaded to {filename}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"❌ Error: {str(e)}"
        }
