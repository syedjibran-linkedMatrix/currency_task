import requests
import random
from datetime import datetime, timedelta
from functools import lru_cache
from utilis import retry_on_failure 
from currencies import Currencies


BASE_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/eur.json"

class CurrencyDataFetcher:
    def __init__(self, days, num_currencies):
        self.days = days
        self.currencies = self.select_random_currencies(num_currencies)  

    def select_random_currencies(self, num_currencies):
        """Select a specified number of random currencies from the Currencies enum."""
        return random.sample(list(Currencies), num_currencies)

    def fetch_data(self):
        today = datetime.today()
        all_data = {currency.value: [] for currency in self.currencies}  

        for i in range(self.days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')  
            url = BASE_URL.format(date=date)
            print(f"\nFetching data for date: {date}")
            data = self.get_currency_data(url)

            if data:  # Only store data if successfully fetched
                eur_data = data.get("eur", {})
                for currency in self.currencies:
                    value = eur_data.get(currency.value, None) 
                    # Append a tuple of (date, value) to the list for that currency
                    if value is not None:  # Only append if value is available
                        all_data[currency.value].append((date, value))

        return all_data  # Return data for selected currencies

    @lru_cache(maxsize=128)
    @retry_on_failure(max_retries=3)  # Decorate with retry mechanism
    def get_currency_data(self, url):
        """Fetch currency data from the API with caching to avoid redundant requests."""
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def print_selected_currencies(self, data):
        """Print the fetched data for the selected currencies."""
        print("\nCurrencies (EUR base):")
        for currency, values in data.items():
            print(f"  {currency.upper()}: {values}")
