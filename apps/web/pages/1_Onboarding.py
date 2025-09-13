import streamlit as st
from fitapp_core.generator import generate_plan

st.title("Onboarding")

col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=16, max_value=99, value=25, step=1)
    experience = st.selectbox("Experience", ["Beginner", "Intermediate", "Advanced"])
with col2:
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=230, value=175, step=1)
    weight_kg = st.number_input("Weight (kg)", min_value=35, max_value=200, value=70, step=1)
    days_per_week = st.slider("Days per week", min_value=2, max_value=6, value=4)

equipment = st.multiselect("Equipment", ["Bodyweight", "Dumbbells", "Barbell", "Machines", "Bands"], default=["Bodyweight", "Dumbbells"])
goal = st.selectbox("Goal", ["Hypertrophy", "Strength", "Fat loss", "Endurance"])

if st.button("Generate plan"):
    profile = {
        "gender": gender,
        "age": age,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "experience": experience,
        "equipment": equipment,
        "days_per_week": days_per_week,
        "goal": goal,
    }
    # plan = generate_plan(profile)
    # st.success("Plan generated!")
    # st.subheader("Your 7‑day plan")
    # st.json(plan)
    st.session_state["profile"] = profile
    st.session_state["plan"] = generate_plan(profile)
    st.success("Plan generated and saved in session!")