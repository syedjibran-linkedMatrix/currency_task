import argparse
from currencies import Currencies  # Import the Currencies enum

class ArgParser:
    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser(description="Fetch historical currency data.")
        parser.add_argument(
            "days", type=int, 
            help="Number of days of historical data to fetch."
        )

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
        # Return days and num_currencies 
        return args.days, args.num_currencies  
