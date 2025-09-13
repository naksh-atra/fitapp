import streamlit as st

st.title("hello, streamlit")
st.write("simple web app")

name=st.text_input("enter your name: ")
if name:
    st.success(f"hello {name}")