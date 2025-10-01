# #v1
# from fpdf import FPDF
# from typing import Dict, List

# def _safe_text(text: str) -> str:
#     """Replace Unicode chars that crash with Helvetica/core fonts."""
#     return text.replace("•", "-").replace("—", "-").replace("–", "-").replace("×", "x")



# def build_pdf_v11(plan: dict) -> bytes:
#     rows = plan["rows"]
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Helvetica", size=14)
#     pdf.cell(0, 10, "Fitapp Workout Plan", new_x="LMARGIN", new_y="NEXT")
#     pdf.set_font("Helvetica", size=10)
#     goal_line = _safe_text(f"Goal: {plan['goal']} - Weeks: {plan.get('week_count', 4)}")
#     pdf.cell(0, 6, goal_line, new_x="LMARGIN", new_y="NEXT")
#     pdf.ln(2)

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
#                 focus = (r.get("main_focus") or "") + (" - " + r["intensity_cue"] if r.get("intensity_cue") else "")
#                 vol = f"{r['sets']}x{r['reps']}" if r.get("sets") and r.get("reps") else (r.get("duration") or "")
#                 values = [
#                     _safe_text((r["movement"] or "")[:40]),
#                     _safe_text(focus[:38]),
#                     _safe_text(vol[:18]),
#                     _safe_text((r.get("notes") or "")[:44]),
#                 ]
#                 for v, w in zip(values, widths):
#                     pdf.cell(w, 6, v, border=1)
#                 pdf.ln()
#         pdf.ln(2)

#     # Cast buffer to bytes to satisfy Streamlit download_button
#     buf = pdf.output(dest="S")
#     return bytes(buf) if isinstance(buf, (bytearray, bytes)) else buf.encode("latin1")


# v1
from fpdf import FPDF
from typing import Dict, List

def _safe_text(text: str) -> str:
    """Replace Unicode chars that crash with Helvetica/core fonts."""
    return text.replace("•", "-").replace("—", "-").replace("–", "-").replace("×", "x")

def _render_sources(pdf: FPDF, plan: dict) -> None:
    """
    Append a 'Sources' section using the same mapping used in the UI:
    plan["sources"] = [{"n": 1, "doc_id": "...", "chunk_id": "..."}, ...]
    Falls back to plan["retrieved_snippets"] if present to reconstruct minimal mapping.
    """
    sources: List[Dict] = plan.get("sources") or []
    if not sources and plan.get("retrieved_snippets"):
        # Back-compat: reconstruct [n, doc_id, chunk_id] from retrieved_snippets
        sources = [
            {"n": i + 1, "doc_id": s.get("doc_id"), "chunk_id": s.get("id")}
            for i, s in enumerate(plan["retrieved_snippets"])
        ]
    if not sources:
        return

    pdf.ln(3)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 7, "Sources", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=9)
    for s in sources:
        n = s.get("n")
        doc_id = s.get("doc_id", "?")
        chunk_id = s.get("chunk_id", "?")
        line = _safe_text(f"[{n}] doc {doc_id} · chunk {chunk_id}")
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

def build_pdf_v11(plan: dict) -> bytes:
    rows = plan["rows"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "Fitapp Workout Plan", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    goal_line = _safe_text(f"Goal: {plan['goal']} - Weeks: {plan.get('week_count', 4)}")
    pdf.cell(0, 6, goal_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    from itertools import groupby
    key = lambda r: (r.get("week_label","Week 1"), r["day"], r.get("day_name",""))
    for (week, day, day_name), group in groupby(sorted(rows, key=key), key):
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(0, 7, _safe_text(f"{week} - {day_name}"), new_x="LMARGIN", new_y="NEXT")
        section_order = ["main", "accessory", "prehab", "cardio_notes"]
        grp = list(group)
        for section in section_order:
            sect_rows = [r for r in grp if r["block_type"] == section]
            if not sect_rows:
                continue
            pdf.set_font("Helvetica", style="", size=10)
            pdf.cell(0, 6, section.replace("_"," ").title(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=9)
            headers = ["Movement","Focus/Intensity","SetsxReps/Duration","Notes"]
            widths = [58, 50, 38, 44]
            for h, w in zip(headers, widths):
                pdf.cell(w, 6, h, border=1)
            pdf.ln()
            for r in sect_rows:
                focus = (r.get("main_focus") or "") + (" - " + r["intensity_cue"] if r.get("intensity_cue") else "")
                vol = f"{r['sets']}x{r['reps']}" if r.get("sets") and r.get("reps") else (r.get("duration") or "")
                values = [
                    _safe_text((r["movement"] or "")[:40]),
                    _safe_text(focus[:38]),
                    _safe_text(vol[:18]),
                    _safe_text((r.get("notes") or "")[:44]),
                ]
                for v, w in zip(values, widths):
                    pdf.cell(w, 6, v, border=1)
                pdf.ln()
        pdf.ln(2)

    # New: append Sources section using plan["sources"] mapping
    _render_sources(pdf, plan)

    # Cast buffer to bytes to satisfy Streamlit download_button
    buf = pdf.output(dest="S")
    return bytes(buf) if isinstance(buf, (bytearray, bytes)) else buf.encode("latin1")
