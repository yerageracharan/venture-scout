from __future__ import annotations
import json
import os
import urllib.request
from .models import Company
from .scoring import score_company, diligence_gaps


def draft_ai_diligence(company: Company) -> str:
    """Optional OpenAI-compatible endpoint, including local Ollama. Never invent evidence."""
    base = os.getenv("LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LLM_MODEL", "")
    api_key = os.getenv("LLM_API_KEY", "")
    if not base or not model:
        raise RuntimeError("Configure LLM_BASE_URL and LLM_MODEL. A local Ollama OpenAI-compatible endpoint also works.")
    result = score_company(company)
    payload = {
        "company": company.to_dict(),
        "scorecard": result,
        "diligence_gaps": diligence_gaps(company),
        "instructions": "Write a rigorous seed-stage venture diligence memo. Separate verified facts, founder claims, analyst hypotheses, and unknowns. Do not invent TAM, ARR, customers, retention, team credentials, valuation, cap table, or investor terms. Call out evidence quality and cite supplied URLs inline. Include bull case, bear case, key assumptions, 10 diligence questions, and 3 falsifiable milestones. Treat missing data as unknown, not zero. Do not claim affiliation with any VC firm.",
    }
    body = json.dumps({
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "You are an evidence-first institutional venture research analyst. Precision and epistemic humility matter more than persuasive writing."},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(f"{base}/chat/completions", data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=90) as response:
        data = json.loads(response.read().decode())
    return data["choices"][0]["message"]["content"]
