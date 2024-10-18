from arg_parser import ArgParser
from fetch_data import CurrencyDataFetcher
from volatility_calculator import CurrencyVolatilityCalculator
from write_data import PDFWriter

def main():
    # Get the arguments from the ArgParser (number of days and selected currencies)
    days, selected_currencies = ArgParser.get_args()

    # Fetch currency data
    fetch_data = CurrencyDataFetcher(days, selected_currencies)
    fetched_data = fetch_data.fetch_data()  # Get raw fetched data
    fetch_data.print_selected_currencies(fetched_data)  # Display raw fetched data

    # Calculate and display volatility
    calculator = CurrencyVolatilityCalculator(fetched_data)
    volatility_data = calculator.calculate_volatility()  # Get raw volatility data
    calculator.display_volatility()  # Display raw volatility data

    # Generate PDF with raw fetched data and volatility data
    pdf_writer = PDFWriter("Currency_Report.pdf")
    pdf_writer.create_pdf(fetched_data, volatility_data)  # Pass raw data directly

if __name__ == "__main__":
    main()
 