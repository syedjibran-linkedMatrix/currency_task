from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
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

    def create_pdf(self, fetched_data, volatility_data, rate_of_change_data):
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
    
        story = []
    
        # Add header
        header_style = self.get_header_style()
        story.append(header_style)
    
        # Add exchange rate table with pagination support
        table_data = self.prepare_table_data(truncated_data)  # Use truncated data
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
        story.append(table)

        # Create and add the graph
        graph_path = self.save_graph_to_temp(truncated_data)  # Use truncated data
        img = Image(graph_path, width=7*inch, height=3.5*inch)
        story.append(img)
    
        # Add volatility and rate of change sections
        story.extend(self.create_data_sections(volatility_data, rate_of_change_data))
    
        # Build the PDF
        doc.build(story)
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

    def save_graph_to_temp(self, data):
        """Create the exchange rate graph and save it to a temporary file."""
        
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Create and save the plot
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
        
        # Save to temporary file
        plt.savefig(temp_filename, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return temp_filename

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
    
        # Add a space between sections if needed
        sections.append(Paragraph("", section_style))  # Optional empty paragraph for spacing
    
        # Rate of change section header
        rate_change_header = Paragraph("<b>Rate of Change Data (%):</b>", section_style)
        sections.append(rate_change_header)
    
        for currency, values in rate_of_change_data.items():
            text = f"{currency.upper()}: {values if values is not None else 'Insufficient data'}"
            sections.append(Paragraph(text, section_style))
    
        return sections