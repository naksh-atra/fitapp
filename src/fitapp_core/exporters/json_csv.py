# # src/fitapp_core/exporters/json_csv.py
# from __future__ import annotations

# import io
# import csv
# import json
# from typing import List, Dict, Any  # <- add Any

# def to_json_bytes(plan: Dict[str, Any]) -> bytes:
#     return json.dumps(plan, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

# # v1 (unchanged)
# def to_csv_str(rows: List[Dict[str, Any]]) -> str:
#     buf = io.StringIO()
#     fieldnames = ["day", "movement", "sets", "reps", "tempo_or_rest", "load_prescription", "notes"]
#     writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
#     writer.writeheader()
#     writer.writerows(rows)
#     return buf.getvalue()

# # v1.1 (new)
# def to_csv_str_v11(rows: List[Dict[str, Any]]) -> str:
#     buf = io.StringIO()
#     fieldnames = [
#         "week_label",
#         "day",
#         "day_name",
#         "block_type",
#         "movement",
#         "main_focus",
#         "intensity_cue",
#         "sets",
#         "reps",
#         "duration",
#         "tempo_or_rest",
#         "notes",
#     ]
#     writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
#     writer.writeheader()
#     writer.writerows(rows)
#     return buf.getvalue()




# src/fitapp_core/exporters/json_csv.py
from __future__ import annotations

import io
import csv
import json
from typing import List, Dict, Any
from collections import defaultdict

def _json_normalize(obj: Any) -> Any:
    """
    Recursively convert plan objects to JSON-serializable Python types.
    - numpy.ndarray -> list
    - numpy scalar types -> Python scalars
    - pandas NA -> None
    - bytes -> utf-8 string (fallback latin-1)
    - tuples/sets -> lists
    - unknown objects -> str(obj) as last resort
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except Exception:
            return obj.decode("latin-1", errors="ignore")
    if isinstance(obj, dict):
        return {str(k): _json_normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_json_normalize(x) for x in obj]

    # numpy support
    try:
        import numpy as np  # local import to avoid hard runtime dep if not used
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
    except Exception:
        pass

    # pandas NA handling
    try:
        import pandas as pd  # local import
        # pd.isna returns bool for scalars; for arrays/broadcast it's handled above
        if isinstance(obj, (pd._libs.missing.NAType,)):  # type: ignore[attr-defined]
            return None
        # Fallback scalar NA check
        if isinstance(obj, (float, str)) and pd.isna(obj):
            return None
    except Exception:
        pass

    # Fallback for any other object type
    return str(obj)

def to_json_bytes(plan: Dict[str, Any]) -> bytes:
    """
    Serialize the full v1.1 plan dict to compact JSON with robust type coercion.
    """
    safe = _json_normalize(plan)
    return json.dumps(safe, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

# Back-compat alias
tojsonbytes = to_json_bytes

# v1 legacy CSV (unchanged)
def to_csv_str(rows: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    fieldnames = ["day", "movement", "sets", "reps", "tempo_or_rest", "load_prescription", "notes"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()

# v1.1 full rows CSV
def to_csv_str_v11(rows: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    fieldnames = [
        "week_label","day","day_name","block_type","movement","main_focus","intensity_cue",
        "sets","reps","duration","tempo_or_rest","notes",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()

# Back-compat alias for tests
tocsvstrv11 = to_csv_str_v11

# v1.1 simple CSV (grid-like aggregation)
def to_csv_str_simple_v11(rows: List[Dict[str, Any]]) -> str:
    agg: Dict[tuple, List[str]] = defaultdict(list)
    for r in rows:
        wk = r.get("week_label", "Week 1")
        dn = r.get("day_name", "")
        sets, reps = r.get("sets"), r.get("reps")
        dur = r.get("duration")
        vol = f"{int(sets)}×{int(reps)}" if isinstance(sets, int) and isinstance(reps, int) else (dur or "")
        base = f"{r.get('movement','')} — {vol}".strip(" —")
        note = (r.get("notes") or "").strip()
        agg[(wk, dn)].append(base if not note else f"{base} · {note}")
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["week_label", "day_name", "items"])
    def _week_key(wk: str) -> int:
        try:
            return int(str(wk).split()[-1])
        except Exception:
            return 1
    for (wk, dn), items in sorted(agg.items(), key=lambda t: (_week_key(t[0][0]), t[0][1])):
        writer.writerow([wk, dn, " | ".join(items)])
    return buf.getvalue()
