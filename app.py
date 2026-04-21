import streamlit as st
import pandas as pd
import os
from utils.data_processor import load_csv_safely, get_pdf_page_image, extract_text_from_pdf, get_sample_data
from utils.ai_helper import analyze_pdf_content, generate_final_report
import io

# Page Config
st.set_page_config(page_title="EU Market Intelligence Dashboard", layout="wide")

# Custom CSS for Professional Polish Design Theme
st.markdown("""
    <style>
    /* Main Background following bg-slate-50 */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    /* Sidebar following bg-slate-800 */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #60a5fa !important; /* blue-400 */
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #94a3b8; /* slate-400 */
    }

    /* Tab Styling following Design HTML Tab Bar */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 16px;
        background-color: transparent !important;
        border: none !important;
        font-weight: 500;
        color: #64748b; /* slate-500 */
        font-size: 14px;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important; /* blue-600 */
        border-bottom: 3px solid #2563eb !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #334155; /* slate-700 */
    }

    /* Card-like containers for content areas */
    .report-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* shadow-sm */
        margin-bottom: 20px;
    }
    
    .status-badge {
        background-color: #eff6ff;
        color: #1d4ed8;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Buttons */
    .stButton > button {
        background-color: #0f172a; /* slate-900 */
        color: #ffffff;
        border-radius: 9999px;
        padding: 8px 24px;
        font-size: 12px;
        font-weight: 700;
        border: none;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #1e293b;
        transform: translateY(-1px);
    }
    
    /* Input fields */
    .stSelectbox, .stTextInput {
        border-radius: 4px;
    }

    /* Custom Header */
    .dashboard-title {
        color: #0f172a;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
    }
    .dashboard-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 2rem;
    }
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Footer */
    .dashboard-footer {
        border-top: 1px solid #e2e8f0;
        padding: 20px 0;
        color: #94a3b8;
        font-size: 11px;
        display: flex;
        justify-content: space-between;
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# Application Header
st.markdown('<h1 class="dashboard-title">EU Report AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="dashboard-subtitle">Agricultural Market Intelligence • Analysis & Draft System</p>', unsafe_allow_html=True)

# Sidebar for Uploads
with st.sidebar:
    st.header("📄 Data Upload")
    pdf_file = st.file_uploader("Upload JRC MARS PDF", type="pdf")
    market_csv = st.file_uploader("Upload Market Data CSV (Price/FX/SCFI)", type="csv")
    energy_csv = st.file_uploader("Upload Energy Data CSV", type="csv")
    
    st.divider()
    st.info("Files can be omitted. Sample data will be used automatically.")

# Initialize Session State
if 'pdf_summary' not in st.session_state:
    st.session_state.pdf_summary = "Please upload a PDF and process it on the 'Report Summary' tab."
if 'processed_pdf' not in st.session_state:
    st.session_state.processed_pdf = None

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Report Summary", "📈 Data & Charts", "🔍 PDF Preview", "📝 Final Report"])

# --- Tab 1: Report Summary ---
with tab1:
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">'
                '<h2 style="margin: 0; font-size: 20px;">Bulletin Summary</h2>'
                '<div>'
                '<span class="status-badge">Live Cycle</span>'
                '</div></div>', unsafe_allow_html=True)
    
    if pdf_file:
        if st.button("Analyze PDF Content"):
            with st.spinner("Analyzing PDF with Gemini..."):
                pdf_bytes = pdf_file.read()
                st.session_state.processed_pdf = pdf_bytes
                text = extract_text_from_pdf(pdf_bytes)
                if text:
                    summary = analyze_pdf_content(text)
                    st.session_state.pdf_summary = summary
                pdf_file.seek(0)
        
        st.markdown(st.session_state.pdf_summary)
    else:
        st.warning("Upload a JRC MARS Bulletin PDF to see the analysis.")
        st.info("Example: JRC MARS Bulletin covers weather synthesis, crop yields, and forecast maps.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: Data & Charts ---
with tab2:
    st.header("Market Trend Visualizations")
    
    # Load Data
    df_market = None
    if market_csv:
        df_market = load_csv_safely(market_csv)
    elif os.path.exists("sample_market_data.csv"):
        df_market = load_csv_safely("sample_market_data.csv")
    
    df_energy = None
    if energy_csv:
        df_energy = load_csv_safely(energy_csv)
    elif os.path.exists("sample_energy_data.csv"):
        df_energy = load_csv_safely("sample_energy_data.csv")
    
    # Fallback to Dummy Generator if still None
    if df_market is None or df_energy is None:
        sample_df = get_sample_data()
        if df_market is None: df_market = sample_df
        if df_energy is None: df_energy = sample_df

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Trends")
        price_col = next((c for c in df_market.columns if 'Price' in c), df_market.columns[1])
        st.line_chart(df_market, y=price_col)
        st.caption("Interpretation: Price trends reflect supply-demand balance and regional crop expectations.")
        
        st.subheader("Exchange Rate (EUR/Local)")
        fx_col = next((c for c in df_market.columns if 'Rate' in c or 'FX' in c), df_market.columns[2] if len(df_market.columns)>2 else df_market.columns[1])
        st.line_chart(df_market, y=fx_col)
        st.caption("Interpretation: Currency fluctuations impact export competitiveness and import costs.")

    with col2:
        st.subheader("SCFI (Freight Index)")
        scfi_col = next((c for c in df_market.columns if 'SCFI' in c or 'Freight' in c), df_market.columns[3] if len(df_market.columns)>3 else df_market.columns[1])
        st.line_chart(df_market, y=scfi_col)
        st.caption("Interpretation: Shipping freight costs significantly affect landed cost prices.")
        
        st.subheader("Energy/Power Prices")
        energy_price_col = next((c for c in df_energy.columns if 'Price' in c), df_energy.columns[1])
        st.line_chart(df_energy, y=energy_price_col)
        st.caption("Interpretation: Energy costs influence processing and storage expenses.")

# --- Tab 3: PDF Preview ---
with tab3:
    st.header("Key Bulletin Pages Preview")
    
    if pdf_file or st.session_state.processed_pdf:
        pdf_data = st.session_state.processed_pdf if st.session_state.processed_pdf else pdf_file.read()
        
        pages_to_show = {
            "Page 3: Weather Synthesis": 2,
            "Page 5: Weather Forecast": 4,
            "Page 10: Potato Section": 9,
            "Page 24: Yield Forecast Map": 23,
            "Page 25: Yield Forecast Map (Cont.)": 24,
            "Page 26: Yield Forecast Map (Cont.)": 25
        }
        
        selected_label = st.selectbox("Select Page to Preview", list(pages_to_show.keys()))
        target_page = pages_to_show[selected_label]
        
        img = get_pdf_page_image(pdf_data, target_page)
        if img:
            st.image(img, use_column_width=True, caption=selected_label)
        else:
            st.error(f"Could not render page {target_page + 1}. The PDF might have fewer pages.")
    else:
        st.info("Upload a PDF file to enable preview.")
        st.image("https://picsum.photos/seed/pdfpreview/800/600", caption="Sample Preview Placeholder")

# --- Tab 4: Final Report ---
with tab4:
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.subheader("Generate Consolidated Report")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        item_opt = st.selectbox("Select Item", ["Potato", "Wheat", "Maize", "Barley"])
    with col_b:
        lang_opt = st.radio("Language", ["Korean", "English"], horizontal=True)
    with col_c:
        tone_opt = st.select_slider("Report Tone", options=["Concise", "Professional", "Detailed"])
        
    if st.button("Generate Final Report Draft", type="primary"):
        csv_summary = f"Current trends: Price {df_market.iloc[-1][1]}, FX {df_market.iloc[-1][2]}, Freight {df_market.iloc[-1][3] if len(df_market.columns)>3 else 'N/A'}"
        
        with st.spinner("Synthesizing data into report..."):
            report_text = generate_final_report(
                item_opt, 
                lang_opt, 
                tone_opt, 
                st.session_state.pdf_summary, 
                csv_summary
            )
            st.session_state.final_report = report_text
            
    if 'final_report' in st.session_state:
        st.text_area("Resulting Report", st.session_state.final_report, height=400)
        st.download_button(
            label="Download Report as Text",
            data=st.session_state.final_report,
            file_name=f"Market_Report_{item_opt}.txt",
            mime="text/plain"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# Footer placed at the end of the script
st.markdown("""
    <div class="dashboard-footer">
        <div>System Status: Ready • Last analyzed: 2025-07-24 14:32</div>
        <div>v1.0-draft • EU Market Insight Engine • Professional Polish Theme</div>
    </div>
    """, unsafe_allow_html=True)
