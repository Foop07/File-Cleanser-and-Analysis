import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple

# --- Presidio Imports for PII Redaction ---
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

def anonymize_text(text_to_clean: str, client_name: str) -> Tuple[str, List[RecognizerResult]]:
    """
    Analyzes text for PII and a custom client name, then redacts them.

    Args:
        text_to_clean: The raw text extracted from a document.
        client_name: The specific client name to find and redact.

    Returns:
        A tuple containing:
        - The cleaned text string.
        - A list of the analysis results from Presidio (for counting).
    """
    # --- Input Validation ---
    if not text_to_clean or not text_to_clean.strip():
        return "", []
    if not client_name or not client_name.strip():
        # If no client name, still process for other PII
        analyzer = AnalyzerEngine()
        analyzer_results = analyzer.analyze(text=text_to_clean, language='en')
        anonymizer = AnonymizerEngine()
        anonymized_result = anonymizer.anonymize(
            text=text_to_clean,
            analyzer_results=analyzer_results
        )
        return anonymized_result.text, analyzer_results

    try:
        # 1. Create a custom recognizer for the specific client name.
        client_name_recognizer = PatternRecognizer(
            supported_entity="CLIENT_NAME", 
            deny_list=[client_name]
        )
        
        # 2. Set up the Presidio AnalyzerEngine.
        analyzer = AnalyzerEngine()
        analyzer.registry.add_recognizer(client_name_recognizer)

        # 3. Ask the analyzer to find all PII and the custom client name.
        analyzer_results = analyzer.analyze(text=text_to_clean, language='en')

        # 4. Set up the AnonymizerEngine.
        anonymizer = AnonymizerEngine()
        
        # 5. Anonymize the text.
        anonymized_result = anonymizer.anonymize(
            text=text_to_clean,
            analyzer_results=analyzer_results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
                "CLIENT_NAME": OperatorConfig("replace", {"new_value": "<CLIENT_NAME_REDACTED>"})
            }
        )
        
        # 6. Return both the cleaned text and the list of results.
        return anonymized_result.text, analyzer_results
    
    except Exception as e:
        error_message = f"An error occurred during text anonymization: {e}"
        print(error_message)
        return error_message, []


def redact_logo(main_image: Image.Image, logo_image: Image.Image) -> Image.Image:
    """
    Finds a logo within a main image and blacks it out.
    """
    try:
        main_img_cv = np.array(main_image.convert('RGB'))
        logo_img_cv = np.array(logo_image.convert('RGB'))
        
        w, h = logo_img_cv.shape[:-1]

        res = cv2.matchTemplate(main_img_cv, logo_img_cv, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            cv2.rectangle(main_img_cv, pt, (pt[0] + h, pt[1] + w), (0, 0, 0), -1)
        
        return Image.fromarray(main_img_cv)

    except Exception as e:
        print(f"An error occurred during logo redaction: {e}")
        return main_image

