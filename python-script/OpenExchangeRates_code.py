import requests
import pandas as pd
import boto3
import io
import os

s3 = boto3.client('s3')

APP_ID = os.environ.get("OPENEXCHANGERATES_APP_ID")  # Add this in Lambda Environment Variables
BUCKET_NAME = os.environ.get("S3_BUCKET", "data-hackathon-smit-muhammad-haseeb")
FOLDER_NAME = "openexchangerates"

def fetch_exchange_rates():
    url = "https://openexchangerates.org/api/latest.json"
    params = {
        "app_id": APP_ID,
        "base": "USD"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    base_currency = data["base"]
    timestamp = data["timestamp"]
    rates = data["rates"]

    df = pd.DataFrame(list(rates.items()), columns=["Currency", "Rate"])
    df = df.sort_values("Currency").reset_index(drop=True)

    return df, base_currency, timestamp

def lambda_handler(event, context):
    try:
        df, base_currency, timestamp = fetch_exchange_rates()

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        filename = f"{FOLDER_NAME}/exchange_rates_{timestamp}.csv"
        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=buffer.getvalue())

        return {
            'statusCode': 200,
            'body': f"Exchange rates for {base_currency} uploaded to {filename}"
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"❌ Error: {str(e)}"
        }
