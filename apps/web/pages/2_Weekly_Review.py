import streamlit as st

# st.title("Weekly Review")
# st.info("Coming soon: log RIR/RPE and readiness, then auto-adjust next week’s plan.")


st.title("Weekly Review")

if st.session_state.get("plan"):
    st.subheader("Current plan (from session)")
    st.json(st.session_state["plan"])
else:
    st.warning("No plan found. Please generate one on the Onboarding page first.")
