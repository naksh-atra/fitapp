# src/fitapp_core/exporters/json_csv.py
from __future__ import annotations

import io
import csv
import json
from typing import List, Dict, Any  # <- add Any

def to_json_bytes(plan: Dict[str, Any]) -> bytes:
    return json.dumps(plan, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

# v1 (unchanged)
def to_csv_str(rows: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    fieldnames = ["day", "movement", "sets", "reps", "tempo_or_rest", "load_prescription", "notes"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()

# v1.1 (new)
def to_csv_str_v11(rows: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    fieldnames = [
        "week_label",
        "day",
        "day_name",
        "block_type",
        "movement",
        "main_focus",
        "intensity_cue",
        "sets",
        "reps",
        "duration",
        "tempo_or_rest",
        "notes",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
