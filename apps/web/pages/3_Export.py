#v1

import streamlit as st
from fitapp_core.exporters.json_csv import to_json_bytes, to_csv_str
from fitapp_core.exporters.pdf import build_pdf

st.title("Export")

if "plan_v1" not in st.session_state:
    st.info("No plan yet. Generate a plan first.")
    st.stop()

plan = st.session_state["plan_v1"]
rows = plan["rows"]
basename = f"fitapp_plan_{plan['goal']}_{plan['pal_value']}_{plan['plan_id']}"

st.download_button(
    "Download JSON",
    data=to_json_bytes(plan),
    file_name=f"{basename}.json",
    mime="application/json",
)

st.download_button(
    "Download CSV",
    data=to_csv_str(rows),
    file_name=f"{basename}.csv",
    mime="text/csv",
)

st.download_button(
    "Download PDF",
    data=build_pdf(plan),
    file_name=f"{basename}.pdf",
    mime="application/pdf",
)
