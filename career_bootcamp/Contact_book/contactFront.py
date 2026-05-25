import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title(" Contact Book")

tab1, tab2, tab3 = st.tabs([" Add Contact", " View Contacts", " Search"])


with tab1:
    st.subheader("Add New Contact")

    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")

    if st.button("Add Contact", type="primary"):
        if name and email and phone:
            payload = {"name": name, "email": email, "phone": phone}
            response = requests.post(f"{API_URL}/contacts", json=payload)


            if response.status_code == 200:
                st.success(f"Contact '{name}' added successfully!")
            else:
                st.error(f" Failed: {response.json()['detail']}")
        else:
            st.warning("Please fill in all fields!")

with tab2:
    st.subheader("All Contacts")

    if st.button("Refresh"):
        st.rerun()

    response = requests.get(f"{API_URL}/contacts")

    if response.status_code == 200:
        contacts = response.json()

        if not contacts:
            st.info("No contacts found. Add some!")
        else:
            for contact in contacts:
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(" **Name:**", contact["name"])
                    with col2:
                        st.write(" **Email:**", contact["email"])
                        st.write(" **Phone:**", contact["phone"])
                    with col3:
                        st.write(" **Added:**", contact["created_at"])

with tab3:
    st.subheader("Search Contact")

    search_text = st.text_input("Enter contact name:")

    if st.button("Search"):
        if search_text:

            response = requests.get(f"{API_URL}/contacts/{search_text}")

            if response.status_code == 200:
                contact = response.json()
                with st.container(border=True):
                    st.write(" **Name:**", contact["name"])
                    st.write(" **Email:**", contact["email"])
                    st.write(" **Phone:**", contact["phone"])
                    st.write(" **Added:**", contact["created_at"])
            else:
                st.error(" Contact not found!")
        else:
            st.warning("Please enter a name to search.")