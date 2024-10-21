from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

class PDFWriter:
    def __init__(self, filename):
        self.filename = filename
        self.page_height = letter[1]
        self.page_width = letter[0]
        self.margin = 30

    def truncate_data(self, data, max_dates=5):
        """Limit data to the most recent dates for table display only."""
        truncated_data = {}
        for currency, values in data.items():
            sorted_values = sorted(values, key=lambda x: x[0], reverse=True)[:max_dates]
            truncated_data[currency] = sorted(sorted_values, key=lambda x: x[0])
        return truncated_data

    def create_pdf(self, fetched_data, volatility_data, rate_of_change_data, moving_average_data):
        # Store full data for graphs
        self.full_data = fetched_data
        # Truncate data for tables
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
        elements.append(Spacer(1, 10))

        # Create pages for each currency
        for i, currency in enumerate(truncated_data.keys()):
            if i > 0:  # Only add page break before currencies after the first one
                elements.append(PageBreak())
            
            elements.extend(self.create_currency_page(
                currency,
                truncated_data[currency],
                volatility_data.get(currency),
                rate_of_change_data.get(currency),
                moving_average_data.get(currency, [])
            ))

        doc.build(elements)
        print(f"PDF generated successfully: {self.filename}")

    def create_currency_page(self, currency, exchange_data, volatility, rate_of_change, moving_averages):
        """Create a single column page for a currency with all components stacked vertically."""
        elements = []

        # Currency header
        currency_header = self.get_header_style(f"{currency.upper()} Currency Analysis")
        elements.append(currency_header)
        elements.append(Spacer(1, 10))

        # Exchange rates table with full width
        elements.append(self.create_subheader("Recent Exchange Rates"))
        table_data = self.prepare_table_data(currency, exchange_data)
        exchange_table = Table(table_data, colWidths=[self.page_width/3 - 20, self.page_width/3 - 20])
        exchange_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(exchange_table)
        elements.append(Spacer(1, 15))

        # Exchange rate graph (using full data)
        elements.append(self.create_subheader("Complete Exchange Rate Trend"))
        full_exchange_data = sorted(self.full_data[currency], key=lambda x: x[0])
        exchange_graph_path = self.save_exchange_graph_to_temp(currency, full_exchange_data, 
                                                             width=6.5*inch, height=2*inch)
        elements.append(Image(exchange_graph_path, width=6.5*inch, height=2*inch))
        elements.append(Spacer(1, 15))

        # Moving average graph (using full data)
        elements.append(self.create_subheader("Complete Moving Averages Trend"))
        moving_average_graph_path = self.save_moving_average_graph_to_temp(
            currency, 
            moving_averages, 
            width=6.5*inch, height=2*inch
        )
        elements.append(Image(moving_average_graph_path, width=6.5*inch, height=2*inch))
        elements.append(Spacer(1, 15))

        # Metrics section
        elements.append(self.create_subheader("Currency Metrics"))
        elements.append(Paragraph(f"Volatility: {volatility if volatility is not None else 'N/A'}", 
                                self.get_metric_style()))
        elements.append(Paragraph(f"Rate of Change: {rate_of_change if rate_of_change is not None else 'N/A'}", 
                                self.get_metric_style()))
        
        if moving_averages:
            ma_text = f"Moving Averages: {', '.join(f'{val:.4f}' for val in moving_averages[:3])}..."
        else:
            ma_text = "Moving Averages: N/A"
        elements.append(Paragraph(ma_text, self.get_metric_style()))

        return elements

    def save_exchange_graph_to_temp(self, currency, values, width=6.5*inch, height=2*inch):
        """Create an exchange rate graph without date labels."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()

        plt.figure(figsize=(width/inch, height/inch))
        
        # Extract only rates and use sequential points
        rates = [item[1] for item in values]
        points = range(len(rates))
        
        plt.plot(points, rates, marker='o', color='#1f77b4', linewidth=1.5, markersize=3)

        plt.title(f'{currency.upper()} Exchange Rate vs EUR', fontsize=10)
        plt.ylabel('Rate', fontsize=8)
        # Remove x-axis labels since we're showing sequential points
        plt.xticks([])
        plt.yticks(fontsize=8)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return temp_filename

    def save_moving_average_graph_to_temp(self, currency, moving_averages, width=6.5*inch, height=2*inch):
        """Create a moving averages graph without date labels."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()

        plt.figure(figsize=(width/inch, height/inch))
        
        if isinstance(moving_averages, list) and moving_averages:
            # Use sequential points for x-axis
            points = range(len(moving_averages))
            
            # If moving_averages is a list of tuples, extract only the values
            if isinstance(moving_averages[0], tuple):
                ma_values = [item[1] for item in moving_averages]
            else:
                ma_values = moving_averages
                
            plt.plot(points, ma_values, marker='o', color='#ff7f0e', linewidth=1.5, markersize=3)

        plt.title(f'{currency.upper()} Moving Averages', fontsize=10)
        plt.ylabel('Value', fontsize=8)
        # Remove x-axis labels since we're showing sequential points
        plt.xticks([])
        plt.yticks(fontsize=8)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return temp_filename

    def get_header_style(self, text):
        """Create a header with the given text."""
        header_style = ParagraphStyle(
            'CustomHeader',
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            alignment=1
        )
        return Paragraph(text, header_style)

    def create_subheader(self, text):
        """Create a subheader with the given text."""
        subheader_style = ParagraphStyle(
            'SubHeader',
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=5,
            spaceAfter=5,
            textColor=colors.HexColor('#2F4F4F')
        )
        return Paragraph(text, subheader_style)

    def get_metric_style(self):
        """Get style for metrics."""
        return ParagraphStyle(
            'MetricStyle',
            fontSize=10,
            fontName='Helvetica',
            spaceBefore=3,
            spaceAfter=3,
            leftIndent=10
        )

    def prepare_table_data(self, currency, values):
        """Prepare data for the table including headers."""
        table_data = [["Date", "Rate"]]
        for date, rate in values:
            table_data.append([date, f"{rate:.4f}"])
        return table_data