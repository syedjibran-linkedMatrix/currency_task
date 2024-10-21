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
            # Sort values by date in descending order and take the most recent 5
            sorted_values = sorted(values, key=lambda x: x[0], reverse=True)[:max_dates]
            # Reverse back to ascending order for display
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

        element_of_pdf = []

        # Add header
        header_style = self.get_header_style()
        element_of_pdf.append(header_style)

        # Add exchange rate table
        table_data = self.prepare_table_data(truncated_data)
        table = Table(table_data, colWidths=[100, 150, 150])
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
        element_of_pdf.append(table)

        # Add the exchange rates graph
        exchange_graph_path = self.save_exchange_graph_to_temp(truncated_data)
        img_exchange = Image(exchange_graph_path, width=7 * inch, height=3.5 * inch)
        element_of_pdf.append(img_exchange)

        # Add the moving averages graph
        ma_graph_path = self.save_ma_graph_to_temp(moving_average_data)
        img_ma = Image(ma_graph_path, width=7 * inch, height=3.5 * inch)
        element_of_pdf.append(img_ma)

        # Add sections for volatility, rate of change, and moving averages
        element_of_pdf.extend(self.create_data_sections(volatility_data, rate_of_change_data))
        element_of_pdf.extend(self.create_moving_average_section(moving_average_data))

        # Build the PDF
        doc.build(element_of_pdf)
        print(f"PDF generated successfully: {self.filename}")

    def get_header_style(self):
        # Create the header text
        header_text = f"Currency Data Report\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
        # Define a ParagraphStyle for the header
        header_style = ParagraphStyle(
            'CustomHeader',
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            alignment=1  # Center alignment
        )
    
        # Create a paragraph using the header text
        header_paragraph = Paragraph(header_text, header_style)
        return header_paragraph

    def prepare_table_data(self, data):
        """Prepare data for the table including headers."""
        table_data = [["Currency", "Date", "Exchange Rate"]]
        for currency, values in data.items():
            for date, rate in values:
                table_data.append([currency.upper(), date, f"{rate:.4f}"])
        return table_data

    def save_exchange_graph_to_temp(self, data):
        """Create the exchange rate graph and save it to a temporary file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()
        
        plt.figure(figsize=(8, 4))
        for currency, values in data.items():
            dates = [item[0] for item in values]
            rates = [item[1] for item in values]
            plt.plot(dates, rates, marker='o', label=currency.upper())

        plt.title('Exchange Rates Over Time - 5 Recent Dates (EUR base)')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return temp_filename

    def save_ma_graph_to_temp(self, moving_average_data):
        """Create the moving averages graph and save it to a temporary file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()
        
        plt.figure(figsize=(8, 4))
        
        # Plot moving averages for each currency
        for currency, ma_values in moving_average_data.items():
            if ma_values:  # Check if there are values to plot
                # Create x-axis points (1 through length of MA values)
                x_points = list(range(1, len(ma_values) + 1))
                plt.plot(x_points, ma_values, marker='o', label=f"{currency.upper()}")

        plt.title('Moving Averages by Currency')
        plt.xlabel('Period')
        plt.ylabel('Moving Average Value')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return temp_filename
    
    def create_moving_average_section(self, moving_average_data):
        """Create a section for moving average data."""
        sections = []
        section_style = ParagraphStyle(
            'SectionStyle',
            fontSize=12,
            fontName='Helvetica',
            spaceAfter=10
        )

        # Add header for moving averages
        header = Paragraph("<b>Moving Averages:</b>", section_style)
        sections.append(header)

        # Add each currency's moving average data
        for currency, ma_values in moving_average_data.items():
            if ma_values:
                ma_text = f"{currency.upper()}: {', '.join(f'{val:.4f}' for val in ma_values)}"
            else:
                ma_text = f"{currency.upper()}: Insufficient data"
            sections.append(Paragraph(ma_text, section_style))

        return sections

    def create_data_sections(self, volatility_data, rate_of_change_data):
        """Create sections for volatility and rate of change data."""
        sections = []
        section_style = ParagraphStyle(
            'SectionStyle',
            fontSize=12,
            fontName='Helvetica',
            spaceAfter=10
        )
        
        # Volatility section header
        volatility_header = Paragraph("<b>Volatility Data:</b>", section_style)
        sections.append(volatility_header)
    
        for currency, values in volatility_data.items():
            text = f"{currency.upper()}: {values if values is not None else 'Insufficient data'}"
            sections.append(Paragraph(text, section_style))
    
        # Add a space between sections
        sections.append(Paragraph("", section_style))
    
        # Rate of change section header
        rate_change_header = Paragraph("<b>Rate of Change Data (%):</b>", section_style)
        sections.append(rate_change_header)
    
        for currency, values in rate_of_change_data.items():
            text = f"{currency.upper()}: {values if values is not None else 'Insufficient data'}"
            sections.append(Paragraph(text, section_style))
    
        return sections