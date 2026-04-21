import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load local .env if exists
load_dotenv()

def get_api_key():
    """
    Retrieves API key from Streamlit secrets (for Cloud) 
    or environment variables (for local/AI Studio).
    """
    # 1. Try Streamlit Secrets (Highest priority for Streamlit Cloud)
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    
    # 2. Try Environment Variables
    return os.getenv("GEMINI_API_KEY")

def configure_genai():
    """Configures the Gemini API library with the current key."""
    api_key = get_api_key()
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def get_gemini_response(prompt, model_name="gemini-1.5-flash"):
    """
    Generic function to get response from Gemini with robust key check.
    """
    if not configure_genai():
        return "⚠️ Gemini API Key is not configured correctly. \n\n" \
               "**How to fix:**\n" \
               "1. If deploying to **Streamlit Cloud**: Add `GEMINI_API_KEY = \"YOUR_KEY\"` in the 'Secrets' panel.\n" \
               "2. If in **AI Studio Build**: Add `GEMINI_API_KEY` to the 'Secrets' menu (Gear icon -> Secrets)."
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini API: {str(e)}"

def analyze_pdf_content(text):
    """
    Analyze JRC MARS Bulletin content and structure it for the Summary tab.
    """
    prompt = f"""
    Below is text extracted from a JRC MARS Bulletin PDF. 
    Analyze and summarize it into the following sections in a professional business tone:
    1. Executive Summary (Overall sentiment)
    2. Weather Overview (Past conditions)
    3. Weather Forecast (Upcoming conditions)
    4. Potato Section (Specific updates on potatoes)
    5. EU Country Analysis (Key highlights per major country)
    6. Yield Forecast (Quantitative expectations)
    7. Key Highlights (Bullet points of main takeaways)

    Use Markdown for formatting. Use Korean if possible for the final summary labels.
    
    TEXT:
    {text[:15000]}
    """
    return get_gemini_response(prompt)

def generate_final_report(item, language, tone, pdf_summary, csv_summary):
    """
    Generate the final consolidated market report.
    """
    prompt = f"""
    Create a professional market report draft for the following item: {item}.
    
    Specifications:
    - Language: {language}
    - Tone: {tone}
    
    Information Sources:
    - PDF Analysis Summary: {pdf_summary}
    - Quantitative Data Summary: {csv_summary}

    Structure:
    1. Introduction
    2. Qualitative Analysis (Weather, Crop status)
    3. Quantitative Analysis (Market Data trends)
    4. Conclusion & Outlook
    
    Generate the report in {language}.
    """
    return get_gemini_response(prompt)
