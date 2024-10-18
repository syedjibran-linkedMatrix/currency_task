class CurrencyRateOfChangeCalculator:
    def __init__(self, currency_data):
        """Initialize the calculator with currency data."""
        self.currency_data = currency_data  # Expected format: {'THB': [('2024-10-17', 36.07878107), ('2024-10-16', 36.23039568)]}

    def calculate_rate_of_change(self):
        """Calculate the rate of change for each currency."""
        rate_of_change = {}
        
        for currency, data in self.currency_data.items():
            # Extract the values from the data
            values = [value for _, value in data if value is not None]

            if len(values) > 1:  # Need at least two values to calculate the rate of change
                initial_value = values[-1]  # Oldest value
                final_value = values[0]  # Most recent value
                rate = ((final_value - initial_value) / initial_value) * 100  # Percentage change
                rate_of_change[currency] = rate
            else:
                rate_of_change[currency] = None  # Not enough data to calculate

        return rate_of_change

    def display_rate_of_change(self):
        """Display the calculated rate of change for each currency."""
        rate_of_change = self.calculate_rate_of_change()
        for currency, rate in rate_of_change.items():
            if rate is not None:
                print(f"Rate of Change for {currency.upper()}: {rate:.2f}%")
            else:
                print(f"Rate of Change for {currency.upper()}: Insufficient data")
