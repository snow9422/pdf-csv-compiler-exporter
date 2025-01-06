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

def create_pdf_with_data(output_pdf_path, input_pdf_path, data):
    # Create a PDF writer
    pdf_writer = PyPDF2.PdfWriter()
    
    # Read the input PDF
    with open(input_pdf_path, "rb") as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        
        # Copy all pages from the input PDF to the writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])
    
    # Create a temporary PDF with the new content
    temp_pdf_path = "temp_output.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Set margins
    pdf.set_margins(20, 20, 20)
    
    # Add logo at the top
    logo_path = "found_logo.svg"
    current_y = add_svg_logo(pdf, logo_path)
    
    # Add a separator
    pdf.set_y(current_y)
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
    
    pdf.output(temp_pdf_path)
    
    # Merge the original PDF and the new content
    with open(temp_pdf_path, "rb") as temp_pdf_file:
        temp_pdf_reader = PyPDF2.PdfReader(temp_pdf_file)
        for page_num in range(len(temp_pdf_reader.pages)):
            pdf_writer.add_page(temp_pdf_reader.pages[page_num])
    
    # Write the final PDF
    with open(output_pdf_path, "wb") as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    
    # Remove the temporary PDF file
    os.remove(temp_pdf_path)
    
    print(f"PDF successfully created at {output_pdf_path}")

def main():
    input_pdf_path = "input.pdf"
    csv_path = "data.csv"
    output_pdf_path = "output.pdf"

    try:
        data = read_csv_data(csv_path)
        create_pdf_with_data(output_pdf_path, input_pdf_path, data)
        print("PDF successfully created!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
