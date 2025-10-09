# import streamlit as st
# from fitapp_core.exporters.json_csv import to_json_bytes, to_csv_str
# from fitapp_core.exporters.pdf import build_pdf_v11

# st.title("Export")

# plan = st.session_state.get("plan_v11")
# if not plan:
#     st.info("No plan yet. Generate a plan first.")
#     st.stop()

# rows = plan["rows"]
# basename = f"FitappWorkoutPlan"

# st.download_button("Download JSON", data=to_json_bytes(plan), file_name=f"{basename}.json", mime="application/json")
# st.download_button("Download CSV", data=to_csv_str(rows), file_name=f"{basename}.csv", mime="text/csv")
# st.download_button("Download PDF", data=build_pdf_v11(plan), file_name=f"{basename}.pdf", mime="application/pdf")



# apps/web/pages/3_Export.py
from __future__ import annotations

import streamlit as st
from fitapp_core.exporters.json_csv import (
    to_json_bytes,
    to_csv_str,
    to_csv_str_v11,
    to_csv_str_simple_v11,
)
from fitapp_core.exporters.pdf import build_pdf_v11

st.title("Export")

plan = st.session_state.get("plan_v11")
if not plan:
    st.info("No plan yet. Generate a plan first.")
    st.stop()

rows = plan.get("rows") or []
basename = "FitappWorkoutPlan"

st.download_button("Download JSON", data=to_json_bytes(plan), file_name=f"{basename}.json", mime="application/json")
st.download_button("Download CSV (full)", data=to_csv_str_v11(rows), file_name=f"{basename}.csv", mime="text/csv")
st.download_button("Download CSV (simple)", data=to_csv_str_simple_v11(rows), file_name=f"{basename}_simple.csv", mime="text/csv")
st.download_button("Download PDF", data=build_pdf_v11(plan), file_name=f"{basename}.pdf", mime="application/pdf")
