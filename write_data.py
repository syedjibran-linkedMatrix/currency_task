from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import matplotlib.pyplot as plt
import io
from reportlab.lib.utils import ImageReader

class PDFWriter:
    def __init__(self, filename):
        self.filename = filename
        self.page_height = letter[1]
        self.margin = 50

    def create_pdf(self, fetched_data, volatility_data, rate_of_change_data):
        # Create a new PDF with the specified filename
        pdf = canvas.Canvas(self.filename, pagesize=letter)
        pdf.setTitle("Currency Data Report")

        # Start with first page
        y = self.page_height - self.margin
        
        # Write header
        y = self.write_header(pdf, y)

        # Limit to 5 dates if the data contains more
        truncated_data = self.truncate_data(fetched_data, max_dates=5)

        # Write fetched data
        y = self.write_section(pdf, "Fetched Currency Data (5 Recent Dates):", truncated_data, y)

        # Calculate space needed for graph (including title and margins)
        graph_height = 3.5 * inch + 40  # Height plus margins
        
        # Check if there's enough space for the graph
        if y - graph_height < self.margin:
            pdf.showPage()  # Start new page
            y = self.page_height - self.margin
            y = self.write_header(pdf, y)  # Write header on new page

        # Add exchange rate graph
        y = self.add_exchange_rate_graph(pdf, fetched_data, y)

        # Check if we need a new page for volatility data
        if y - 100 < self.margin:  # 100 is estimated minimum space needed for next section
            pdf.showPage()
            y = self.page_height - self.margin
            y = self.write_header(pdf, y)

        # Write volatility data
        y = self.write_section(pdf, "Volatility Data:", volatility_data, y)

        # Check if we need a new page for rate of change data
        if y - 100 < self.margin:
            pdf.showPage()
            y = self.page_height - self.margin
            y = self.write_header(pdf, y)

        # Write rate of change data
        y = self.write_section(pdf, "Rate of Change Data (%):", rate_of_change_data, y)

        # Save the PDF
        pdf.save()
        print(f"PDF generated successfully: {self.filename}")

    def write_header(self, pdf, y):
        """Write the header section and return the new y position."""
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, y, "Currency Data Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(200, y - 20, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return y - 50  # Return new y position after header

    def add_exchange_rate_graph(self, pdf, data, y):
        """Create and add exchange rate graph to the PDF."""
        # Add section title
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Exchange Rate Trends:")
        y -= 20

        # Create a new figure
        plt.figure(figsize=(8, 4))
        
        # Plot each currency
        for currency, values in data.items():
            dates = [item[0] for item in values]
            rates = [item[1] for item in values]
            plt.plot(dates, rates, marker='o', label=currency.upper())

        # Customize the plot
        plt.title('Exchange Rates Over Time (EUR base)')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()

        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        buf.seek(0)

        # Add the plot to the PDF
        img = ImageReader(buf)
        img_width = 7 * inch
        img_height = 3.5 * inch
        x = (letter[0] - img_width) / 2  # Center the image
        pdf.drawImage(img, x, y - img_height, width=img_width, height=img_height)

        return y - img_height - 20

    def truncate_data(self, data, max_dates=5):
        """Limit the data to a maximum of 5 dates per currency."""
        return {currency: values[:max_dates] for currency, values in data.items()}

    def write_section(self, pdf, title, data, y):
        """Write a section with title and data to the PDF."""
        original_y = y
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, title)
        pdf.setFont("Helvetica", 10)
        y -= 20

        for currency, values in data.items():
            line_content = f"{currency.upper()}: {values if values is not None else 'Insufficient data'}"
            y = self.wrap_text(pdf, line_content, y)
            
            # Check if we need a new page
            if y < self.margin:
                pdf.showPage()
                y = self.page_height - self.margin
                y = self.write_header(pdf, y)
                pdf.setFont("Helvetica", 10)

        return y

    def wrap_text(self, pdf, text, y, x=50, line_height=15):
        """Wrap text to fit within the PDF page."""
        words = text.split()
        current_line = []
        current_y = y

        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = pdf.stringWidth(test_line, "Helvetica", 10)

            if text_width > (letter[0] - 100):
                pdf.drawString(x, current_y, ' '.join(current_line))
                current_y -= line_height

                # Check if we need a new page
                if current_y < self.margin:
                    pdf.showPage()
                    current_y = self.page_height - self.margin
                    self.write_header(pdf, current_y)
                    current_y -= 50  # Adjust for header
                    pdf.setFont("Helvetica", 10)

                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            pdf.drawString(x, current_y, ' '.join(current_line))
            current_y -= line_height

        return current_y