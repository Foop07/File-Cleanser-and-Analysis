import streamlit as st
import os
from PIL import Image

# --- Import our dedicated backend modules ---
from utils.text_extractor import extract_text
from utils.data_cleanser import anonymize_text
from utils.content_interpreter import identify_client_name, interpret_content

# --- UI Rendering Function ---
def display_report(file, result):
    """Renders a single, detailed intelligence report."""
    st.header(f"Intelligence Report: {file.name}")

    col1, col2 = st.columns(2)
    col1.metric("File Type", os.path.splitext(file.name)[1])
    pii_level = result.get('pii_sensitivity_level', 'N/A')
    col2.metric("PII Sensitivity Level", pii_level)
    
    st.markdown("---")
    st.subheader("Executive Summary")
    st.write(result.get('executive_summary', 'No summary available.'))
    
    st.subheader("Detailed Findings")
    findings = result.get('detailed_findings', {})
    if not findings or all(not v for v in findings.values()):
        st.info("No detailed findings were extracted from this document.")
    else:
        for category, items in findings.items():
            if items:
                st.markdown(f"**{category.replace('_', ' ').title()}**")
                for item in items:
                    with st.expander(f"{item['title']}"):
                        st.write(item['description'])

# --- Main Application UI ---
st.set_page_config(layout="wide", page_title="Intelligent File Analyzer")
st.title("🚀 Intelligent File Analyzer")
st.info("Upload one or more documents. The AI will automatically identify the client, cleanse the data, and generate a detailed security report for each file.")

uploaded_files = st.file_uploader(
    "Upload Documents for Analysis",
    type=['pdf', 'png', 'jpeg', 'jpg', 'pptx', 'xlsx'],
    accept_multiple_files=True
)

if st.button("Generate Intelligence Reports", type="primary"):
    if not uploaded_files:
        st.warning("Please upload at least one file to begin analysis.")
    else:
        st.header("Batch Analysis Results")
        
        for file in uploaded_files:
            st.markdown("---")
            with st.spinner(f"Processing {file.name}..."):
                
                # --- PIPELINE STEP 1: TEXT EXTRACTION ---
                extraction_result = extract_text(file)
                raw_text = extraction_result.get("text")
                error = extraction_result.get("error")

                # --- NEW: ERROR CHECK ---
                # If the extractor returned an error, display it and skip to the next file.
                if error:
                    st.error(f"**{file.name}**: Could not process file. Reason: {error}")
                    continue # This is the key change to stop the pipeline for this file.
                
                # --- The rest of the pipeline only runs if there was no error ---
                client_name = identify_client_name(raw_text)
                st.write(f"🤖 AI identified client for **{file.name}** as: **{client_name}**")
                
                anonymized_text, pii_results = anonymize_text(raw_text, client_name)
                pii_count = len(pii_results)
                
                analysis_result = interpret_content(anonymized_text, pii_count)

                if "error" in analysis_result:
                    st.error(f"Could not analyze {file.name}: {analysis_result['error']}")
                else:
                    display_report(file, analysis_result)
        
        st.success("✅ Batch processing complete.")

