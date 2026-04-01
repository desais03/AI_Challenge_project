# llm_reasoner.py (HYBRID VERSION)

import os
import requests
from typing import Dict


# -----------------------------
# FALLBACK (ALWAYS WORKS)
# -----------------------------
def fallback_explanation(evaluation: Dict) -> str:
    explanation = []

    explanation.append(
        f"This claim is {evaluation['verdict'].lower()} with an approval probability of {evaluation['approval_probability']}%."
    )

    if evaluation["icd_valid"]:
        explanation.append("The diagnosis code aligns with the procedure requirements.")
    else:
        explanation.append("The diagnosis code does not align well with the procedure.")

    if evaluation["missing_rules"]:
        explanation.append("The following requirements are missing:")
        for rule in evaluation["missing_rules"]:
            explanation.append(f"- {rule}")
    else:
        explanation.append("All major policy conditions are satisfied.")

    return "\n".join(explanation)


# -----------------------------
# OPENAI (OPTIONAL)
# -----------------------------
def try_openai(prompt: str) -> str | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if not os.getenv("OPENAI_API_KEY"):
            return None

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception:
        return None


# -----------------------------
# OLLAMA (LOCAL AI)
# -----------------------------
def try_ollama(prompt: str) -> str | None:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        )

        if response.status_code == 200:
            return response.json()["response"]

        return None

    except Exception:
        return None


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def generate_ai_explanation(
    clinical_note: str,
    icd_code: str,
    cpt_code: str,
    evaluation: Dict,
    policy_rules: list
) -> str:

    prompt = f"""
You are a medical insurance reviewer.

Clinical Note:
{clinical_note}

ICD: {icd_code}
CPT: {cpt_code}

Policy Rules:
{policy_rules}

System Output:
Approval Probability: {evaluation['approval_probability']}%
Verdict: {evaluation['verdict']}

Explain clearly:
- Why approved or denied
- What is missing
- Keep it short and professional
"""

    # 1️⃣ Try OpenAI
    openai_result = try_openai(prompt)
    if openai_result:
        return openai_result

    # 2️⃣ Try Ollama (local)
    ollama_result = try_ollama(prompt)
    if ollama_result:
        return ollama_result

    # 3️⃣ Always fallback
    return fallback_explanation(evaluation)