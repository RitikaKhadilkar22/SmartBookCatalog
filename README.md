# PDF Metadata Extractor

A Python script that automatically extracts metadata from PDF files using AI-powered text analysis and OCR capabilities. Designed specifically for processing Sanskrit, Hindi, and English books/documents.

## Features

- **Dual Text Extraction**: Uses `pdfplumber` for text-based PDFs and OCR fallback for image-based PDFs
- **AI-Powered Metadata Extraction**: Leverages Mistral AI to intelligently extract book information
- **Multi-Language Support**: Detects Sanskrit, Hindi, and English documents
- **Smart Language Detection**: Analyzes filenames and content to determine language
- **Multiple Output Formats**: Generates both CSV and Excel files with formatting
- **Error Handling**: Robust error handling with graceful fallbacks

## Output Columns

The script generates exactly 8 columns in the following sequence:

1. **Book Title** - Title of the book/document
2. **Author** - Author name(s)
3. **Editor** - Editor name(s)
4. **Year of Publishing** - Publication year
5. **Publisher** - Publisher information
6. **Language** - Document language (Hindi/Sanskrit/English)
7. **Number of Pages (optional)** - Total page count
8. **Format (optional)** - File format (always "PDF")

## Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu), Windows, or macOS
- **Python**: 3.7 or higher
- **Tesseract OCR**: For image-based PDF processing

### Python Dependencies
All Python packages are listed in `requirements.txt`:
```
pdfplumber==0.10.0
pandas==2.1.4
requests==2.31.0
pathlib
openpyxl==3.1.2
pytesseract==0.3.10
pdf2image==1.17.0
Pillow==10.1.0
```

## Installation

### 1. Clone or Download the Project

Create a project directory and place the files:
```bash
mkdir ~/sanskrit
cd ~/sanskrit
# Place Assignment.py, requirements.txt, and README.md here
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-san
```

#### Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Uncomment and set the path in Assignment.py if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

### 4. Set Up Mistral AI API

The script uses Mistral AI for intelligent metadata extraction. The API key is already configured in the script, but you may want to:

1. **Use your own API key** (recommended for production):
   - Sign up at https://mistral.ai/
   - Replace `MISTRAL_API_KEY` in Assignment.py with your key

2. **Or use the provided key** for testing (rate-limited)

## Setup

### 1. Create Directory Structure

```bash
mkdir -p ~/sanskrit/books/pdf
```

### 2. Add Your PDF Files

Place all PDF files you want to process in the `books/pdf` directory:
```
~/sanskrit/
├── Assignment.py
├── requirements.txt
├── README.md
└── books/
    └── pdf/
        ├── book1.pdf
        ├── book2.pdf
        └── ...
```

## Usage

### Basic Usage

1. **Navigate to the project directory**:
   ```bash
   cd ~/sanskrit
   ```

2. **Run the script**:
   ```bash
   python Assignment.py
   ```

### Expected Output

The script will:
1. Scan all PDF files in `books/pdf/`
2. Extract text using pdfplumber
3. Fall back to OCR if no text is found
4. Use AI to extract metadata
5. Save results to both CSV and Excel formats

**Output files**:
- `shared_pdfs_metadata.csv` - CSV format
- `shared_pdfs_metadata.xlsx` - Excel with formatting (bold headers, auto-width, frozen panes)

### Sample Console Output

```
OCR libraries loaded successfully
Found 5 PDFs in target folder.

============================================================
Processing: sanskrit_book_1.pdf
============================================================
PDF has 248 pages
Found text on page 1: 1250 characters
API Status Code: 200
Extracted metadata: {'Book Title': 'Sanskrit Grammar', 'Author': 'Unknown', ...}

Processing complete. Results saved to:
   CSV: /home/ritika/sanskrit/shared_pdfs_metadata.csv
   Excel: /home/ritika/sanskrit/shared_pdfs_metadata.xlsx

SUCCESS! Metadata saved at: ('/home/ritika/sanskrit/shared_pdfs_metadata.csv', '/home/ritika/sanskrit/shared_pdfs_metadata.xlsx')
```

## Configuration

### File Paths

You can modify the paths in `Assignment.py`:

```python
# Path to your PDF files
target_folder = "/home/ritika/sanskrit/books/pdf"

# Output directory
output_path = "/home/ritika/sanskrit"
```

### OCR Languages

The script supports multiple OCR languages:
```python
# Try Hindi + English first, fall back to English only
page_text = pytesseract.image_to_string(page, lang='eng+hin')
```

### AI Model Configuration

You can adjust the Mistral AI model:
```python
# Use different models: mistral-tiny, mistral-small, mistral-medium
ai_response = call_mistral_api(prompt, model="mistral-tiny")
```

## Troubleshooting

### Common Issues

1. **"OCR libraries not available"**
   ```bash
   pip install pytesseract pillow pdf2image
   sudo apt-get install tesseract-ocr
   ```

2. **"Target folder not found"**
   ```bash
   mkdir -p ~/sanskrit/books/pdf
   ```

3. **"No PDF files found"**
   - Ensure PDF files are in `~/sanskrit/books/pdf/`
   - Check file extensions (.pdf)

4. **API Errors**
   - Check internet connection
   - Verify Mistral API key is valid
   - Check API rate limits

5. **Permission Errors**
   ```bash
   chmod +x Assignment.py
   ```

### OCR Issues

- **Missing language packs**: Install additional Tesseract language packs
- **Poor OCR quality**: PDFs with low image quality may not extract well
- **Memory issues**: Large PDFs may require more RAM for OCR processing

## Project Structure

```
~/sanskrit/
├── Assignment.py              # Main script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── books/                   # PDF storage
│   └── pdf/                # Place PDF files here
├── shared_pdfs_metadata.csv    # Output CSV (generated)
└── shared_pdfs_metadata.xlsx   # Output Excel (generated)
```

## Technical Details

### Processing Pipeline

1. **File Discovery**: Scans `books/pdf/` for .pdf files
2. **Text Extraction**: 
   - Primary: pdfplumber (for text-based PDFs)
   - Fallback: OCR via pytesseract + pdf2image (for image-based PDFs)
3. **Metadata Extraction**:
   - Filename analysis for language/title hints
   - AI analysis of extracted text
   - Page count extraction
4. **Output Generation**: CSV and Excel files with formatting

### Language Detection Logic

- **Hindi**: Filename contains "hindi" or "हिन्दी"
- **Sanskrit**: Filename contains "sanskrit" or "devanagari"
- **English**: Filename contains "english" or "eng"
- **Default**: "Unknown" if no patterns match

## API Information

- **Mistral AI**: Used for intelligent metadata extraction
- **Rate Limits**: Depends on your API plan
- **Model**: Uses "mistral-tiny" by default (cost-effective)
- **Fallback**: Works without AI if API is unavailable

## Contributing

Feel free to enhance the script by:
- Adding more language detection patterns
- Improving filename parsing logic
- Adding support for other document formats
- Enhancing error handling

## License

This project is for educational and research purposes. Please respect the terms of service of the APIs and libraries used.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure PDF files are in the correct directory
4. Check console output for specific error messages
