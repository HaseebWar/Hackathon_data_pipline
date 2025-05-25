import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_coinmarketcap_top10():
    """
    Scrape top 10 cryptocurrencies from CoinMarketCap
    """
    
    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    url = "https://coinmarketcap.com/"
    
    try:
        print("Fetching data from CoinMarketCap...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the cryptocurrency table
        crypto_data = []
        
        # Look for the main table containing cryptocurrency data
        table = soup.find('table') or soup.find('div', class_='cmc-table')
        
        if not table:
            # Alternative approach: look for cryptocurrency rows
            crypto_rows = soup.find_all('tr', limit=11)  # Get top 10 + header
            if not crypto_rows:
                print("Could not find cryptocurrency table. Trying alternative selectors...")
                # Try different selectors
                crypto_rows = soup.select('tbody tr')[:10]
        else:
            crypto_rows = table.find_all('tr')[1:11]  # Skip header, get top 10
        
        if not crypto_rows:
            print("No cryptocurrency data found. The website structure may have changed.")
            return None
        
        print(f"Found {len(crypto_rows)} cryptocurrency entries")
        
        for i, row in enumerate(crypto_rows[:10], 1):
            try:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 7:  # Ensure we have enough data
                    continue
                
                # Extract data with fallback methods
                rank = str(i)
                
                # Name and symbol
                name_cell = cells[1] if len(cells) > 1 else cells[0]
                name = ""
                symbol = ""
                
                # Try to find name and symbol
                name_elem = name_cell.find('p', class_='coin-item-name') or \
                           name_cell.find('a') or \
                           name_cell.find('span')
                
                if name_elem:
                    name = name_elem.get_text(strip=True)
                
                # Look for symbol
                symbol_elem = name_cell.find('p', class_='coin-item-symbol') or \
                             name_cell.find_all('span')
                
                if symbol_elem:
                    if isinstance(symbol_elem, list) and len(symbol_elem) > 1:
                        symbol = symbol_elem[1].get_text(strip=True)
                    else:
                        symbol = symbol_elem.get_text(strip=True) if hasattr(symbol_elem, 'get_text') else str(symbol_elem)
                
                # Price
                price_cell = cells[2] if len(cells) > 2 else None
                price = price_cell.get_text(strip=True) if price_cell else "N/A"
                
                # 24h Change
                change_cell = cells[4] if len(cells) > 4 else None
                change_24h = change_cell.get_text(strip=True) if change_cell else "N/A"
                
                # Market Cap
                market_cap_cell = cells[6] if len(cells) > 6 else None
                market_cap = market_cap_cell.get_text(strip=True) if market_cap_cell else "N/A"
                
                # Volume
                volume_cell = cells[7] if len(cells) > 7 else None
                volume_24h = volume_cell.get_text(strip=True) if volume_cell else "N/A"
                
                crypto_info = {
                    'Rank': rank,
                    'Name': name or f"Crypto {i}",
                    'Symbol': symbol or "N/A",
                    'Price': price,
                    '24h Change': change_24h,
                    'Market Cap': market_cap,
                    '24h Volume': volume_24h
                }
                
                crypto_data.append(crypto_info)
                print(f"Extracted: {crypto_info['Name']} ({crypto_info['Symbol']})")
                
            except Exception as e:
                print(f"Error extracting data for row {i}: {e}")
                continue
        
        return crypto_data
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None

def save_to_csv(data, filename='top10_crypto.csv'):
    """Save data to CSV file"""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")



def main():
    """Main function to run the scraper"""
    print("CoinMarketCap Top 10 Cryptocurrency Scraper")
    print("=" * 50)
    
    # Scrape data
    crypto_data = scrape_coinmarketcap_top10()
    
    if crypto_data:
        # Save data to CSV only
        save_to_csv(crypto_data)
        print(f"Successfully scraped {len(crypto_data)} cryptocurrencies and saved to CSV!")
    else:
        print("Failed to scrape data. Please check your internet connection and try again.")
        print("\nNote: CoinMarketCap may have anti-scraping measures in place.")
        print("Consider using their official API for production use:")
        print("https://coinmarketcap.com/api/")

if __name__ == "__main__":
    main()