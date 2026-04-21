import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load local .env if exists
load_dotenv()

def get_api_key():
    """
    Retrieves API key from Streamlit secrets (for Cloud) 
    or environment variables (for local/AI Studio).
    """
    # Prefer OpenAI Key
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY")

def get_ai_response(prompt, model_name="gpt-4o"):
    """
    Generic function to get response from OpenAI GPT with robust key check.
    """
    api_key = get_api_key()
    if not api_key:
        return "⚠️ OpenAI API Key is not configured. \n\n" \
               "**How to fix:**\n" \
               "1. Get an API key from [platform.openai.com](https://platform.openai.com/).\n" \
               "2. Add `OPENAI_API_KEY = \"YOUR_KEY\"` in Streamlit Secrets or environment variables."
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional market analyst specializing in EU agriculture."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to OpenAI API: {str(e)}"

def analyze_pdf_content(text):
    """
    Analyze JRC MARS Bulletin content and structure it for the Summary tab using GPT.
    """
    prompt = f"""
    Analyze the following JRC MARS Bulletin text and summarize it into professional sections.
    Use Korean for labels if the user language is set to Korean.
    Sections: Executive Summary, Weather Overview, Weather Forecast, Potato Section, EU Country Analysis, Yield Forecast.
    TEXT:
    {text[:15000]}
    """
    return get_ai_response(prompt)

def generate_final_report(item, language, tone, pdf_summary, csv_summary):
    """
    Generate the final consolidated market report using GPT.
    """
    prompt = f"""
    Create a professional market report for: {item}.
    Language: {language}, Tone: {tone}.
    Sources: {pdf_summary} and {csv_summary}.
    Structure: Introduction, Qualitative Analysis, Quantitative Analysis, Conclusion.
    """
    return get_ai_response(prompt)
