import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide"
)

st.title("🥕 SmartPantry")
st.caption("Food Expiry & Waste Reduction Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Food",
        "🥫 My Pantry",
        "🍳 Meal Suggestions",
        "📊 Waste Analytics"
    ]
)

if page == "🏠 Dashboard":

    st.header("Dashboard")

    st.write(
        "Welcome to SmartPantry. Monitor your food, "
        "expiry dates and household food waste."
    )


elif page == "➕ Add Food":

    st.header("➕ Add Food")

    with st.form("food_form"):

        item_name = st.text_input("Food Name")

        category = st.selectbox(
            "Category",
            [
                "Dairy",
                "Meat",
                "Vegetables",
                "Fruits",
                "Bakery",
                "Frozen Food",
                "Beverages",
                "Snacks",
                "Canned Food",
                "Dry Food",
                "Others"
            ]
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1
        )

        unit = st.selectbox(
            "Unit",
            [
                "Piece",
                "Pack",
                "Bottle",
                "Can",
                "Box",
                "kg",
                "g",
                "L"
            ]
        )

        purchase_date = st.date_input(
            "Purchase Date",
            value=date.today()
        )

        expiry_date = st.date_input(
            "Expiry Date"
        )

        cost = st.number_input(
            "Cost (RM)",
            min_value=0.0,
            step=0.50
        )

        storage = st.selectbox(
            "Storage Location",
            [
                "Refrigerator",
                "Freezer",
                "Pantry",
                "Kitchen Cabinet",
                "Others"
            ]
        )

        submitted = st.form_submit_button(
            "Add to Pantry"
        )

        if submitted:

            if not item_name:
                st.error("Please enter the food name.")

            elif expiry_date < purchase_date:
                st.error(
                    "Expiry date cannot be before purchase date."
                )

            else:
                st.success(
                    f"{item_name} added successfully!"
                )


elif page == "🥫 My Pantry":

    st.header("🥫 My Pantry")

    st.info(
        "Your saved pantry items will appear here."
    )


elif page == "🍳 Meal Suggestions":

    st.header("🍳 Meal Suggestions")

    st.info(
        "Meal recommendations will be added here."
    )


elif page == "📊 Waste Analytics":

    st.header("📊 Waste Analytics")

    st.info(
        "Food waste statistics will appear here."
    )
