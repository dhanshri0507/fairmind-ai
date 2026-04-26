import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize the client with your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROFESSIONAL_SYSTEM = """
You are a senior AI fairness auditor writing a compliance report.
Analyse the bias metrics provided and structure your response as:
1. EXECUTIVE SUMMARY (2 sentences - what is the verdict?)
2. ROOT CAUSE ANALYSIS (why does this bias exist?)
3. AFFECTED GROUPS (who is harmed and how?)
4. RECOMMENDED MITIGATIONS (numbered list of specific fixes)
Use precise, professional language. Reference specific metric values.
Keep total response under 300 words.
"""

CASUAL_SYSTEM = """
You are a friendly, plain-speaking AI bias detective.
Explain these bias findings to someone who has never studied data science.
Rules:
- Use everyday language, zero jargon, no statistics terms.
- Use an analogy to explain what the bias means in real life.
- Be direct: tell them clearly if this is a big problem or a small one.
- End with one simple action they can take right now.
- Maximum 150 words.
"""

def explain_bias(audit_results: dict, mode: str = "professional") -> str:
    """
    Generates a professional or casual explanation of bias using Gemini 2.5 Flash.
    """
    system_prompt = PROFESSIONAL_SYSTEM if mode == "professional" else CASUAL_SYSTEM

    user_message = f"Audit Results:\n{json.dumps(audit_results, indent=2)}\n\nPlease provide a {mode} explanation based on the system instructions."

    try:
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_name,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3 if mode == "professional" else 0.6,
                max_output_tokens=1024,
            )
        )
        return response.text
    except Exception as e:
        # A good fallback for the hackathon demo
        return f"The Gemini API encountered an error: {str(e)}. Please check your API key and project setup."
