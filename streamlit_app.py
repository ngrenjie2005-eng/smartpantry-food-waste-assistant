import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide"
)


# =========================================================
# SESSION DATA
# =========================================================

if "pantry_items" not in st.session_state:
    st.session_state.pantry_items = []


# =========================================================
# FUNCTIONS
# =========================================================

def calculate_expiry(expiry_date):
    """
    Calculate days remaining, expiry status and urgency score.
    """

    if isinstance(expiry_date, str):
        expiry_date = datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        ).date()

    today = date.today()

    days_left = (expiry_date - today).days

    if days_left < 0:
        status = "⚫ Expired"
        priority = 100

    elif days_left <= 2:
        status = "🔴 Urgent"
        priority = 90

    elif days_left <= 7:
        status = "🟠 Expiring Soon"
        priority = 75

    elif days_left <= 14:
        status = "🟡 Use Soon"
        priority = 40

    else:
        status = "🟢 Fresh"
        priority = 20

    return days_left, status, priority


def expiry_message(days_left):
    """
    Create a user-friendly expiry message.
    """

    if days_left < 0:
        days_expired = abs(days_left)

        if days_expired == 1:
            return "Expired 1 day ago"

        return f"Expired {days_expired} days ago"

    elif days_left == 0:
        return "Expires today"

    elif days_left == 1:
        return "Expires tomorrow"

    else:
        return f"Expires in {days_left} days"


def create_dataframe():
    """
    Convert pantry records into a DataFrame.
    """

    if not st.session_state.pantry_items:
        return pd.DataFrame()

    data = []

    for item in st.session_state.pantry_items:

        days_left, expiry_status, priority = calculate_expiry(
            item["expiry_date"]
        )

        data.append(
            {
                "ID": item["id"],
                "Food": item["item_name"],
                "Category": item["category"],
                "Quantity": item["quantity"],
                "Unit": item["unit"],
                "Purchase Date": item["purchase_date"],
                "Expiry Date": item["expiry_date"],
                "Days Left": days_left,
                "Expiry Status": expiry_status,
                "Priority Score": priority,
                "Cost (RM)": item["cost"],
                "Storage": item["storage"],
                "Item Status": item["item_status"]
            }
        )

    return pd.DataFrame(data)


def mark_item(item_id, new_status):
    """
    Change food status to Consumed or Wasted.
    """

    for item in st.session_state.pantry_items:

        if item["id"] == item_id:
            item["item_status"] = new_status
            break


def delete_item(item_id):
    """
    Delete pantry record.
    """

    st.session_state.pantry_items = [
        item
        for item in st.session_state.pantry_items
        if item["id"] != item_id
    ]


# =========================================================
# HEADER
# =========================================================

st.title("🥕 SmartPantry")

st.caption(
    "Food Expiry & Waste Reduction Assistant"
)


# =========================================================
# SIDEBAR
# =========================================================

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

st.sidebar.divider()

st.sidebar.caption(
    "SmartPantry helps reduce household food waste "
    "through expiry monitoring and smarter food usage."
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.header("🏠 Pantry Dashboard")

    df = create_dataframe()

    if df.empty:

        st.info(
            "Your pantry is currently empty. "
            "Go to **Add Food** to add your first item."
        )

    else:

        active_df = df[
            df["Item Status"] == "Available"
        ]

        total_items = len(active_df)

        expiring_soon = len(
            active_df[
                (active_df["Days Left"] >= 0)
                &
                (active_df["Days Left"] <= 7)
            ]
        )

        expired_items = len(
            active_df[
                active_df["Days Left"] < 0
            ]
        )

        consumed_items = len(
            df[
                df["Item Status"] == "Consumed"
            ]
        )

        wasted_items = len(
            df[
                df["Item Status"] == "Wasted"
            ]
        )

        waste_cost = df.loc[
            df["Item Status"] == "Wasted",
            "Cost (RM)"
        ].sum()

        # KPI cards

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🥫 Available Items",
            total_items
        )

        col2.metric(
            "⚠️ Expiring Soon",
            expiring_soon
        )

        col3.metric(
            "⌛ Expired",
            expired_items
        )

        col4, col5, col6 = st.columns(3)

        col4.metric(
            "✅ Consumed",
            consumed_items
        )

        col5.metric(
            "🗑️ Wasted",
            wasted_items
        )

        col6.metric(
            "💸 Waste Cost",
            f"RM {waste_cost:.2f}"
        )

        st.divider()

        # =================================================
        # PRIORITY SECTION
        # =================================================

        st.subheader("⚠️ Use These Foods First")

        priority_df = active_df.copy()

        priority_df = priority_df[
            priority_df["Days Left"] <= 14
        ]

        priority_df = priority_df.sort_values(
            by=[
                "Priority Score",
                "Days Left"
            ],
            ascending=[
                False,
                True
            ]
        )

        if priority_df.empty:

            st.success(
                "No food currently needs urgent attention."
            )

        else:

            for _, row in priority_df.head(5).iterrows():

                message = expiry_message(
                    row["Days Left"]
                )

                with st.container(border=True):

                    col_a, col_b = st.columns(
                        [3, 1]
                    )

                    with col_a:

                        st.subheader(
                            row["Food"]
                        )

                        st.write(
                            f"**{row['Expiry Status']}**"
                        )

                        st.write(message)

                        st.caption(
                            f"{row['Quantity']} "
                            f"{row['Unit']} • "
                            f"{row['Storage']}"
                        )

                    with col_b:

                        st.metric(
                            "Priority",
                            row["Priority Score"]
                        )


# =========================================================
# ADD FOOD PAGE
# =========================================================

elif page == "➕ Add Food":

    st.header("➕ Add Food")

    st.write(
        "Add food items to your pantry and SmartPantry "
        "will automatically monitor their expiry dates."
    )

    with st.form(
        "food_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            item_name = st.text_input(
                "Food Name *",
                placeholder="Example: Fresh Milk"
            )

            category = st.selectbox(
                "Category *",
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
                "Quantity *",
                min_value=1,
                value=1,
                step=1
            )

            unit = st.selectbox(
                "Unit *",
                [
                    "Piece",
                    "Pack",
                    "Bottle",
                    "Can",
                    "Box",
                    "kg",
                    "g",
                    "L",
                    "ml"
                ]
            )

        with col2:

            purchase_date = st.date_input(
                "Purchase Date *",
                value=date.today()
            )

            expiry_date = st.date_input(
                "Expiry Date *",
                value=date.today()
            )

            cost = st.number_input(
                "Cost (RM)",
                min_value=0.0,
                value=0.0,
                step=0.50,
                format="%.2f"
            )

            storage = st.selectbox(
                "Storage Location *",
                [
                    "Refrigerator",
                    "Freezer",
                    "Pantry",
                    "Kitchen Cabinet",
                    "Others"
                ]
            )

        submitted = st.form_submit_button(
            "➕ Add to Pantry",
            use_container_width=True
        )

        if submitted:

            if not item_name.strip():

                st.error(
                    "Please enter the food name."
                )

            elif expiry_date < purchase_date:

                st.error(
                    "Expiry date cannot be earlier "
                    "than the purchase date."
                )

            else:

                new_item = {
                    "id": str(uuid.uuid4()),
                    "item_name": item_name.strip(),
                    "category": category,
                    "quantity": quantity,
                    "unit": unit,
                    "purchase_date": str(
                        purchase_date
                    ),
                    "expiry_date": str(
                        expiry_date
                    ),
                    "cost": float(cost),
                    "storage": storage,
                    "item_status": "Available"
                }

                st.session_state.pantry_items.append(
                    new_item
                )

                days_left, expiry_status, priority = (
                    calculate_expiry(
                        expiry_date
                    )
                )

                st.success(
                    f"✅ {item_name} added to "
                    f"your pantry successfully!"
                )

                st.info(
                    f"{expiry_status} — "
                    f"{expiry_message(days_left)}"
                )


# =========================================================
# MY PANTRY
# =========================================================

elif page == "🥫 My Pantry":

    st.header("🥫 My Pantry")

    df = create_dataframe()

    if df.empty:

        st.info(
            "Your pantry is empty. "
            "Add some food first."
        )

    else:

        # =================================================
        # SEARCH + FILTERS
        # =================================================

        search = st.text_input(
            "🔍 Search Food",
            placeholder="Search by food name..."
        )

        col1, col2, col3 = st.columns(3)

        category_filter = col1.selectbox(
            "Category",
            ["All"]
            + sorted(
                df["Category"]
                .unique()
                .tolist()
            )
        )

        storage_filter = col2.selectbox(
            "Storage",
            ["All"]
            + sorted(
                df["Storage"]
                .unique()
                .tolist()
            )
        )

        status_filter = col3.selectbox(
            "Item Status",
            [
                "All",
                "Available",
                "Consumed",
                "Wasted"
            ]
        )

        filtered_df = df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df["Food"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Category"]
                == category_filter
            ]

        if storage_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Storage"]
                == storage_filter
            ]

        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Item Status"]
                == status_filter
            ]

        filtered_df = filtered_df.sort_values(
            by="Days Left",
            ascending=True
        )

        st.subheader(
            f"Food Records ({len(filtered_df)})"
        )

        display_columns = [
            "Food",
            "Category",
            "Quantity",
            "Unit",
            "Expiry Date",
            "Days Left",
            "Expiry Status",
            "Cost (RM)",
            "Storage",
            "Item Status"
        ]

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # MANAGE ITEMS
        # =================================================

        st.divider()

        st.subheader("Manage Pantry Items")

        available_items = [
            item
            for item in st.session_state.pantry_items
            if item["item_status"] == "Available"
        ]

        if available_items:

            item_options = {
                f"{item['item_name']} "
                f"({item['expiry_date']})":
                item["id"]
                for item in available_items
            }

            selected_label = st.selectbox(
                "Select an available food item",
                list(item_options.keys())
            )

            selected_id = item_options[
                selected_label
            ]

            col1, col2, col3 = st.columns(3)

            if col1.button(
                "✅ Mark as Consumed",
                use_container_width=True
            ):

                mark_item(
                    selected_id,
                    "Consumed"
                )

                st.success(
                    "Item marked as consumed."
                )

                st.rerun()

            if col2.button(
                "🗑️ Mark as Wasted",
                use_container_width=True
            ):

                mark_item(
                    selected_id,
                    "Wasted"
                )

                st.warning(
                    "Item marked as wasted."
                )

                st.rerun()

            if col3.button(
                "❌ Delete Item",
                use_container_width=True
            ):

                delete_item(
                    selected_id
                )

                st.success(
                    "Item deleted."
                )

                st.rerun()

        else:

            st.info(
                "There are no available pantry items "
                "to manage."
            )


# =========================================================
# MEAL SUGGESTIONS
# =========================================================

elif page == "🍳 Meal Suggestions":

    st.header("🍳 Meal Suggestions")

    st.info(
        "The next development stage will recommend "
        "meals based on ingredients currently available "
        "in your pantry."
    )

    df = create_dataframe()

    if not df.empty:

        available_df = df[
            df["Item Status"]
            == "Available"
        ]

        if not available_df.empty:

            st.subheader(
                "Currently Available Ingredients"
            )

            ingredients = (
                available_df["Food"]
                .tolist()
            )

            for ingredient in ingredients:

                st.write(
                    f"• {ingredient}"
                )

        else:

            st.warning(
                "No available ingredients."
            )


# =========================================================
# WASTE ANALYTICS
# =========================================================

elif page == "📊 Waste Analytics":

    st.header("📊 Waste Analytics")

    df = create_dataframe()

    if df.empty:

        st.info(
            "Waste analytics will appear after "
            "you add food records."
        )

    else:

        wasted_df = df[
            df["Item Status"]
            == "Wasted"
        ]

        consumed_df = df[
            df["Item Status"]
            == "Consumed"
        ]

        total_waste_cost = wasted_df[
            "Cost (RM)"
        ].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🗑️ Foods Wasted",
            len(wasted_df)
        )

        col2.metric(
            "✅ Foods Consumed",
            len(consumed_df)
        )

        col3.metric(
            "💸 Waste Cost",
            f"RM {total_waste_cost:.2f}"
        )

        st.divider()

        if wasted_df.empty:

            st.success(
                "No food has been recorded "
                "as wasted yet. Great job!"
            )

        else:

            st.subheader(
                "Waste by Category"
            )

            waste_category = (
                wasted_df
                .groupby("Category")
                .size()
                .reset_index(
                    name="Items Wasted"
                )
            )

            st.bar_chart(
                waste_category,
                x="Category",
                y="Items Wasted"
            )
