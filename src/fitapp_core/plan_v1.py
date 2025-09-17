from typing import Optional, List
from .models import Inputs, Plan, PlanRow, PAL_MAP
from .energy import bmr_mifflin_st_jeor, tdee_from_bmr
from .rag.retriever import retrieve_snippets
from .rag.prompts import USER_TEMPLATE
from .rag.llm import call_llm_json

def generate_plan_v1(inputs: Inputs, tweak_note: Optional[str] = None) -> Plan:
    pal_value = PAL_MAP[inputs.pal_code]
    bmr = bmr_mifflin_st_jeor(inputs.sex, inputs.weight_kg, inputs.height_cm, inputs.age)
    tdee = tdee_from_bmr(bmr, pal_value)
    snippets = retrieve_snippets(inputs.model_dump())
    snippets_text = "\n".join(f"- [{s.get('id','doc')}]: {s['text']}" for s in snippets) or "- none"
    prompt = USER_TEMPLATE.format(
        age=inputs.age, sex=inputs.sex, height_cm=inputs.height_cm, weight_kg=inputs.weight_kg,
        pal_value=pal_value, tdee=tdee, goal=inputs.goal, snippets=snippets_text
    )
    if tweak_note:
        prompt += f"\nUser tweak: {tweak_note}\n"
    rows_json = call_llm_json(prompt)
    rows: List[PlanRow] = [PlanRow(**r) for r in rows_json]
    return Plan(goal=inputs.goal, pal_value=pal_value, bmr=bmr, tdee=tdee, rows=rows)
