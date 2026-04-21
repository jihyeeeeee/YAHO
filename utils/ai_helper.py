import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, model_name="gemini-1.5-flash"):
    """
    Generic function to get response from Gemini.
    """
    if not api_key:
        return "Gemini API Key is not configured. Please check your .env file or Secrets panel."
    
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

    Use Markdown for formatting.
    
    TEXT:
    {text[:15000]} # Limit text length for token safety
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
    - PDF Analysis Summary:
    {pdf_summary}
    
    - Quantitative Data Summary (Price, FX, SCFI, Energy trends):
    {csv_summary}

    Structure:
    1. Introduction
    2. Qualitative Analysis (Weather, Crop status)
    3. Quantitative Analysis (Market Data trends)
    4. Conclusion & Outlook
    
    Generate the report in {language}.
    """
    return get_gemini_response(prompt)
