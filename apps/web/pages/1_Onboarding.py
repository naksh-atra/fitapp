#v1
import streamlit as st
from fitapp_core.models import Inputs, PAL_MAP
from fitapp_core.energy import bmr_mifflin_st_jeor, tdee_from_bmr

st.title("Onboarding")

with st.form("user_inputs"):
    col1, col2 = st.columns(2)
    age = col1.number_input("Age (years)", min_value=16, max_value=80, value=25, step=1)
    sex = col2.selectbox("Sex", ["male", "female"])
    height_cm = col1.number_input("Height (cm)", min_value=120, max_value=220, value=175, step=1)
    weight_kg = col2.number_input("Weight (kg)", min_value=35.0, max_value=200.0, value=70.0, step=0.5)
    pal_code = col1.selectbox("Physical Activity Level", ["sedentary", "active", "vigorous"])
    goal = col2.selectbox("Goal", ["hypertrophy", "strength", "fat_loss", "endurance"])
    # notes = st.text_area("Notes (optional)", placeholder="Injuries, equipment limits, preferences")
    submitted = st.form_submit_button("Compute & Save")

if submitted:
    inputs = Inputs(
        age=int(age), sex=sex, height_cm=int(height_cm), weight_kg=float(weight_kg),
        pal_code=pal_code, goal=goal or None
    )
    pal_value = PAL_MAP[pal_code]
    bmr = bmr_mifflin_st_jeor(inputs.sex, inputs.weight_kg, inputs.height_cm, inputs.age)
    tdee = tdee_from_bmr(bmr, pal_value)
    st.session_state["inputs_v1"] = inputs
    st.session_state["calc_v1"] = {"pal_value": pal_value, "bmr": bmr, "tdee": tdee}
    st.success(f"BMR={bmr} kcal/day, TDEE≈{tdee} kcal/day (PAL={pal_value})")
