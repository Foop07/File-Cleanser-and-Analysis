import streamlit as st
from utils.content_interpreter import interpret_content
from utils.logo_detector import detect_logo
import os

# Set your GROQ API key here if not using environment variable
# os.environ["GROQ_API_KEY"] = "your_api_key_here"

st.title("File Cleanser & Logo Detection")

# --- File Upload ---
st.header("1. Upload Document")
doc_file = st.file_uploader("Upload a document (PDF, TXT, DOCX, XLSX)", type=["pdf", "txt", "docx", "xlsx", "csv"])

st.header("2. Upload Logo Image (Optional)")
logo_file = st.file_uploader("Upload logo image to check", type=["png", "jpg", "jpeg", "bmp"])

st.header("3. Document Text & PII Count")
doc_text = st.text_area("Paste document text (optional, will override extracted text)")
pii_count = st.number_input("Enter PII count (number)", min_value=0, value=0)

# --- Process on Button Click ---
if st.button("Analyze Document"):
    text_to_analyze = doc_text
    # Extract text from uploaded file if doc_text not provided
    if doc_file and not doc_text:
        from utils.text_extractor import extract_text_from_file
        text_to_analyze = extract_text_from_file(doc_file)
    
    # Logo detection
    logos_detected = []
    if logo_file and doc_file:
        logos_detected = detect_logo(doc_file, logo_file)  # assuming your detect_logo can take file-like objects
    
    # Content analysis
    result = interpret_content(text_to_analyze, pii_count)
    
    # Add logos to result
    result["logos_detected"] = logos_detected

    # --- Display Results ---
    st.subheader("--- Analysis Result ---")
    st.json(result)
