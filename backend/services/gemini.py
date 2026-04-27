import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("fairmind.gemini")

# Initialize the client with your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Fallback model chain — tries each in order until one works
MODEL_CHAIN = [
    os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"),
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

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

# Static fallback used when ALL Gemini models are quota-exhausted
STATIC_FALLBACK = {
    "professional": (
        "## Compliance Report: Bias Audit Findings\n\n"
        "### 1. EXECUTIVE SUMMARY\n"
        "The audit has detected statistically significant bias across one or more protected attributes. "
        "Immediate review of the model's training data and decision thresholds is recommended.\n\n"
        "### 2. ROOT CAUSE ANALYSIS\n"
        "Bias typically originates from historical imbalances in training data, proxy variables correlated "
        "with protected attributes, or threshold policies applied uniformly across heterogeneous subgroups.\n\n"
        "### 3. AFFECTED GROUPS\n"
        "Groups with lower positive rates face systematic disadvantage in model outcomes, "
        "which may constitute unlawful discrimination under relevant fairness regulations.\n\n"
        "### 4. RECOMMENDED MITIGATIONS\n"
        "1. Apply Reweighing or Disparate Impact Remover in pre-processing.\n"
        "2. Implement Equalized Odds post-processing to calibrate decision thresholds per group.\n"
        "3. Schedule quarterly fairness audits with updated data.\n\n"
        "_(AI explanation unavailable — Gemini API quota reached. This is a pre-generated summary.)_"
    ),
    "casual": (
        "🔍 **Here's what we found in plain English:**\n\n"
        "Your AI model is treating different groups of people unequally — like a job interview process "
        "that keeps rejecting candidates from certain backgrounds without a fair reason.\n\n"
        "This is a **real problem** that needs attention. The good news? It's fixable!\n\n"
        "**One thing you can do right now:** Use the Simulate tab above to try bias mitigation strategies "
        "like Reweighing — it can reduce the gap significantly.\n\n"
        "_(Gemini AI quota reached for today. This is a pre-written summary. Try again tomorrow!)_"
    ),
}


def explain_bias(audit_results: dict, mode: str = "professional") -> str:
    """
    Generates a professional or casual explanation of bias using Gemini.
    Tries each model in MODEL_CHAIN before falling back to a static response.
    Never raises — always returns a string.
    """
    system_prompt = PROFESSIONAL_SYSTEM if mode == "professional" else CASUAL_SYSTEM
    user_message = (
        f"Audit Results:\n{json.dumps(audit_results, indent=2)}\n\n"
        f"Please provide a {mode} explanation based on the system instructions."
    )

    last_error = None
    for model_name in MODEL_CHAIN:
        try:
            logger.info(f"Trying Gemini model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3 if mode == "professional" else 0.6,
                    max_output_tokens=1024,
                ),
            )
            logger.info(f"Success with model: {model_name}")
            return response.text
        except Exception as e:
            err_str = str(e)
            logger.warning(f"Model {model_name} failed: {err_str[:120]}")
            last_error = err_str
            # Only continue the chain on quota/rate-limit errors
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                continue
            # For other errors (auth, network) break immediately
            break

    # All models failed — return friendly static fallback
    logger.error(f"All Gemini models exhausted. Last error: {last_error}")
    return STATIC_FALLBACK.get(mode, STATIC_FALLBACK["professional"])
