# from fpdf import FPDF
# from typing import Dict, List

# def _safe_text(text: str) -> str:
#     """Replace Unicode chars that crash with Helvetica/core fonts."""
#     return text.replace("•", "-").replace("—", "-").replace("–", "-").replace("×", "x")

# def _render_sources(pdf: FPDF, plan: dict) -> None:
#     """
#     Append a 'Sources' section using the same mapping used in the UI:
#     plan["sources"] = [{"n": 1, "doc_id": "...", "chunk_id": "..."}]
#     Falls back to plan["retrieved_snippets"] if present to reconstruct minimal mapping.
#     """
#     sources: List[Dict] = plan.get("sources") or []
#     if not sources and plan.get("retrieved_snippets"):
#         sources = [
#             {"n": i + 1, "doc_id": s.get("doc_id"), "chunk_id": s.get("id")}
#             for i, s in enumerate(plan["retrieved_snippets"])
#         ]
#     if not sources:
#         return

#     pdf.ln(3)
#     pdf.set_font("Helvetica", style="B", size=11)
#     pdf.cell(0, 7, "Sources", new_x="LMARGIN", new_y="NEXT")

#     pdf.set_font("Helvetica", size=9)
#     for s in sources:
#         n = s.get("n")
#         doc_id = s.get("doc_id", "?")
#         chunk_id = s.get("chunk_id", "?")
#         line = _safe_text(f"[{n}] doc {doc_id} · chunk {chunk_id}")
#         pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

# def build_pdf_v11(plan: dict) -> bytes:
#     rows = plan.get("rows") or []
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Helvetica", size=14)
#     pdf.cell(0, 10, "Fitapp Workout Plan", new_x="LMARGIN", new_y="NEXT")
#     pdf.set_font("Helvetica", size=10)
#     goal_line = _safe_text(f"Goal: {plan['goal']} - Weeks: {plan.get('week_count', 4)}")
#     pdf.cell(0, 6, goal_line, new_x="LMARGIN", new_y="NEXT")
#     pdf.ln(2)

#     # Group flattened rows by week/day for presentation
#     from itertools import groupby
#     key = lambda r: (r.get("week_label","Week 1"), r["day"], r.get("day_name",""))
#     for (week, day, day_name), group in groupby(sorted(rows, key=key), key):
#         pdf.set_font("Helvetica", style="B", size=11)
#         pdf.cell(0, 7, _safe_text(f"{week} - {day_name}"), new_x="LMARGIN", new_y="NEXT")
#         section_order = ["main", "accessory", "prehab", "cardio_notes"]
#         grp = list(group)
#         for section in section_order:
#             sect_rows = [r for r in grp if r["block_type"] == section]
#             if not sect_rows:
#                 continue
#             pdf.set_font("Helvetica", style="", size=10)
#             pdf.cell(0, 6, section.replace("_"," ").title(), new_x="LMARGIN", new_y="NEXT")
#             pdf.set_font("Helvetica", size=9)
#             headers = ["Movement","Focus/Intensity","SetsxReps/Duration","Notes"]
#             widths = [58, 50, 38, 44]
#             for h, w in zip(headers, widths):
#                 pdf.cell(w, 6, h, border=1)
#             pdf.ln()
#             for r in sect_rows:
#                 focus = ((r.get("main_focus") or "") + (" - " + r["intensity_cue"] if r.get("intensity_cue") else "")).strip(" -")
#                 vol = f"{r['sets']}x{r['reps']}" if r.get("sets") and r.get("reps") else (r.get("duration") or "")
#                 values = [
#                     _safe_text((r["movement"] or "")[:40]),
#                     _safe_text((focus or "")[:38]),
#                     _safe_text((vol or "")[:18]),
#                     _safe_text((r.get("notes") or "")[:44]),
#                 ]
#                 for v, w in zip(values, widths):
#                     pdf.cell(w, 6, v, border=1)
#                 pdf.ln()
#         pdf.ln(2)

#     _render_sources(pdf, plan)
#     buf = pdf.output(dest="S")
#     return bytes(buf) if isinstance(buf, (bytearray, bytes)) else buf.encode("latin1")



# src/fitapp_core/exporters/pdf.py
from __future__ import annotations

from fpdf import FPDF
from typing import Dict, List, Tuple

DAY_ORDER = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def _safe_text(text: str) -> str:
    return (text or "").replace("•","-").replace("—","-").replace("–","-").replace("×","x")

def _cell_lines(day_rows: List[dict]) -> List[str]:
    lines: List[str] = []
    order = ["main", "accessory", "prehab", "cardio_notes"]
    for section in order:
        for r in (row for row in day_rows if row.get("block_type") == section):
            sets = r.get("sets"); reps = r.get("reps"); dur = r.get("duration")
            vol = f"{int(sets)}×{int(reps)}" if isinstance(sets, int) and isinstance(reps, int) else (dur or "")
            base = f"{r.get('movement','')} — {vol}".strip(" —")
            note = (r.get("notes") or "").strip()
            lines.append(base if not note else f"{base} · {note}")
    return lines or ["(no items)"]

def _week_labels(rows: List[dict]) -> List[str]:
    labs = sorted({r.get("week_label","Week 1") for r in rows},
                  key=lambda w: int(str(w).split()[-1]) if str(w).startswith("Week") else 1)
    if not labs:
        labs = ["Week 1","Week 2","Week 3","Week 4"]
    return labs

def _group(rows: List[dict]) -> Dict[str, Dict[str, List[dict]]]:
    out: Dict[str, Dict[str, List[dict]]] = {}
    for r in rows:
        wk = r.get("week_label","Week 1"); dn = r.get("day_name","")
        out.setdefault(wk, {}).setdefault(dn, []).append(r)
    return out

def _multi_cell_measure(pdf: FPDF, w: float, line_h: float, text: str) -> float:
    """
    Render text in a multi_cell and return the height consumed.
    Uses a save/restore cursor trick.
    """
    x, y = pdf.get_x(), pdf.get_y()
    start_y = y
    pdf.multi_cell(w, line_h, text, border=1)
    end_y = pdf.get_y()
    h = end_y - start_y
    pdf.set_xy(x + w, y)  # place cursor at right edge of the cell for next column
    return h

def build_pdf_v11(plan: dict) -> bytes:
    rows = plan.get("rows") or []
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 8, "Fitapp Workout Plan", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 6, _safe_text(f"Goal: {plan.get('goal','?')} - Weeks: {plan.get('week_count', 4)}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Table layout
    left_margin = pdf.l_margin
    right_margin = pdf.r_margin
    usable_w = pdf.w - left_margin - right_margin
    day_col_w = 28
    week_col_w = (usable_w - day_col_w) / 4.0  # 4 week columns
    line_h = 5  # line height inside cells

    week_labels = _week_labels(rows)
    grouped = _group(rows)

    # Header row
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.set_x(left_margin)
    pdf.cell(day_col_w, 8, "", border=1)  # corner cell
    for wk in week_labels[:4]:
        pdf.cell(week_col_w, 8, _safe_text(wk), border=1)
    pdf.ln(8)

    # Body rows by day
    pdf.set_font("Helvetica", size=9)
    for dn in DAY_ORDER:
        # Left day label cell
        pdf.set_x(left_margin)
        pdf.cell(day_col_w, line_h, dn, border=1)
        # Measure and render each week column; collect heights to compute row advance
        col_heights: List[float] = []
        start_y = pdf.get_y()
        start_x = pdf.get_x()
        # Render 4 columns, keeping cursor progression across columns via _multi_cell_measure
        for wk in week_labels[:4]:
            dr = grouped.get(wk, {}).get(dn, [])
            # Build text for this cell
            lines = _cell_lines(dr)
            text = "\n".join(_safe_text(s)[:70] for s in lines[:10])  # clamp width and number of lines
            h = _multi_cell_measure(pdf, week_col_w, line_h, text)
            col_heights.append(h if h > 0 else line_h)
        # After last column, the cursor is at the right edge; move to next line by the tallest column height
        row_h = max(col_heights) if col_heights else line_h
        # Set X to left margin and Y to start_y + row_h to start the next day row
        pdf.set_xy(left_margin, start_y + row_h)

    # Footer note (optional)
    pdf.ln(4)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(0, 5, "Notes: Progression guidance is included in each week cell.", new_x="LMARGIN", new_y="NEXT")

    out = pdf.output(dest="S")
    return bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin1")
