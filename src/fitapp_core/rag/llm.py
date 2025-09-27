#v1


# #basic placeholder
# from typing import List, Dict

# def call_llm_json(prompt: str) -> List[Dict]:
#     return [
#         {"day": 1, "movement": "Squat", "sets": 3, "reps": 8, "tempo_or_rest": "2-0-2", "load_prescription": "RPE 7", "notes": "Warm-up first."},
#         {"day": 1, "movement": "Bench Press", "sets": 3, "reps": 8, "tempo_or_rest": "2-1-2", "load_prescription": "RPE 7", "notes": ""},
#         {"day": 2, "movement": "Deadlift", "sets": 3, "reps": 5, "tempo_or_rest": "1-0-1", "load_prescription": "RPE 8", "notes": "Straps optional."},
#     ]



# # src/fitapp_core/rag/llm.py
# import os, json
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=".env.local")


# BASE_URL = "https://api.perplexity.ai"
# MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")  # or "sonar"
# API_KEY = os.getenv("PERPLEXITY_API_KEY")

# _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# SYSTEM_JSON_ONLY = (
#     "Return ONLY a JSON array of objects with fields: "
#     "day, movement, sets, reps, tempo_or_rest, load_prescription, notes."
# )

# def call_llm_json(user_prompt: str):
#     resp = _client.chat.completions.create(
#         model=MODEL,
#         temperature=0,
#         messages=[
#             {"role": "system", "content": SYSTEM_JSON_ONLY},
#             {"role": "user", "content": user_prompt},
#         ],
#         response_format={"type": "json_object"},
#         # Perplexity-specific options are available if needed, e.g. search filters
#         # see docs for search_mode/search_recency_filter/etc.
#         max_tokens=800,
#     )
#     content = resp.choices[0].message.content
#     return json.loads(content)



# import os, json
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=".env.local")

# BASE_URL = "https://api.perplexity.ai"
# MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")  # or "sonar"
# API_KEY = os.getenv("PERPLEXITY_API_KEY")

# _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# SYSTEM_JSON_ONLY = (
#     "Return ONLY a JSON array of objects with fields: "
#     # "day, movement, sets, reps, tempo_or_rest, load_prescription, notes, ONLY FOR 3 DAYS."
#     "day, movement, sets, reps, ONLY FOR 1 DAY."
# )




# PLAN_SCHEMA = {
#     "name": "plan_schema",
#     "schema": {
#         "type": "array",
#         "items": {
#             "type": "object",
#             "properties": {
#                 "day": {"type": "string"},
#                 "movement": {"type": "string"},
#                 "sets": {"type": "string"},
#                 "reps": {"type": "string"},
#             },
#             "required": ["day", "movement", "sets", "reps"],
#             "additionalProperties": False,
#         },
#     },
# }
# def call_llm_json(user_prompt: str):
#     resp = _client.chat.completions.create(
#         model=MODEL,
#         temperature=0,
#         messages=[
#             {"role": "system", "content": SYSTEM_JSON_ONLY},
#             {"role": "user", "content": user_prompt},
#         ],
#         response_format={"type": "json_schema", "json_schema": PLAN_SCHEMA},
#         max_tokens=20000,
#     )
#     print("RAW RESPONSE >>>")
#     print(resp.choices[0].message.content)
#     return json.loads(resp.choices[0].message.content)












import os, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

BASE_URL = "https://api.perplexity.ai"
MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
API_KEY = os.getenv("PERPLEXITY_API_KEY")

_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Ask LLM to return integers for 'day' and 'reps'
SYSTEM_JSON_ONLY = (
    "Return ONLY a JSON array of objects with fields: "
    "day (integer), movement (string), sets (string), reps (integer), "
    "ONLY FOR 1 DAY. Do NOT include any extra fields."
)

PLAN_SCHEMA = {
    "name": "plan_schema",
    "schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "day": {"type": "integer"},
                "movement": {"type": "string"},
                "sets": {"type": "string"},
                "reps": {"type": "integer"},
            },
            "required": ["day", "movement", "sets", "reps"],
            "additionalProperties": False,
        },
    },
}

def call_llm_json(user_prompt: str):
    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_JSON_ONLY},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_schema", "json_schema": PLAN_SCHEMA},
        max_tokens=2000,
    )
    raw_content = resp.choices[0].message.content
    print("RAW RESPONSE >>>")
    print(raw_content)

    # Try parsing JSON; fallback to cleaning numeric fields
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        # Optional: quick fix for string numbers like "Day 1" or "8-12"
        raw_content = raw_content.replace("Day ", "")
        raw_content = raw_content.replace("-", ",")  # handle ranges if necessary
        data = json.loads(raw_content)
    
    # Ensure day and reps are integers
    for row in data:
        if isinstance(row.get("day"), str):
            row["day"] = int(''.join(filter(str.isdigit, row["day"])))
        if isinstance(row.get("reps"), str):
            row["reps"] = int(''.join(filter(str.isdigit, row["reps"])))

    return data
