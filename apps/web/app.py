import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Fitapp — Workout Plan Generator", page_icon="💪", layout="centered")

import os
from pathlib import Path

def _data_status_line() -> str:
    data_dir = Path("./data").resolve()
    idx_dir = data_dir / "index" / "v1"
    proc_dir = data_dir / "processed"
    idx_ok = (idx_dir / "faiss.index").exists() and (idx_dir / "meta.parquet").exists()
    proc_ok = (proc_dir / "chunks.jsonl").exists() or (proc_dir / "docs.jsonl").exists()
    return f"Data: {data_dir} | Index OK: {idx_ok} | Processed OK: {proc_ok}"

# Log once on page load
status = _data_status_line()
print("[Fitapp] Startup:", status)
st.caption(status)

st.title("Fitapp — Workout Plan Generator")
st.write("Use the pages in the sidebar to onboard and review weekly changes.")

st.subheader("Quick Demo")
st.caption("Click to preview how generated workout plans are presented in a clean, tabular layout.")

if st.button("Demo Plan"):
    # Minimal, static demo rows in v1.1 style (no generation, no API calls)
    demo_rows = [
        # Day 1
        {"week_label":"Week 1","day":1,"day_name":"Mon","block":"main","movement":"Barbell Bench Press","sets":3,"reps":8,"tempo_or_rest":"2-0-2","notes":""},
        {"week_label":"Week 1","day":1,"day_name":"Mon","block":"accessory","movement":"Triceps Pushdown","sets":3,"reps":10,"tempo_or_rest":"","notes":""},
        # Day 2
        {"week_label":"Week 1","day":2,"day_name":"Tue","block":"main","movement":"Back Squat","sets":3,"reps":8,"tempo_or_rest":"2-0-2","notes":""},
        {"week_label":"Week 1","day":2,"day_name":"Tue","block":"accessory","movement":"Leg Extension","sets":3,"reps":12,"tempo_or_rest":"","notes":""},
        # Day 3
        {"week_label":"Week 1","day":3,"day_name":"Wed","block":"main","movement":"Overhead Press","sets":3,"reps":8,"tempo_or_rest":"2-0-2","notes":""},
        {"week_label":"Week 1","day":3,"day_name":"Wed","block":"accessory","movement":"Lateral Raise","sets":3,"reps":12,"tempo_or_rest":"","notes":""},
        # Day 4
        {"week_label":"Week 1","day":4,"day_name":"Thu","block":"main","movement":"Romanian Deadlift","sets":3,"reps":8,"tempo_or_rest":"3-0-1","notes":""},
        {"week_label":"Week 1","day":4,"day_name":"Thu","block":"accessory","movement":"Seated Row","sets":3,"reps":10,"tempo_or_rest":"","notes":""},
        # Day 5
        {"week_label":"Week 1","day":5,"day_name":"Fri","block":"main","movement":"Incline Bench Press","sets":3,"reps":8,"tempo_or_rest":"2-0-2","notes":""},
        {"week_label":"Week 1","day":5,"day_name":"Fri","block":"accessory","movement":"Face Pull","sets":3,"reps":15,"tempo_or_rest":"","notes":""},
        # Day 6
        {"week_label":"Week 1","day":6,"day_name":"Sat","block":"prehab","movement":"Copenhagen Plank","sets":2,"reps":12,"tempo_or_rest":"","notes":"Each side"},
        # Day 7
        {"week_label":"Week 1","day":7,"day_name":"Sun","block":"cardio_notes","movement":"Zone 2 Cardio","sets":None,"reps":None,"tempo_or_rest":"20–30 min","notes":"Easy pace"},
    ]

    # Arrange columns similar to PDF tables
    df = pd.DataFrame(demo_rows)[
        ["week_label","day","day_name","block","movement","sets","reps","tempo_or_rest","notes"]
    ]

    st.subheader("Demo Plan (table)")
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("Click “Demo Plan” to preview a typical weekly plan table.")











#streamlit run apps/web/app.py --server.address localhost --server.port 8501