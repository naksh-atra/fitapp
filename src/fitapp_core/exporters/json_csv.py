#v1
import json, io, csv
from typing import Dict, List

CSV_FIELDS = ["day","movement","sets","reps","tempo_or_rest","load_prescription","notes"]

def to_json_bytes(plan: Dict) -> bytes:
    return json.dumps(plan, indent=2).encode("utf-8")

def to_csv_str(rows: List[Dict]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
