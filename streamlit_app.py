import streamlit as st

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide"
)

st.title("🥕 SmartPantry")

st.subheader("Food Expiry & Waste Reduction Assistant")

st.write(
    "Track your pantry items, monitor expiry dates, "
    "reduce food waste, and discover meals you can make "
    "with ingredients you already have."
)

st.success("SmartPantry is running successfully!")
