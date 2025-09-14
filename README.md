🔒 Automated File Cleanser and Analyzer

This project is an automated solution designed for security consultants to cleanse and analyze client-provided documents. It processes various file formats, redacts sensitive information (PII, client names, logos), and uses an LLM to extract key security insights, ensuring all data is anonymized and ready for analysis.

Features

    Multi-Format Support: Ingests and extracts text from .pdf, .png, .jpeg, .pptx, and more.

    Automated PII Redaction: Uses Microsoft Presidio to automatically find and mask names, locations, and other sensitive personal data.

    Client-Specific Cleansing: Allows users to specify a client name and logo for targeted redaction.

    Intelligent Analysis: Leverages a fast, open-source LLM (Llama 3.1 via Groq) to extract structured security data like firewall rules and IAM policies.

    Tabular Summary: Presents the final, cleansed findings in a clean and easy-to-read table.

Installation & Setup

Follow these steps to set up the project on your local machine.

1. Clone the repository:

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

2. Create and activate a virtual environment:

# For Windows
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate

# For macOS / Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:
Make sure you have all the required libraries by installing from requirements.txt.

pip install -r requirements.txt

4. Install Tesseract OCR Engine:
This tool requires the Tesseract engine for OCR.

    Download and install it from the official Tesseract repository.

    Important: Note the installation path. You may need to add it to the app.py script if it's not found automatically.

#How to Run the Application

1. Set Your Environment Variable:
This application requires an API key from Groq to perform the AI analysis. Get your free key from the Groq Console.

In your terminal, set the environment variable:

# For Windows (PowerShell)
$env:GROQ_API_KEY="YOUR_API_KEY_HERE"

# For macOS / Linux
export GROQ_API_KEY="YOUR_API_KEY_HERE"

2. Run the Streamlit App:
In the same terminal session, run the following command:

streamlit run app.py

A new tab will open in your browser with the running application.
 Technologies Used

    Backend: Python

    Web Framework: Streamlit

    AI/LLM: Groq API with Llama 3.1

    NLP/PII Redaction: Microsoft Presidio

    OCR: Google Tesseract (pytesseract)

    File Parsing: PyMuPDF, python-pptx


    Image Processing: OpenCV, Pillow
