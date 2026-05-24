import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Finance Bootcamp")

# Title
st.title(" Finance Bootcamp Dashboard")

# Simple text input
name = st.text_input("Enter your name:")

# Button
if st.button("Greet Me!"):
    if name:
        # Call FastAPI backend
        response = requests.get(f"http://127.0.0.1:8000/greet/{name}")
        data = response.json()

        # Display result
        st.success(data["greeting"])
    else:
        st.warning("Please enter your name!")

# Sidebar info
st.sidebar.info("Day 1: FastAPI + Streamlit Basics")