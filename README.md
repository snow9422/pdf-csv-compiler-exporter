# PDF CSV Compiler

This script reads a PDF file, extracts its content, reads data from a CSV file, and outputs a new PDF with the combined data and a logo.

## Requirements

Ensure you have the required libraries installed:
```sh
pip install PyPDF2 pandas reportlab svglib chardet
```

## Usage

1. Place your input PDF file as `input.pdf`, your CSV file as `data.csv`, and your logo file as `found_logo.svg` in the same directory as the script.

2. Run the script:
```sh
python pdf_csv_compiler.py
```

This will generate a new PDF file named `output.pdf` with the content from the input PDF, the data from the CSV file, and the logo.

## Script Details

- `extract_text_from_pdf(pdf_path)`: Extracts all text content from the PDF.
- `read_csv_data(csv_path)`: Reads data from the CSV file with proper encoding detection and data cleaning.
- `add_svg_logo(pdf, svg_path, x=20, y=20, width=50)`: Adds the SVG logo to the PDF.
- `create_pdf_with_data(output_pdf_path, text_content, data)`: Creates a new PDF with the extracted text content, CSV data, and logo.

## Example

1. Ensure your directory structure looks like this:
```
/c:/Users/<username>/pdf_csv_compiler/
│
├── input.pdf
├── data.csv
├── found_logo.svg
├── pdf_csv_compiler.py
└── README.md
```
Replace `<username>` with your root username.

2. Run the script:
```sh
python pdf_csv_compiler.py
```

3. The output PDF will be generated as `output.pdf` in the same directory.

## Notes

- The script automatically detects the encoding of the CSV file using `chardet`.
- The script cleans up the CSV data by replacing `--` with `NA` and converting date, amount, and balance columns to appropriate formats.
- The logo is added at the top of the output PDF, followed by the content from the input PDF and the transaction data from the CSV file.
