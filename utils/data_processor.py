import pandas as pd
import fitz  # PyMuPDF
import io
from PIL import Image
import streamlit as st

def load_csv_safely(file_path_or_buffer):
    """
    Safely load CSV with multiple encoding attempts.
    """
    encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin-1']
    for enc in encodings:
        try:
            if isinstance(file_path_or_buffer, str):
                df = pd.read_csv(file_path_or_buffer, encoding=enc)
            else:
                file_path_or_buffer.seek(0)
                df = pd.read_csv(file_path_or_buffer, encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error loading CSV with {enc}: {str(e)}")
            continue
    return None

def get_pdf_page_image(pdf_data, page_num):
    """
    Render a PDF page to an image using PyMuPDF.
    """
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        if page_num < 0 or page_num >= doc.page_count:
            return None
        
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Zoom for better quality
        img_data = pix.tobytes("png")
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        st.error(f"Error rendering PDF page {page_num + 1}: {str(e)}")
        return None

def extract_text_from_pdf(pdf_data):
    """
    Extract all text from PDF for analysis.
    """
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def get_sample_data():
    """
    Returns fallback sample data for charts.
    """
    import numpy as np
    dates = pd.date_range(start="2024-01-01", periods=12, freq='ME')
    data = {
        'Date': dates,
        'Price': np.random.uniform(900, 1000, 12),
        'ExchangeRate': np.random.uniform(1400, 1500, 12),
        'SCFI': np.random.uniform(2000, 3000, 12),
        'PowerPrice': np.random.uniform(50, 150, 12)
    }
    return pd.DataFrame(data)
