import requests
import pandas as pd

APP_ID = "**************"

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

print(f"\nExchange Rates relative to {base_currency} (Timestamp: {timestamp}):\n")
print(df.head(10))

df.to_csv("exchange_rates.csv", index=False)
