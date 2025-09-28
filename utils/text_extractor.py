


import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pptx import Presentation
import pandas as pd
import cv2
import numpy as np
import streamlit as st
from PyPDF2 import PdfReader

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# -------------------------
# 1. SIMPLE FILE TEXT EXTRACTION
# -------------------------
def extract_text_from_file(file):
    """
    Extract text from .txt, .csv, .pdf files (Streamlit uploaded files)
    """
    filename = file.name.lower()

    # Text files
    if filename.endswith(".txt"):
        return file.read().decode("utf-8")

    # CSV files
    elif filename.endswith(".csv"):
        df = pd.read_csv(file)
        return df.to_string(index=False)

    # PDF files
    elif filename.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    else:
        return ""

# -------------------------
# 2. IMAGE PREPROCESSING FOR OCR
# -------------------------
def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    img_cv = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    h, w = thresh.shape
    if h < 500 or w < 500:
        thresh = cv2.resize(thresh, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
    return Image.fromarray(thresh)

# -------------------------
# 3. LOGO DETECTION
# -------------------------
def detect_logos(image: Image.Image, logo_folder: str = "assets/logos/", threshold: float = 0.8) -> dict:
    """Detects multiple logos in an image and returns {logo_name: True/False}."""
    results = {}
    if not os.path.exists(logo_folder):
        return results  # Safe if folder missing
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    for logo_file in os.listdir(logo_folder):
        logo_path = os.path.join(logo_folder, logo_file)
        logo = cv2.imread(logo_path)
        if logo is None:
            continue
        logo_gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, logo_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        results[logo_file] = len(loc[0]) > 0
    return results

# -------------------------
# 4. MAIN TEXT EXTRACTION FUNCTION
# -------------------------
def extract_text(uploaded_file) -> dict:
    """
    Determines file type and extracts text.
    Returns: {"text": str, "logos_detected": dict (optional), "error": str}
    """
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        # --- IMAGE FILES ---
        if file_extension in ['.jpg', '.jpeg', '.png']:
            image = Image.open(uploaded_file)
            processed_image = preprocess_image_for_ocr(image)
            text = pytesseract.image_to_string(processed_image)
            logos_detected = detect_logos(image)
            return {"text": text, "logos_detected": logos_detected, "error": None}

        # --- TXT, CSV, PDF ---
        elif file_extension in ['.txt', '.csv', '.pdf']:
            text = extract_text_from_file(uploaded_file)
            return {"text": text, "error": None}

        # --- PPTX ---
        elif file_extension == '.pptx':
            text = ""
            prs = Presentation(uploaded_file)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            return {"text": text, "error": None}

        # --- XLSX ---
        elif file_extension == '.xlsx':
            text = ""
            excel_sheets = pd.read_excel(uploaded_file, sheet_name=None)
            for sheet_name, df in excel_sheets.items():
                text += f"--- Sheet: {sheet_name} ---\n{df.to_string()}\n\n"
            return {"text": text, "error": None}

        # --- UNSUPPORTED FILES ---
        else:
            return {"text": None, "error": f"Unsupported file format: {file_extension}"}

    except Exception as e:
        return {"text": None, "error": f"Error processing {uploaded_file.name}: {e}"}

# -------------------------
# 5. STREAMLIT APP
# -------------------------
st.title("File Cleanser & Logo Detection")

uploaded_file = st.file_uploader("Upload your file")
if uploaded_file:
    result = extract_text(uploaded_file)

    if result.get("error"):
        st.error(result["error"])
    else:
        st.subheader("Extracted Text")
        st.text_area("", value=result.get("text", ""), height=300)

        if "logos_detected" in result:
            st.subheader("Logo Detection")
            if result["logos_detected"]:
                for logo, detected in result["logos_detected"].items():
                    st.write(f"{logo}: {'Detected ✅' if detected else 'Not detected ❌'}")
            else:
                st.write("No logos detected or logo folder missing.")
