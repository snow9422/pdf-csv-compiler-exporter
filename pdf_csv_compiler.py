import PyPDF2
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import chardet

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']

def extract_text_from_pdf(pdf_path):
    text_content = []
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text_content.extend(page.extract_text().split('\n'))
    except Exception as e:
        print(f"Warning: Error processing PDF: {str(e)}")
    return text_content

def read_csv_data(csv_path):
    try:
        # Detect the file encoding
        encoding = detect_encoding(csv_path)
        print(f"Detected CSV encoding: {encoding}")
        
        # Read CSV with detected encoding
        data = pd.read_csv(csv_path, encoding=encoding)
        
        # Clean up the data
        data = data.replace('--', pd.NA)  # Replace -- with NA
        data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y', errors='coerce')
        
        # Clean up Amount and Balance columns
        data['Amount'] = pd.to_numeric(data['Amount'].replace('[\$,]', '', regex=True), errors='coerce')
        data['Balance'] = pd.to_numeric(data['Balance'].str.replace('[\$,]', '', regex=True), errors='coerce')
        
        print(f"Successfully read CSV with {len(data)} rows")
        return data
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        raise

def add_svg_logo(pdf, svg_path, x=20, y=20, width=50):
    try:
        # Convert SVG to PNG using svglib
        drawing = svg2rlg(svg_path)
        png_path = "temp_logo.png"
        renderPM.drawToFile(drawing, png_path, fmt="PNG")
        
        # Calculate height maintaining aspect ratio
        aspect = drawing.height / drawing.width
        height = width * aspect
        
        # Add PNG to PDF
        pdf.image(png_path, x=x, y=y, w=width)
        
        # Remove temporary PNG file
        os.remove(png_path)
        
        # Return the height of the logo for spacing
        return height + y + 10
        
    except Exception as e:
        print(f"Warning: Could not add logo: {str(e)}")
        return y

def create_pdf_with_data(output_pdf_path, text_content, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Set margins
    pdf.set_margins(20, 20, 20)
    
    # Add logo at the top
    logo_path = "found_logo.svg"
    current_y = add_svg_logo(pdf, logo_path)
    
    # Add original text content with adjusted y position
    if text_content:
        pdf.set_y(current_y)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Original PDF Content:", ln=True)
        pdf.set_font("Arial", size=10)
        for line in text_content:
            if line.strip():
                pdf.cell(0, 10, txt=line.strip(), ln=True)
    
    # Add a separator
    pdf.ln(10)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)
    
    # Add CSV data
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Transaction Data from CSV:", ln=True)
    pdf.set_font("Arial", size=10)
    
    # Create table headers
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 10, "Date", 1, 0, 'C', True)
    pdf.cell(80, 10, "Description", 1, 0, 'C', True)
    pdf.cell(30, 10, "Amount", 1, 0, 'C', True)
    pdf.cell(30, 10, "Balance", 1, 1, 'C', True)
    
    # Add transaction data
    for index, row in data.iterrows():
        try:
            date_str = row['Date'].strftime('%m/%d/%Y') if pd.notna(row['Date']) else '--'
            desc = str(row['Description'])[:50] if pd.notna(row['Description']) else '--'
            amount = f"${row['Amount']:,.2f}" if pd.notna(row['Amount']) else '--'
            balance = f"${row['Balance']:,.2f}" if pd.notna(row['Balance']) else '--'
            
            pdf.cell(30, 10, date_str, 1)
            pdf.cell(80, 10, desc, 1)
            pdf.cell(30, 10, amount, 1)
            pdf.cell(30, 10, balance, 1, 1)
            
            if pdf.get_y() > 250:
                pdf.add_page()
                # Repeat headers on new page
                pdf.cell(30, 10, "Date", 1, 0, 'C', True)
                pdf.cell(80, 10, "Description", 1, 0, 'C', True)
                pdf.cell(30, 10, "Amount", 1, 0, 'C', True)
                pdf.cell(30, 10, "Balance", 1, 1, 'C', True)
        except Exception as e:
            print(f"Warning: Could not process row {index}: {str(e)}")
            continue
    
    try:
        pdf.output(output_pdf_path)
        print(f"PDF successfully created at {output_pdf_path}")  # Debug print
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        raise

def main():
    pdf_path = "input.pdf"
    csv_path = "data.csv"
    output_pdf_path = "output.pdf"

    try:
        text_content = extract_text_from_pdf(pdf_path)
        data = read_csv_data(csv_path)
        create_pdf_with_data(output_pdf_path, text_content, data)
        print("PDF successfully created!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
