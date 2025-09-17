#v1


import streamlit as st
import pandas as pd
from fitapp_core.plan_v1 import generate_plan_v1

st.title("Plan")

if "inputs_v1" not in st.session_state:
    st.info("No inputs yet. Go to Onboarding to enter details.")
    st.stop()

@st.cache_data(show_spinner=True)
def cached_generate_plan(inputs_dict, tweak_note):
    plan = generate_plan_v1(**inputs_dict, tweak_note=tweak_note)
    return plan.model_dump()

tweak = st.text_input("Suggest a tweak (optional)", placeholder="e.g., swap squats for leg press")
plan_dict = cached_generate_plan({"inputs": st.session_state["inputs_v1"]}, tweak)
st.session_state["plan_v1"] = plan_dict

df = pd.DataFrame(plan_dict["rows"])
st.subheader("Routine")
st.dataframe(df, width='stretch')
st.caption(f"Goal: {plan_dict['goal']} • PAL={plan_dict['pal_value']} • BMR={plan_dict['bmr']} • TDEE≈{plan_dict['tdee']}")
