import os
import sys
import pdfplumber
import pandas as pd
import requests
import json
import re
from pathlib import Path

# OCR imports with error handling
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    # Tesseract configuration (usually auto-detected on Linux)
    # For Linux, Tesseract is typically in PATH after installation
    # If needed, uncomment and set custom path:
    # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    OCR_AVAILABLE = True
    print("OCR libraries loaded successfully")
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"OCR libraries not available: {e}")
    print("Install with: pip install pytesseract pillow pdf2image")

# API Configuration (Mistral)
MISTRAL_API_KEY = "ommxGRJdPbFNl4sGxQqsSvv9QniYkQ7A"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def call_mistral_api(prompt, model="mistral-tiny"):
    """Call Mistral AI API with error handling"""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        print(f"API Status Code: {response.status_code}")

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"API Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def extract_text_with_ocr(pdf_path, max_pages=5):
    """Extract text using OCR for image-based PDFs"""
    if not OCR_AVAILABLE:
        print("OCR not available. Please install required packages.")
        return ""

    try:
        print("Converting PDF to images for OCR...")
        pages = convert_from_path(pdf_path, first_page=1, last_page=max_pages, dpi=200)

        extracted_text = ""
        for i, page in enumerate(pages):
            print(f"Processing page {i+1} with OCR...")
            
            try:
                page_text = pytesseract.image_to_string(page, lang='eng+hin')
            except:
                page_text = pytesseract.image_to_string(page, lang='eng')

            if page_text.strip():
                extracted_text += f"--- Page {i+1} (OCR) ---\n{page_text}\n"
                print(f"OCR found {len(page_text)} characters on page {i+1}")
            else:
                print(f"No text found on page {i+1}")

        return extracted_text

    except Exception as e:
        print(f"OCR extraction failed: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber and OCR fallback"""
    text = ""
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"PDF has {total_pages} pages")

            pages_to_check = min(5, total_pages)
            text_found = False

            for i in range(pages_to_check):
                try:
                    page_text = pdf.pages[i].extract_text()
                    if page_text and page_text.strip():
                        text += f"--- Page {i+1} ---\n{page_text}\n"
                        text_found = True
                        print(f"Found text on page {i+1}: {len(page_text)} characters")
                except Exception as e:
                    print(f"Error extracting from page {i+1}: {e}")

            if not text_found:
                print("No extractable text found. Trying OCR...")
                ocr_text = extract_text_with_ocr(pdf_path, max_pages=3)
                if ocr_text:
                    text += ocr_text
                    text_found = True
                    print("OCR extraction successful")
                else:
                    print("OCR extraction failed or no text found")

            filename = os.path.basename(pdf_path)
            if filename:
                text += f"\n[FILENAME: {filename}]\n"

            text += f"\n[DOCUMENT INFO: Total pages in document: {total_pages}]\n"

            if not text_found:
                print("WARNING: No text found via any method!")

    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")
        return ""

    return text
def extract_basic_metadata(text, pdf_path=""):
    # Follow the exact sequence requested
    metadata = {
        "Book Title": "Unknown",
        "Author": "Unknown",
        "Editor": "Unknown",
        "Year of Publishing": "Unknown",
        "Publisher": "Unknown",
        "Language": "Unknown",
        "Number of Pages ": "Unknown",
        "Format ": "PDF"
    }

    # Extract language from filename and text
    filename_pattern = r'\[FILENAME: (.+?)\]'
    filename_match = re.search(filename_pattern, text)
    if filename_match:
        filename = filename_match.group(1)
        print(f"Analyzing filename: {filename}")
        
        filename_lower = filename.lower()
        if any(term in filename_lower for term in ['hindi', 'हिन्दी']):
            metadata["Language"] = "Hindi"
        elif any(term in filename_lower for term in ['sanskrit', 'devanagari']):
            metadata["Language"] = "Sanskrit"
        elif any(term in filename_lower for term in ['english', 'eng']):
            metadata["Language"] = "English"
        
        # Try to extract title from filename
        filename_clean = filename.replace('.pdf', '').replace('.PDF', '')
        if '_' in filename:
            parts = filename_clean.split('_')
            meaningful_parts = [p.strip() for p in parts if len(p.strip()) > 3]
            if meaningful_parts:
                title_candidate = max(meaningful_parts, key=len).replace('-', ' ').strip()
                metadata["Book Title"] = title_candidate

    # Extract page count
    page_pattern = r'Total pages in document: (\d+)'
    page_match = re.search(page_pattern, text)
    if page_match:
        metadata["Number of Pages "] = page_match.group(1)

    return metadata

def clean_and_parse_json(json_string):
    try:
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        json_match = re.search(r'\{.*\}', json_string, re.DOTALL)
        if json_match:
            json_string = json_match.group()
        ai_data = json.loads(json_string)
        
        # Map AI response to our column names
        mapped_metadata = {}
        if "title" in ai_data and ai_data["title"] != "Unknown":
            mapped_metadata["Book Title"] = ai_data["title"]
        if "author" in ai_data and ai_data["author"] != "Unknown":
            mapped_metadata["Author"] = ai_data["author"]
        if "year" in ai_data and ai_data["year"] != "Unknown":
            mapped_metadata["Year of Publishing"] = ai_data["year"]
        if "publisher" in ai_data and ai_data["publisher"] != "Unknown":
            mapped_metadata["Publisher"] = ai_data["publisher"]
        if "language" in ai_data and ai_data["language"] != "Unknown":
            mapped_metadata["Language"] = ai_data["language"]
        if "pages" in ai_data and ai_data["pages"] != "Unknown":
            mapped_metadata["Number of Pages "] = ai_data["pages"]
        
        return mapped_metadata
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return {}

def extract_metadata_from_text(text, pdf_path=""):
    basic_metadata = extract_basic_metadata(text, pdf_path)
    if len(text.strip()) < 100:
        print("Limited text available. Using filename analysis only.")
        return basic_metadata

    prompt = f"""
    You are given text from a PDF's first two pages.
    Extract metadata as JSON with these keys:
    title, author, year, publisher, language, pages, format
    Text:
    {text[:2000]}
    """

    ai_response = call_mistral_api(prompt)
    if ai_response:
        ai_metadata = clean_and_parse_json(ai_response)
        final_metadata = basic_metadata.copy()
        final_metadata.update({k: v for k, v in ai_metadata.items() if v != "Unknown"})
        return final_metadata

    return basic_metadata

def process_single_pdf(pdf_path):
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")
    
    try:
        text = extract_text_from_pdf(pdf_path)
        print(f"Extracted text length: {len(text)} characters")
        
        metadata = extract_metadata_from_text(text, pdf_path)
        print(f"Extracted metadata: {metadata}")
        return metadata
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return {
            "Book Title": "Processing Error",
            "Author": "Error",
            "Editor": "Error", 
            "Year of Publishing": "Error",
            "Publisher": "Error",
            "Language": "Error",
            "Number of Pages ": "Error",
            "Format ": "PDF"
        }

def process_all_pdfs_batch():
    # Path to your PDFs (Linux path)
    target_folder = "/home/ritika/sanskrit/books/pdf"

    # Path to output folder (current directory)
    output_path = "/home/ritika/sanskrit"

    output_csv = os.path.join(output_path, "shared_pdfs_metadata.csv")
    output_xlsx = os.path.join(output_path, "shared_pdfs_metadata.xlsx")

    # If folder missing
    if not os.path.exists(target_folder):
        print(f"Target folder not found: {target_folder}")
        return None

    # Get all PDFs
    pdf_files = [os.path.join(target_folder, f) for f in os.listdir(target_folder) if f.lower().endswith(".pdf")]

    # If no PDFs found
    if not pdf_files:
        print("No PDF files found in the target folder!")
        return None

    print(f"\nFound {len(pdf_files)} PDFs in target folder.")

    all_metadata = []
    for pdf_path in pdf_files:
        metadata = process_single_pdf(pdf_path)
        all_metadata.append(metadata)

    if all_metadata:
        df = pd.DataFrame(all_metadata)

        # Save as CSV
        df.to_csv(output_csv, index=False)

        # Save as Excel with formatting
        with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="PDF_Metadata")

            workbook = writer.book
            worksheet = writer.sheets["PDF_Metadata"]

            # Make header bold
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)

            # Autofit column widths
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

            # Freeze top row
            worksheet.freeze_panes = "A2"

        print(f"\nProcessing complete. Results saved to:")
        print(f"   CSV: {output_csv}")
        print(f"   Excel: {output_xlsx}")

        # Show preview of available columns
        available_columns = df.columns.tolist()
        preview_columns = [col for col in ['Book Title', 'Author', 'Publisher'] if col in available_columns]
        if preview_columns:
            print(df[preview_columns].head())
        else:
            print(df.head())
        return output_csv, output_xlsx
    else:
        print("No metadata was extracted!")
        return None


if __name__ == "__main__":
    output_files = process_all_pdfs_batch()
    if output_files:
        print(f"\nSUCCESS! Metadata saved at: {output_files}")
    else:
        print("No output generated.")
