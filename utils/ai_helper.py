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
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY")

def get_gemini_response(prompt, model_name="gemini-1.5-flash"):
    """
    Gemini 호출을 시도하고, 실패하면 None을 반환.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    genai.configure(api_key=api_key)

    models_to_try = [
        model_name,
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
    ]

    for model_id in models_to_try:
        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_text = str(e).lower()

            # 모델 없음이면 다음 모델 시도
            if "404" in error_text or "not found" in error_text:
                continue

            # quota, rate limit, auth 문제 포함 전부 실패 처리
            return None

    return None
    
def analyze_pdf_content(text):
    """
    Analyze JRC MARS Bulletin content for Summary tab.
    """
    prompt = f"""
    Analyze and summarize the JRC MARS Bulletin:
    - Executive Summary
    - Weather Overview
    - Weather Forecast
    - Potato Section
    - EU Country Analysis
    - Yield Forecast
    
    Provide highlights in Korean if possible.
    TEXT:
    {text[:15000]}
    """
    return get_gemini_response(prompt)

def generate_final_report(item, language, tone, pdf_summary, csv_summary):
    """
    Generate final report draft.
    """
    prompt = f"""
    Create a professional market report for: {item}.
    Language: {language}, Tone: {tone}.
    Sources: {pdf_summary} and {csv_summary}.
    """
    return get_gemini_response(prompt)
