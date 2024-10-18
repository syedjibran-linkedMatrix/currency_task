class CurrencyVolatilityCalculator:
    def __init__(self, currency_data):
        """Initialize the calculator with currency data."""
        self.currency_data = currency_data  # Expected format: {'THB': [('2024-10-17', 36.07878107), ('2024-10-16', 36.23039568)]}

    def calculate_mean(self, values):
        """Calculate the mean of a list of values."""
        return sum(values) / len(values) if values else 0

    def calculate_standard_deviation(self, values, mean):
        """Calculate the standard deviation of a list of values."""
        if len(values) < 2:
            return 0  # Not enough data for standard deviation
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)  # Sample standard deviation
        return variance ** 0.5

    def calculate_volatility(self):
        """Calculate the volatility for each currency."""
        volatility = {}
        for currency, data in self.currency_data.items():
            # data = [('2024-10-17', 36.07878107), ('2024-10-16', 36.23039568), ('2024-10-15', 36.15000000)]
            # Extract the values from the data

            values = [value for _, value in data if value]

            # values = [36.07878107, 36.23039568, 36.15000000]

            if len(values) > 1:  # Ensure there are enough values to calculate standard deviation
                mean = self.calculate_mean(values)
                stddev = self.calculate_standard_deviation(values, mean)
                volatility[currency] = stddev
            else:
                volatility[currency] = None  # Not enough data to calculate

        return volatility

    def display_volatility(self):
        """Display the calculated volatility for each currency."""
        volatility = self.calculate_volatility()
        for currency, vol in volatility.items():
            print(f"Volatility for {currency.upper()}: {vol if vol else 'Insufficient data'}")


# def main():
#     # Sample input for testing, can be replaced with actual data from fetch_data.py
#     currency_data = {
#         'THB': [('2024-10-17', 36.07878107), ('2024-10-16', 36.23039568)],
#         'BRL': [('2024-10-17', 6.15909755), ('2024-10-16', 6.1565057)],
#     }

#     calculator = CurrencyVolatilityCalculator(currency_data)
#     calculator.display_volatility()


# if __name__ == "__main__":
#     main()
