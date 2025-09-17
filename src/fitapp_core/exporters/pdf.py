#v1

from fpdf import FPDF
from typing import Dict, List

def build_pdf(plan: Dict) -> bytes:
    rows: List[Dict] = plan["rows"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "Fitapp Workout Plan", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Goal: {plan['goal']} | PAL={plan['pal_value']} | BMR={plan['bmr']} | TDEE~{plan['tdee']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=9)
    headers = ["Day","Movement","Sets","Reps","Tempo/Rest","Load","Notes"]
    col_w = [12, 50, 12, 12, 28, 26, 50]
    for h, w in zip(headers, col_w):
        pdf.cell(w, 6, h, border=1)
    pdf.ln()
    for r in rows:
        pdf.cell(col_w[0], 6, str(r["day"]), border=1)
        pdf.cell(col_w[1], 6, (r["movement"] or "")[:30], border=1)
        pdf.cell(col_w[2], 6, str(r["sets"]), border=1)
        pdf.cell(col_w[3], 6, str(r["reps"]), border=1)
        pdf.cell(col_w[4], 6, (r.get("tempo_or_rest") or "")[:14], border=1)
        pdf.cell(col_w[5], 6, (r.get("load_prescription") or "")[:16], border=1)
        pdf.cell(col_w[6], 6, (r.get("notes") or "")[:30], border=1)
        pdf.ln()
    # return pdf.output(dest="S").encode("latin1")
    # return bytes(pdf.output(dest="S"))
    return bytes(pdf.output())
