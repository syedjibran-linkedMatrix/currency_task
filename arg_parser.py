import argparse
from currencies import Currencies  # Import the Currencies enum

class ArgParser:
    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser(description="Fetch historical currency data.")

        # Add 'days' argument
        parser.add_argument(
            "days", type=int, 
            help="Number of days of historical data to fetch."
        )

        # Add 'num_currencies' argument
        parser.add_argument(
            "num_currencies", type=int,
            help="Number of currencies to select randomly."
        )

        args = parser.parse_args()

        # Validate arguments
        if args.days <= 0:
            parser.error("The number of days must be positive.")
        if not (1 <= args.num_currencies <= len(Currencies)):
            parser.error(f"Number of currencies must be between 1 and {len(Currencies)}.")

        return args.days, args.num_currencies  # Return days and num_currencies only
