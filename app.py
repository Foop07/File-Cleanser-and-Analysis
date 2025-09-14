# app.py
import streamlit as st
from processor import process_document # We will create this function next
from utils.text_extractor import extract_text_from_file
from data_cleanser import anonymize_text_with_presidio, redact_logo_from_image

st.title("📄 Document Cleanser and Analyzer")

uploaded_file = st.file_uploader("Upload a document to be cleansed and analyzed", type=['pdf', 'png', 'jpeg', 'xlsx', 'pptx'])

if uploaded_file is not None:
    st.info("Processing your document... Please wait.")
    
    # This is the main trigger
    # It sends the uploaded file to your backend logic
    clean_text, extracted_data = process_document(uploaded_file)
    
    st.subheader("✅ Cleansed Text")
    st.text_area("Anonymized Text", clean_text, height=250)
    
    st.subheader("📊 Extracted Insights")
    st.json(extracted_data)
    # ... inside your file uploader logic ...
    
    # Step 1: Extract raw text
    raw_text = extract_text_from_file(uploaded_file_path)
    
    # Step 2: Anonymize the text
    # (You'll need a way for the user to input the client name)
    client_name = st.text_input("Enter Client Name to Redact")
    clean_text = anonymize_text_with_presidio(raw_text, client_name)
    
    # Step 3: Redact the logo (if the file is an image)
    # (You'll need a file uploader for the logo)
    logo_file = st.file_uploader("Upload Client Logo")
    if file_is_image and logo_file:
        redacted_image = redact_logo_from_image(uploaded_file_path, logo_file_path)
        st.image(redacted_image)
    
    st.text_area("Cleaned Text", clean_text)