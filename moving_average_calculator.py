# moving_average_calculator.py

class MovingAverageCalculator:
    def __init__(self, data, window_size=5):
        """
        Initialize the calculator with fetched data and a window size.
        :param data: Fetched currency data in the form {currency: [(date, rate), ...]}
        :param window_size: Size of the moving average window.
        """
        self.data = data
        self.window_size = window_size

    def calculate_moving_averages(self):
        """
        Calculate the moving averages for each currency.
        :return: A dictionary with moving averages for each currency.
        """
        moving_averages = {}

        for currency, values in self.data.items():
            rates = [rate for _, rate in values]
            if len(rates) < self.window_size:
                moving_averages[currency] = None  # Insufficient data
                continue

            # Calculate moving averages
            ma_list = [
                sum(rates[i:i + self.window_size]) / self.window_size
                for i in range(len(rates) - self.window_size + 1)
            ]
            moving_averages[currency] = ma_list

        return moving_averages

    def display_moving_averages(self, moving_averages):
        """Print the moving averages."""
        print("\nMoving Averages:".format(self.window_size))
        for currency, ma_list in moving_averages.items():
            if ma_list:
                print(f"{currency.upper()}: {ma_list}")
            else:
                print(f"{currency.upper()}: Insufficient data")
