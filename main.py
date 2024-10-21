from arg_parser import ArgParser
from fetch_data import CurrencyDataFetcher
from volatility_calculator import CurrencyVolatilityCalculator
from write_data import PDFWriter
from calculate_rate_of_change import CurrencyRateOfChangeCalculator

def main():
   
    days, selected_currencies = ArgParser.get_args()

    # Fetch currency data
    fetch_data = CurrencyDataFetcher(days, selected_currencies)
    fetched_data = fetch_data.fetch_data()  
    fetch_data.print_selected_currencies(fetched_data)  

    # Calculate and display volatility
    calculator = CurrencyVolatilityCalculator(fetched_data)
    volatility_data = calculator.calculate_volatility()  
    calculator.display_volatility()  

    # Calculate and display rate of change
    rate_calculator = CurrencyRateOfChangeCalculator(fetched_data)
    rate_of_change = rate_calculator.calculate_rate_of_change()
    rate_calculator.display_rate_of_change()

    # Generate PDF with raw fetched data, volatility data, and rate of change data
    pdf_writer = PDFWriter("Currency_Report.pdf")
    pdf_writer.create_pdf(fetched_data, volatility_data, rate_of_change)  

if __name__ == "__main__":
    main()
