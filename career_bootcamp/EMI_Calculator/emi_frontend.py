import time

import streamlit as st
import requests

st.set_page_config(page_title="EMI Calculator")

st.title("EMI Calculator")
st.write("Welcome to the EMI Calculator!")

col1, col2 = st.columns([1, 1])

with col1:

    principal = st.number_input(
        "Loan Amount",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000
    )

    interest_rate = st.slider(
        "Interest Rate (%)",
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    tenure = st.slider(
        "Loan Tenure (Months)",
        min_value=1,
        max_value=360,
        value=12
    )

    calculate_button = st.button(
        "Calculate EMI",
        type="primary"
    )

with col2:

    st.subheader("Results")

    if calculate_button:

        payload = {
            "principal": principal,
            "interest_rate": interest_rate,
            "tenure": tenure
        }

        try:
            with st.spinner("Please wait..."):
                time.sleep(3)

                st.success("Done!")
                response = requests.post(
                    "http://127.0.0.1:8000/cal-emi",
                    json=payload
                )

            if response.status_code == 200:

                data = response.json()

                st.metric(
                    "Monthly EMI",
                    f"Rs {data['emi']:,.2f}"
                )

                st.metric(
                    "Total Payment",
                    f"Rs {data['total_payment']:,.2f}"
                )

                st.metric(
                    "Total Interest",
                    f"Rs {data['total_interest']:,.2f}"
                )
            else:
                st.error("Something went wrong")

        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to API")