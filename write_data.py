from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime

class PDFWriter:
    def __init__(self, filename):
        self.filename = filename

    def create_pdf(self, fetched_data, volatility_data):
        # Create a new PDF with the specified filename
        pdf = canvas.Canvas(self.filename, pagesize=letter)
        pdf.setTitle("Currency Data Report")

        # Write header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, "Currency Data Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(200, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Limit to 5 dates if the data contains more
        truncated_data = self.truncate_data(fetched_data, max_dates=5)

        # Write fetched data
        y = 700
        y = self.write_section(pdf, "Fetched Currency Data (5 Recent Dates):", truncated_data, y)

        # Write volatility data
        y -= 20  # Space between sections
        y = self.write_section(pdf, "Volatility Data:", volatility_data, y)

        # Save the PDF
        pdf.showPage()
        pdf.save()
        print(f"PDF generated successfully: {self.filename}")

    def truncate_data(self, data, max_dates=5):
        """Limit the data to a maximum of 5 dates per currency."""
        return {currency: values[:max_dates] for currency, values in data.items()}

    def write_section(self, pdf, title, data, y, page_bottom=50):
        """Write a section with title and data to the PDF."""
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, title)
        pdf.setFont("Helvetica", 10)  # Adjust font size for more compact text
        y -= 20  # Space before content

        for currency, values in data.items():
            line_content = f"{currency.upper()}: {values}"
            y = self.wrap_text(pdf, line_content, y, page_bottom)

        return y

    def wrap_text(self, pdf, text, y, page_bottom, x=50, line_height=15):
        """Wrap text to fit within the PDF page."""
        # Split the text into manageable pieces
        words = text.split()
        current_line = []
        current_y = y

        for word in words:
            # Join current line with the new word
            test_line = ' '.join(current_line + [word])
            # Measure the width of the text
            text_width = pdf.stringWidth(test_line, "Helvetica", 10)

            # Check if the line width exceeds page width (minus margins)
            if text_width > (letter[0] - 100):  # 100 points for left/right margin
                # Draw the current line and reset for new line
                pdf.drawString(x, current_y, ' '.join(current_line))
                current_y -= line_height  # Move down for next line

                # Check if we need a new page
                if current_y < page_bottom:
                    pdf.showPage()  # Start a new page
                    current_y = 750  # Reset Y-position for new page
                    pdf.setFont("Helvetica", 10)  # Reset font

                # Start a new line with the current word
                current_line = [word]
            else:
                current_line.append(word)

        # Draw any remaining words in the current line
        if current_line:
            pdf.drawString(x, current_y, ' '.join(current_line))
            current_y -= line_height

        return current_y
