import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Optional

# --- Pydantic models for structured output (same as before) ---
class Finding(BaseModel):
    """A model for a single, categorized finding."""
    title: str = Field(description="A short, bold headline for the finding.")
    description: str = Field(description="A one or two-sentence explanation of the finding.")

class CategorizedFindings(BaseModel):
    """A model to hold lists of findings, grouped by category."""
    firewall_rules: Optional[List[Finding]] = Field(None, description="A list of all extracted firewall rules.")
    iam_policies: Optional[List[Finding]] = Field(None, description="A list of all extracted IAM policies.")
    security_observations: Optional[List[Finding]] = Field(None, description="Other notable security-related observations.")

class IntelligentSummary(BaseModel):
    """The final, detailed analysis report structure."""
    executive_summary: str = Field(description="A two or three-sentence executive summary of the document's content and overall risk.")
    pii_sensitivity_level: str = Field(description="An assessment of the PII risk level based on the count of PII found.", enum=["None", "Low", "Medium", "High", "Critical"])
    detailed_findings: CategorizedFindings = Field(description="A structured breakdown of all key findings, categorized appropriately.")

# --- AI STEP 1: IDENTIFY THE CLIENT NAME ---
def identify_client_name(text_to_analyze: str) -> str:
    """
    Uses a fast LLM call to find the most likely client/company name in the text.
    """
    if not text_to_analyze or not text_to_analyze.strip():
        return "Unknown"
    
    try:
        # A very focused prompt for a simple task
        prompt = ChatPromptTemplate.from_template(
            "Analyze the following document text. Identify the primary company, organization, or client that this document is about. Look for repeated company names in headers, footers, or titles. Respond with ONLY the single most likely company name, and nothing else. If you cannot determine the name with high confidence, respond with the word 'Unknown'."
        )
        llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
        # A simple string parser is enough for this task
        chain = prompt | llm | StrOutputParser()
        
        client_name = chain.invoke({"input": text_to_analyze})
        
        # Clean up the output
        client_name = client_name.strip().replace('"', '')
        return client_name if client_name and client_name != "Unknown" else "Unknown"
        
    except Exception as e:
        print(f"Error during client identification: {e}")
        return "Unknown"

# --- AI STEP 2: PERFORM DETAILED ANALYSIS ---
def interpret_content(text_to_analyze: str, pii_count: int) -> Dict:
    """
    Uses a strictly prompted LLM to generate a factual, detailed analysis of the text.
    (This is the robust function from our previous step).
    """
    if not os.getenv("GROQ_API_KEY"):
        return {"error": "GROQ_API_KEY environment variable not set!"}
    if not text_to_analyze or not text_to_analyze.strip():
        return {
            "executive_summary": "No text could be extracted from the document for analysis.",
            "pii_sensitivity_level": "None",
            "detailed_findings": {}
        }

    try:
        parser = JsonOutputParser(pydantic_object=IntelligentSummary)
        prompt_template = """
        You are a Tier-3 cybersecurity analyst. Your task is to provide a detailed and factual analysis of a document.
        Follow these steps precisely:
        1.  Assess PII Risk: Based on the provided PII count ({pii_count}), determine the sensitivity level (None, Low, Medium, High, Critical).
        2.  Extract Entities: Identify and extract ONLY specific security entities like Firewall Rules, IAM Policies, IP addresses, or hostnames.
        3.  Generate Summary & Findings: Write a brief executive summary and categorize all extracted entities with bold titles.

        **CRITICAL RULES**:
        - Do not invent information if the text is nonsensical or empty.
        - Base your analysis strictly on the provided text.
        - Do not suggest "further investigation".
        
        Respond ONLY with a JSON object in this format: {format_instructions}
        
        **Document Text to Analyze**:
        {text}
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
        chain = prompt | llm | parser

        return chain.invoke({
            "text": text_to_analyze,
            "pii_count": pii_count,
            "format_instructions": parser.get_format_instructions()
        })
    except Exception as e:
        return {"error": f"An error occurred during AI analysis: {e}"}

