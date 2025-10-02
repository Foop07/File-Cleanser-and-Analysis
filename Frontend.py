import streamlit as st
import os
from PIL import Image

from utils.text_extractor import extract_text
from utils.data_cleanser import anonymize_text
from utils.content_interpreter import identify_client_name, interpret_content



# UI RENDERING FUNCTIONS


def display_report(file, result):
    """
    Renders a single, detailed intelligence report with metrics and findings.
    
    Args:
        file: Uploaded file object
        result: Analysis result dictionary
    """
    st.header(f"📄 Intelligence Report: {file.name}")

    # Metrics Display
    col1, col2 = st.columns(2)
    
    col1.metric("File Type", os.path.splitext(file.name)[1])
    
    pii_level = result.get('pii_sensitivity_level', 'N/A')
    pii_colors = {
        "None": "🟢",
        "Low": "🟡", 
        "Medium": "🟠",
        "High": "🔴",
        "Critical": "🔴"
    }
    pii_icon = pii_colors.get(pii_level, "⚪")
    col2.metric("PII Sensitivity Level", f"{pii_icon} {pii_level}")


    # Executive Summary 
    st.markdown("---")
    st.subheader("📋 Executive Summary")
    st.write(result.get('executive_summary', 'No summary available.'))
    

    # Detailed Findings 
    st.subheader("🔍 Detailed Findings")
    findings = result.get('detailed_findings', {})
    
    if not findings or all(not v for v in findings.values()):
        st.info("No detailed findings were extracted from this document.")
    else:
        for category, items in findings.items():
            if items:
                st.markdown(f"**{category.replace('_', ' ').title()}**")
                for item in items:
                    with st.expander(f"• {item['title']}"):
                        st.write(item['description'])

# MAIN APPLICATION
st.set_page_config(
    layout="wide", 
    page_title="Intelligent File Analyzer",
    page_icon="🚀"
)

st.title("🚀 Intelligent File Analyzer")
st.info(
    "📤 Upload one or more documents. The AI will automatically identify the client, "
    "cleanse the data, and generate a detailed security report for each file."
)


# File Upload Section
uploaded_files = st.file_uploader(
    "📁 Upload Documents for Analysis",
    type=['pdf', 'png', 'jpeg', 'jpg', 'pptx', 'xlsx'],
    accept_multiple_files=True
)

# Analysis Button & Processing Pipeline
if st.button("🔬 Generate Intelligence Reports", type="primary"):
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one file to begin analysis.")
    else:
        st.header("📊 Batch Analysis Results")
        
        for file in uploaded_files:
            st.markdown("---")
            
            with st.spinner(f"⚙️ Processing {file.name}..."):
                file_extension = os.path.splitext(file.name)[1].lower()

                # PIPELINE STEP 1: Text Extraction
                extraction_result = extract_text(file)
                raw_text = extraction_result.get("text")
                error = extraction_result.get("error")

                # Check for extraction errors
                if error:
                    st.error(f"❌ **{file.name}**: Could not process file. Reason: {error}")
                    continue

                # Validate extracted text quality
                if not raw_text or len(raw_text.strip()) < 10:
                    st.warning(
                        f"⚠️ **{file.name}**: Very little text could be extracted. "
                        "The file may be empty or the OCR quality is poor."
                    )
                    continue

                # PIPELINE STEP 2: Client Identification
                client_name = identify_client_name(raw_text)
                st.write(f"🏢 AI identified client for **{file.name}** as: **{client_name}**")
                
                # PIPELINE STEP 3: Data Anonymization
                anonymized_text, pii_results = anonymize_text(raw_text, client_name)
                pii_count = len(pii_results)
                
                # PIPELINE STEP 4: Content Analysis
                analysis_result = interpret_content(anonymized_text, pii_count)

                if "error" in analysis_result:
                    st.error(f"❌ Could not analyze {file.name}: {analysis_result['error']}")
                else:
                    display_report(file, analysis_result)
        
        st.success("✅ Batch processing complete!")
