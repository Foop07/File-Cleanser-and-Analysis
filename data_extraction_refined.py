import os
import json
from langchain_groq import ChatGroq

# LangChain's specialized tool for structured data extraction
from langchain.chains import create_extraction_chain

# IMPORTANT: Set up your Groq API Key
# 1. Go to groq.com, sign up for a free account.
# 2. Get your API key and set it as an environment variable.
# In your terminal:
# For Windows: set GROQ_API_KEY=your_key_here
# For macOS/Linux: export GROQ_API_KEY=your_key_here

def extract_structured_data_with_groq(text_to_analyze):
    """
    Uses Groq's fast Llama 3 model to extract specific security data from text.
    """
    # 1. The schema remains exactly the same. We are just swapping the engine.
    schema = {
        "properties": {
            "firewall_rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "string"},
                        "source_ip": {"type": "string"},
                        "destination_port": {"type": "string"},
                        "action": {"type": "string", "enum": ["ALLOW", "DENY", "REJECT"]},
                        "description": {"type": "string"},
                    },
                },
            },
            "iam_policies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "policy_name": {"type": "string"},
                        "principal": {"type": "string"},
                        "effect": {"type": "string", "enum": ["Allow", "Deny"]},
                        "action": {"type": "string"},
                        "resource": {"type": "string"},
                    },
                },
            },
        },
        "required": ["firewall_rules", "iam_policies"],
    }

    # 2. Initialize the LLM - THIS IS THE ONLY PART THAT CHANGES!
    # We're swapping ChatOpenAI for ChatGroq and specifying an open-source model.
    llm = ChatGroq(
        temperature=0, 
        model_name="llama3-8b-8192" # Using Llama 3 8B model on Groq
    )

    # 3. The extraction chain setup is identical.
    chain = create_extraction_chain(schema=schema, llm=llm)

    # 4. Run the chain on our text
    print("Extracting structured data with Groq...")
    extracted_data = chain.run(text_to_analyze)
    print("Extraction complete.")
    
    return extracted_data

# --- EXAMPLE USAGE ---
if __name__ == '__main__':
    sample_cleansed_text = """
    Security audit for <CLIENT_NAME_REDACTED> completed on <DATE>.
    
    Firewall configuration analysis:
    Rule 45: DENY source 10.0.0.50 to port 80. Description: Block web traffic from legacy server.
    Rule 46: ALLOW source 192.168.1.0/24 to port 443. Description: Allow internal HTTPS access.

    Access Management Review:
    The policy named S3-Read-Only grants user 'data-analyst-role' the ability to perform 's3:GetObject' on all objects in the 'production-data-bucket'. Effect is Allow.
    """

    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable not set.")
        print("Please sign up at groq.com, get a key, and set it before running.")
    else:
        insights = extract_structured_data_with_groq(sample_cleansed_text)
        
        print("\n--- Extracted Security Insights (via Groq/Llama 3) ---")
        print(json.dumps(insights, indent=2))
        print("-" * 50)
