from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


class PDFWriter:
    def __init__(self, filename):
        self.filename = filename
        self.page_height = letter[1]
        self.page_width = letter[0]
        self.margin = 50

    def truncate_data(self, data, max_dates=5):
        """Limit data to the most recent dates."""
        truncated_data = {}
        for currency, values in data.items():
            sorted_values = sorted(values, key=lambda x: x[0], reverse=True)[:max_dates]
            truncated_data[currency] = sorted(sorted_values, key=lambda x: x[0])
        return truncated_data

    def create_pdf(self, fetched_data, volatility_data, rate_of_change_data, moving_average_data):
        # Truncate data to 5 most recent dates
        truncated_data = self.truncate_data(fetched_data, max_dates=5)

        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )

        elements = []

        # Add main header
        main_header = self.get_header_style("Currency Data Report")
        elements.append(main_header)
        elements.append(PageBreak())

        # Create a page for each currency
        for currency in truncated_data.keys():
            elements.extend(self.create_currency_page(
                currency,
                truncated_data[currency],
                volatility_data.get(currency),
                rate_of_change_data.get(currency),
                moving_average_data.get(currency, [])
            ))
            elements.append(PageBreak())

        # Build the PDF
        doc.build(elements)
        print(f"PDF generated successfully: {self.filename}")

    def create_currency_page(self, currency, exchange_data, volatility, rate_of_change, moving_averages):
        """Create a complete page for a single currency."""
        elements = []

        # Currency header
        currency_header = self.get_header_style(f"{currency.upper()} Currency Analysis")
        elements.append(currency_header)

        # Add subheader for exchange rates
        elements.append(self.create_subheader("Recent Exchange Rates"))

        # Exchange rates table
        table_data = self.prepare_table_data(currency, exchange_data)
        table = Table(table_data, colWidths=[150, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Add some spacing
        elements.append(Paragraph("<br/><br/>", ParagraphStyle('Spacing')))

        # Exchange rate graph
        elements.append(self.create_subheader("Exchange Rate Trend"))
        exchange_graph_path = self.save_exchange_graph_to_temp(currency, exchange_data)
        img_exchange = Image(exchange_graph_path, width=6 * inch, height=3 * inch)
        elements.append(img_exchange)

        # Add metrics section
        elements.append(self.create_subheader("Currency Metrics"))
        
        # Volatility
        volatility_text = f"Volatility: {volatility if volatility is not None else 'Insufficient data'}"
        elements.append(Paragraph(volatility_text, self.get_metric_style()))

        # Rate of Change
        roc_text = f"Rate of Change: {rate_of_change if rate_of_change is not None else 'Insufficient data'}"
        elements.append(Paragraph(roc_text, self.get_metric_style()))

        # Moving Averages
        if moving_averages:
            ma_text = f"Moving Averages: {', '.join(f'{val:.4f}' for val in moving_averages)}"
        else:
            ma_text = "Moving Averages: Insufficient data"
        elements.append(Paragraph(ma_text, self.get_metric_style()))

        return elements

    def get_header_style(self, text):
        """Create a header with the given text."""
        header_style = ParagraphStyle(
            'CustomHeader',
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            alignment=1  # Center alignment
        )
        return Paragraph(text, header_style)

    def create_subheader(self, text):
        """Create a subheader with the given text."""
        subheader_style = ParagraphStyle(
            'SubHeader',
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#2F4F4F')
        )
        return Paragraph(text, subheader_style)

    def get_metric_style(self):
        """Get the style for metric display."""
        return ParagraphStyle(
            'MetricStyle',
            fontSize=12,
            fontName='Helvetica',
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20
        )

    def prepare_table_data(self, currency, values):
        """Prepare data for the table including headers."""
        table_data = [["Date", "Exchange Rate"]]
        for date, rate in values:
            table_data.append([date, f"{rate:.4f}"])
        return table_data

    def save_exchange_graph_to_temp(self, currency, values):
        """Create the exchange rate graph for a single currency and save it to a temporary file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()
        
        plt.figure(figsize=(8, 4))
        
        dates = [item[0] for item in values]
        rates = [item[1] for item in values]
        plt.plot(dates, rates, marker='o', color='#1f77b4', linewidth=2)

        plt.title(f'{currency.upper()} Exchange Rate vs EUR')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return temp_filename