# Streamlit app that collects inputs and displays the generated 7‑day plan, aligning with Streamlit’s client‑server model for quick local and deployable UIs


import streamlit as st
from fitapp_core.generator import generate_plan


# Initialize shared state once
if "profile" not in st.session_state:
    st.session_state["profile"] = {}
if "plan" not in st.session_state:
    st.session_state["plan"] = None

st.set_page_config(page_title="Fitapp — Workout Plan Generator", page_icon="💪", layout="centered")

st.title("Fitapp — Workout Plan Generator")
st.write("Use the pages in the sidebar to onboard and review weekly changes.", unsafe_allow_html=False)

if st.button("Quick demo plan"):
    profile = {
        "gender": "Other",
        "age": 25,
        "height_cm": 175,
        "weight_kg": 70,
        "experience": "Beginner",
        "equipment": ["Bodyweight", "Dumbbells"],
        "days_per_week": 4,
        "goal": "Hypertrophy",
    }
    plan = generate_plan(profile)
    st.subheader("Demo 7-day plan (JSON)")
    st.json(plan)
