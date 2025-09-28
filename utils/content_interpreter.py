
import os
import json
from typing import Dict, Any
from utils.logo_detector import detect_logo
from langchain_groq import ChatGroq


def interpret_content(document_text: str, pii_count: int, image_path: str = None, logo_path: str = None) -> Dict[str, Any]:
    """
    Analyze document text and optionally detect logos in an image.

    Args:
        document_text (str): Text extracted from the file.
        pii_count (int): Number of Personally Identifiable Information (PII) items.
        image_path (str, optional): Path to the document image for logo detection.
        logo_path (str, optional): Path to the logo template image.

    Returns:
        Dict[str, Any]: Structured analysis result.
    """
    analysis = {
        "executive_summary": "",
        "pii_sensitivity_level": "Unknown",
        "detailed_findings": {},
        "logos_detected": [],
    }

    try:
        if not os.getenv("GROQ_API_KEY"):
            analysis["error"] = "GROQ_API_KEY environment variable not set!"
            return analysis

        client = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")

        prompt = f"""
        Analyze the following document text for security and privacy risks.

        Text: {document_text}
        PII count: {pii_count}

        Provide:
        - Executive Summary
        - PII Sensitivity Level (Low, Medium, High, Critical)
        - Detailed Findings (firewall rules, IAM policies, IPs, hostnames, and general observations)

        Return response in JSON format only.
        """

        # --- FIX: handle AIMessage response properly ---
        response = client.invoke(prompt)

        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        try:
            parsed_output = json.loads(response_text)
            analysis.update(parsed_output)
        except json.JSONDecodeError:
            analysis["error"] = "Failed to parse AI response"
            analysis["raw_output"] = response_text

        # --- Logo detection if both paths provided ---
        if image_path and logo_path:
            logo_found = detect_logo(image_path, logo_path)
            analysis["logos_detected"] = [logo_path] if logo_found else []

    except Exception as e:
        analysis["error"] = f"AI analysis failed: {str(e)}"

    return analysis
