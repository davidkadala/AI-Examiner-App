import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os

# Extract text from normal PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text.strip()

# Extract text from scanned PDFs using OCR
def extract_text_with_ocr(pdf_path, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()

# auto-detect if PDF is scanned or not
def smart_extract_text(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    if len(text.strip()) < 100:
        print("Low text detected, using OCR...")
        text = extract_text_with_ocr(pdf_path)
    return text
