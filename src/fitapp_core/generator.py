# Pure Python module implementing the rules‑first workout plan generator so logic is reusable, testable, and decoupled from UI per Python structuring guidelines.

# file: generator.py
from __future__ import annotations
from typing import Dict, Any, List
from retriever import retrieve_snippets
from prompts import SYSTEM_PROMPT_V11, USER_TEMPLATE_V11, render_snippets_for_v11
from llm import generate as llm_generate

# Optional: centralize retrieval defaults
_TOP_K = 6
_DEFAULT_EVIDENCE_LEVEL = "evidence"  # can be "experience" if desired

def _make_retrieval_query(profile: Dict[str, Any]) -> str:
    goal = str(profile.get("goal", "")).strip()
    freq = str(profile.get("days_per_week", "")).strip()
    equip = str(profile.get("equipment", "")).strip()
    pop = str(profile.get("experience", "")).strip()
    return f"{goal}, {pop}, {freq} days/week, equipment: {equip}".strip(", ")

def _format_user_template(profile: Dict[str, Any], snippets_text: str) -> str:
    sex = profile.get("sex", "")
    age = profile.get("age", "")
    height_cm = profile.get("height_cm", "")
    weight_kg = profile.get("weight_kg", "")
    pal_value = profile.get("pal_value", "")
    goal = profile.get("goal", "")
    equipment = profile.get("equipment", "")
    bmr = profile.get("bmr", "")
    tdee = profile.get("tdee", "")
    tweak = profile.get("tweak", "")
    return USER_TEMPLATE_V11.format(
        sex=sex,
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        pal_value=pal_value,
        goal=goal,
        equipment=equipment,
        bmr=bmr,
        tdee=tdee,
        snippets=snippets_text,
        tweak=tweak,
    )

def generate_plan_with_context(user_instructions: str, snippets: List[Dict]) -> Dict[str, Any]:
    texts = [s["text"] for s in snippets]
    formatted_snippets = render_snippets_for_v11(texts)
    # Compose a single prompt string; SYSTEM enforces JSON‑only, USER provides inputs + evidence
    prompt = f"{SYSTEM_PROMPT_V11}\n\n{user_instructions}"
    # Call the model
    output = llm_generate(prompt)
    # Carry source mapping for UI/PDF
    sources = [{"n": i+1, "chunk_id": s["id"], "doc_id": s.get("doc_id")} for i, s in enumerate(snippets)]
    return {
        "text": output,                  # JSON array string (per SYSTEM_PROMPT_V11)
        "sources": sources,              # for citations in UI/PDF
        "snippets_count": len(snippets),
    }

def generate_plan(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrates retrieval + generation.
    Returns:
      {
        "text": <JSON array string>,
        "sources": [{"n": int, "chunk_id": str, "doc_id": str}, ...],
        "retrieval_query": str,
        "snippets_count": int
      }
    """
    # 1) Build retrieval query from the user profile
    query = _make_retrieval_query(profile)

    # 2) Retrieve grounded snippets (optionally filter by domain/evidence)
    domains = profile.get("domain_filters")  # e.g., ["strength"] / ["hypertrophy"] or None
    evidence = profile.get("evidence_level", _DEFAULT_EVIDENCE_LEVEL)
    hits = retrieve_snippets({
        "query": query,
        "domains": domains,
        "evidence": evidence,
        "top_k": _TOP_K,
    })

    # 3) Fill the v11 user template with inputs and evidence excerpts
    evidence_block = render_snippets_for_v11([h["text"] for h in hits]) if hits else ""
    user_instructions = _format_user_template(profile, evidence_block)

    # 4) Compose final prompt (SYSTEM + USER) and generate JSON-only output
    prompt = f"{SYSTEM_PROMPT_V11}\n\n{user_instructions}"
    output = llm_generate(prompt)

    # 5) Return output plus source mapping for UI and PDF export
    sources = [{"n": i+1, "chunk_id": h["id"], "doc_id": h.get("doc_id")} for i, h in enumerate(hits)]
    return {
        "text": output,
        "sources": sources,
        "retrieval_query": query,
        "snippets_count": len(hits),
    }
