import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
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
# SESSION STATE
# =========================================================

if "pantry_items" not in st.session_state:
    st.session_state.pantry_items = []


# =========================================================
# FOOD NORMALISATION
# =========================================================

FOOD_ALIASES = {
    "milk": ["milk", "fresh milk"],
    "egg": ["egg", "eggs"],
    "bread": ["bread", "toast"],
    "cheese": ["cheese"],
    "chicken": ["chicken", "chicken breast"],
    "rice": ["rice"],
    "carrot": ["carrot", "carrots"],
    "tomato": ["tomato", "tomatoes"],
    "potato": ["potato", "potatoes"],
    "onion": ["onion", "onions"],
    "pasta": ["pasta", "spaghetti"],
    "tuna": ["tuna", "canned tuna"],
    "lettuce": ["lettuce"],
    "banana": ["banana", "bananas"],
    "apple": ["apple", "apples"],
    "yogurt": ["yogurt", "yoghurt"],
    "butter": ["butter"],
    "flour": ["flour"],
    "noodle": ["noodle", "noodles"],
    "sausage": ["sausage", "sausages"],
    "mushroom": ["mushroom", "mushrooms"],
    "cucumber": ["cucumber", "cucumbers"],
    "beef": ["beef"],
    "fish": ["fish"],
    "spinach": ["spinach"]
}


def normalize_food(food_name):

    food_name = str(food_name).lower().strip()

    for canonical, variations in FOOD_ALIASES.items():

        for variation in variations:

            if variation in food_name:
                return canonical

    return food_name


# =========================================================
# RECIPES
# =========================================================

RECIPES = [
    {
        "name": "Cheese Omelette",
        "icon": "🍳",
        "ingredients": ["egg", "cheese", "milk"],
        "category": "Breakfast"
    },
    {
        "name": "Egg Sandwich",
        "icon": "🥪",
        "ingredients": ["bread", "egg", "cheese"],
        "category": "Breakfast"
    },
    {
        "name": "Chicken Fried Rice",
        "icon": "🍚",
        "ingredients": [
            "chicken",
            "rice",
            "egg",
            "carrot",
            "onion"
        ],
        "category": "Main Meal"
    },
    {
        "name": "Tomato Pasta",
        "icon": "🍝",
        "ingredients": [
            "pasta",
            "tomato",
            "onion",
            "cheese"
        ],
        "category": "Main Meal"
    },
    {
        "name": "Tuna Sandwich",
        "icon": "🥪",
        "ingredients": [
            "bread",
            "tuna",
            "lettuce",
            "tomato"
        ],
        "category": "Light Meal"
    },
    {
        "name": "Chicken Sandwich",
        "icon": "🥪",
        "ingredients": [
            "bread",
            "chicken",
            "lettuce",
            "tomato"
        ],
        "category": "Light Meal"
    },
    {
        "name": "Vegetable Fried Rice",
        "icon": "🍚",
        "ingredients": [
            "rice",
            "egg",
            "carrot",
            "onion"
        ],
        "category": "Main Meal"
    },
    {
        "name": "Simple Salad",
        "icon": "🥗",
        "ingredients": [
            "lettuce",
            "tomato",
            "cucumber"
        ],
        "category": "Healthy"
    },
    {
        "name": "Chicken Salad",
        "icon": "🥗",
        "ingredients": [
            "chicken",
            "lettuce",
            "tomato",
            "cucumber"
        ],
        "category": "Healthy"
    },
    {
        "name": "Mashed Potato",
        "icon": "🥔",
        "ingredients": [
            "potato",
            "milk",
            "butter"
        ],
        "category": "Side Dish"
    },
    {
        "name": "Mushroom Omelette",
        "icon": "🍳",
        "ingredients": [
            "egg",
            "mushroom",
            "cheese"
        ],
        "category": "Breakfast"
    },
    {
        "name": "Chicken Noodles",
        "icon": "🍜",
        "ingredients": [
            "noodle",
            "chicken",
            "carrot",
            "onion"
        ],
        "category": "Main Meal"
    },
    {
        "name": "Sausage Egg Breakfast",
        "icon": "🍳",
        "ingredients": [
            "sausage",
            "egg",
            "bread"
        ],
        "category": "Breakfast"
    },
    {
        "name": "Banana Yogurt Bowl",
        "icon": "🥣",
        "ingredients": [
            "banana",
            "yogurt"
        ],
        "category": "Healthy"
    },
    {
        "name": "Apple Yogurt Bowl",
        "icon": "🥣",
        "ingredients": [
            "apple",
            "yogurt"
        ],
        "category": "Healthy"
    },
    {
        "name": "Cheesy Tomato Toast",
        "icon": "🍞",
        "ingredients": [
            "bread",
            "tomato",
            "cheese"
        ],
        "category": "Light Meal"
    }
]


# =========================================================
# EXPIRY FUNCTIONS
# =========================================================

def convert_date(value):

    if isinstance(value, str):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    return value


def calculate_expiry(expiry_date):

    expiry_date = convert_date(expiry_date)

    days_left = (
        expiry_date - date.today()
    ).days

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

    if days_left < 0:

        amount = abs(days_left)

        if amount == 1:
            return "Expired 1 day ago"

        return f"Expired {amount} days ago"

    if days_left == 0:
        return "Expires today"

    if days_left == 1:
        return "Expires tomorrow"

    return f"Expires in {days_left} days"


# =========================================================
# PANTRY FUNCTIONS
# =========================================================

def create_dataframe():

    if not st.session_state.pantry_items:
        return pd.DataFrame()

    records = []

    for item in st.session_state.pantry_items:

        days_left, expiry_status, priority = (
            calculate_expiry(
                item["expiry_date"]
            )
        )

        records.append(
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
                "Cost (RM)": float(
                    item["cost"]
                ),
                "Storage": item["storage"],
                "Item Status": item[
                    "item_status"
                ]
            }
        )

    return pd.DataFrame(records)


def mark_item(item_id, new_status):

    for item in st.session_state.pantry_items:

        if item["id"] == item_id:

            item["item_status"] = new_status

            item["status_date"] = str(
                date.today()
            )

            break


def delete_item(item_id):

    st.session_state.pantry_items = [
        item
        for item
        in st.session_state.pantry_items
        if item["id"] != item_id
    ]


def raw_backup_dataframe():

    if not st.session_state.pantry_items:
        return pd.DataFrame()

    return pd.DataFrame(
        st.session_state.pantry_items
    )


# =========================================================
# SAMPLE DATA
# =========================================================

def load_sample_data():

    today = date.today()

    samples = [
        {
            "item_name": "Fresh Milk",
            "category": "Dairy",
            "quantity": 1,
            "unit": "Bottle",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=2)
            ),
            "cost": 7.50,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Chicken Breast",
            "category": "Meat",
            "quantity": 1,
            "unit": "Pack",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=4)
            ),
            "cost": 12.00,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Eggs",
            "category": "Dairy",
            "quantity": 10,
            "unit": "Piece",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=7)
            ),
            "cost": 8.50,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Bread",
            "category": "Bakery",
            "quantity": 1,
            "unit": "Pack",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=3)
            ),
            "cost": 4.50,
            "storage": "Pantry"
        },
        {
            "item_name": "Cheese",
            "category": "Dairy",
            "quantity": 1,
            "unit": "Pack",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=8)
            ),
            "cost": 9.50,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Tomatoes",
            "category": "Vegetables",
            "quantity": 4,
            "unit": "Piece",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=5)
            ),
            "cost": 5.00,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Rice",
            "category": "Dry Food",
            "quantity": 2,
            "unit": "kg",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=120)
            ),
            "cost": 18.00,
            "storage": "Pantry"
        },
        {
            "item_name": "Carrots",
            "category": "Vegetables",
            "quantity": 3,
            "unit": "Piece",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=9)
            ),
            "cost": 4.00,
            "storage": "Refrigerator"
        },
        {
            "item_name": "Onions",
            "category": "Vegetables",
            "quantity": 4,
            "unit": "Piece",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=20)
            ),
            "cost": 4.50,
            "storage": "Pantry"
        },
        {
            "item_name": "Pasta",
            "category": "Dry Food",
            "quantity": 2,
            "unit": "Pack",
            "purchase_date": str(today),
            "expiry_date": str(
                today + timedelta(days=90)
            ),
            "cost": 10.00,
            "storage": "Pantry"
        }
    ]

    for sample in samples:

        sample["id"] = str(
            uuid.uuid4()
        )

        sample["item_status"] = (
            "Available"
        )

        sample["status_date"] = ""

        st.session_state.pantry_items.append(
            sample
        )


# =========================================================
# RECIPE MATCHING
# =========================================================

def calculate_recipe_matches():

    available_items = [
        item
        for item
        in st.session_state.pantry_items
        if item["item_status"]
        == "Available"
    ]

    pantry_keys = {}

    for item in available_items:

        key = normalize_food(
            item["item_name"]
        )

        if key not in pantry_keys:
            pantry_keys[key] = []

        pantry_keys[key].append(
            item
        )

    results = []

    for recipe in RECIPES:

        required = recipe[
            "ingredients"
        ]

        matched = [
            ingredient
            for ingredient in required
            if ingredient in pantry_keys
        ]

        missing = [
            ingredient
            for ingredient in required
            if ingredient not in pantry_keys
        ]

        match_percentage = (
            len(matched)
            /
            len(required)
            *
            100
        )

        expiring_used = []

        expiry_bonus = 0

        for ingredient in matched:

            for pantry_item in pantry_keys[
                ingredient
            ]:

                days_left, _, _ = (
                    calculate_expiry(
                        pantry_item[
                            "expiry_date"
                        ]
                    )
                )

                if 0 <= days_left <= 2:

                    expiry_bonus += 8

                    expiring_used.append(
                        (
                            pantry_item[
                                "item_name"
                            ],
                            days_left
                        )
                    )

                    break

                elif 3 <= days_left <= 7:

                    expiry_bonus += 5

                    expiring_used.append(
                        (
                            pantry_item[
                                "item_name"
                            ],
                            days_left
                        )
                    )

                    break

        expiry_bonus = min(
            expiry_bonus,
            20
        )

        recommendation_score = (
            match_percentage * 0.8
            +
            expiry_bonus
        )

        recommendation_score = min(
            recommendation_score,
            100
        )

        results.append(
            {
                "name": recipe["name"],
                "icon": recipe["icon"],
                "category": recipe[
                    "category"
                ],
                "required": required,
                "matched": matched,
                "missing": missing,
                "match_percentage":
                    match_percentage,
                "expiry_bonus":
                    expiry_bonus,
                "score":
                    recommendation_score,
                "expiring_used":
                    expiring_used
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


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

st.sidebar.write(
    "**SmartPantry**"
)

st.sidebar.caption(
    "Track food expiry, reduce waste "
    "and discover meals using the "
    "ingredients you already have."
)

if not st.session_state.pantry_items:

    if st.sidebar.button(
        "🧪 Load Demo Data",
        use_container_width=True
    ):

        load_sample_data()

        st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.header("🏠 Pantry Dashboard")

    df = create_dataframe()

    if df.empty:

        st.info(
            "Your pantry is currently empty."
        )

        st.write(
            "Go to **Add Food** to create "
            "your first pantry record, or "
            "use **Load Demo Data** in the sidebar."
        )

    else:

        active_df = df[
            df["Item Status"]
            == "Available"
        ]

        total_available = len(
            active_df
        )

        expiring_soon = len(
            active_df[
                (
                    active_df[
                        "Days Left"
                    ] >= 0
                )
                &
                (
                    active_df[
                        "Days Left"
                    ] <= 7
                )
            ]
        )

        expired = len(
            active_df[
                active_df[
                    "Days Left"
                ] < 0
            ]
        )

        consumed = len(
            df[
                df["Item Status"]
                == "Consumed"
            ]
        )

        wasted = len(
            df[
                df["Item Status"]
                == "Wasted"
            ]
        )

        waste_cost = df.loc[
            df["Item Status"]
            == "Wasted",
            "Cost (RM)"
        ].sum()

        pantry_value = active_df[
            "Cost (RM)"
        ].sum()

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------

        row1 = st.columns(4)

        row1[0].metric(
            "🥫 Available",
            total_available
        )

        row1[1].metric(
            "⚠️ Expiring Soon",
            expiring_soon
        )

        row1[2].metric(
            "⌛ Expired",
            expired
        )

        row1[3].metric(
            "💰 Pantry Value",
            f"RM {pantry_value:.2f}"
        )

        row2 = st.columns(3)

        row2[0].metric(
            "✅ Consumed",
            consumed
        )

        row2[1].metric(
            "🗑️ Wasted",
            wasted
        )

        row2[2].metric(
            "💸 Waste Cost",
            f"RM {waste_cost:.2f}"
        )

        st.divider()

        # -------------------------------------------------
        # FOOD PRIORITY
        # -------------------------------------------------

        st.subheader(
            "⚠️ Use These Foods First"
        )

        priority_df = active_df[
            active_df[
                "Days Left"
            ] <= 14
        ].copy()

        priority_df = (
            priority_df.sort_values(
                by=[
                    "Priority Score",
                    "Days Left"
                ],
                ascending=[
                    False,
                    True
                ]
            )
        )

        if priority_df.empty:

            st.success(
                "No food currently needs "
                "urgent attention."
            )

        else:

            for _, row in (
                priority_df
                .head(5)
                .iterrows()
            ):

                with st.container(
                    border=True
                ):

                    c1, c2, c3 = (
                        st.columns(
                            [3, 2, 1]
                        )
                    )

                    with c1:

                        st.subheader(
                            row["Food"]
                        )

                        st.write(
                            row[
                                "Expiry Status"
                            ]
                        )

                    with c2:

                        st.write(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )

                        st.caption(
                            f"{row['Quantity']} "
                            f"{row['Unit']} • "
                            f"{row['Storage']}"
                        )

                    with c3:

                        st.metric(
                            "Priority",
                            row[
                                "Priority Score"
                            ]
                        )

        # -------------------------------------------------
        # CATEGORY CHART
        # -------------------------------------------------

        if not active_df.empty:

            st.divider()

            st.subheader(
                "📦 Current Pantry Composition"
            )

            category_counts = (
                active_df
                .groupby("Category")
                .size()
                .reset_index(
                    name="Items"
                )
            )

            fig = px.bar(
                category_counts,
                x="Category",
                y="Items",
                title=(
                    "Available Food "
                    "by Category"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# =========================================================
# ADD FOOD
# =========================================================

elif page == "➕ Add Food":

    st.header("➕ Add Food")

    st.write(
        "Add a food item and SmartPantry "
        "will automatically monitor its "
        "expiry priority."
    )

    with st.form(
        "food_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            item_name = st.text_input(
                "Food Name *",
                placeholder=(
                    "Example: Fresh Milk"
                )
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

            purchase_date = (
                st.date_input(
                    "Purchase Date *",
                    value=date.today()
                )
            )

            expiry_date = (
                st.date_input(
                    "Expiry Date *",
                    value=(
                        date.today()
                        +
                        timedelta(days=7)
                    )
                )
            )

            cost = st.number_input(
                "Total Cost (RM)",
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

        submitted = (
            st.form_submit_button(
                "➕ Add to Pantry",
                use_container_width=True
            )
        )

        if submitted:

            if not item_name.strip():

                st.error(
                    "Please enter a food name."
                )

            elif (
                expiry_date
                <
                purchase_date
            ):

                st.error(
                    "Expiry date cannot be "
                    "earlier than the "
                    "purchase date."
                )

            else:

                new_item = {
                    "id": str(
                        uuid.uuid4()
                    ),
                    "item_name":
                        item_name.strip(),
                    "category":
                        category,
                    "quantity":
                        int(quantity),
                    "unit":
                        unit,
                    "purchase_date":
                        str(purchase_date),
                    "expiry_date":
                        str(expiry_date),
                    "cost":
                        float(cost),
                    "storage":
                        storage,
                    "item_status":
                        "Available",
                    "status_date":
                        ""
                }

                st.session_state[
                    "pantry_items"
                ].append(
                    new_item
                )

                days_left, status, _ = (
                    calculate_expiry(
                        expiry_date
                    )
                )

                st.success(
                    f"✅ {item_name} "
                    "added successfully!"
                )

                st.info(
                    f"{status} — "
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
            "Your pantry is empty."
        )

    else:

        # -------------------------------------------------
        # SEARCH AND FILTER
        # -------------------------------------------------

        search = st.text_input(
            "🔍 Search Food",
            placeholder=(
                "Search by food name..."
            )
        )

        f1, f2, f3 = st.columns(3)

        category_filter = (
            f1.selectbox(
                "Category",
                ["All"]
                +
                sorted(
                    df[
                        "Category"
                    ]
                    .unique()
                    .tolist()
                )
            )
        )

        storage_filter = (
            f2.selectbox(
                "Storage",
                ["All"]
                +
                sorted(
                    df[
                        "Storage"
                    ]
                    .unique()
                    .tolist()
                )
            )
        )

        status_filter = (
            f3.selectbox(
                "Item Status",
                [
                    "All",
                    "Available",
                    "Consumed",
                    "Wasted"
                ]
            )
        )

        filtered_df = df.copy()

        if search:

            filtered_df = (
                filtered_df[
                    filtered_df[
                        "Food"
                    ]
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]
            )

        if category_filter != "All":

            filtered_df = (
                filtered_df[
                    filtered_df[
                        "Category"
                    ]
                    ==
                    category_filter
                ]
            )

        if storage_filter != "All":

            filtered_df = (
                filtered_df[
                    filtered_df[
                        "Storage"
                    ]
                    ==
                    storage_filter
                ]
            )

        if status_filter != "All":

            filtered_df = (
                filtered_df[
                    filtered_df[
                        "Item Status"
                    ]
                    ==
                    status_filter
                ]
            )

        filtered_df = (
            filtered_df
            .sort_values(
                "Days Left",
                ascending=True
            )
        )

        st.subheader(
            f"Food Records "
            f"({len(filtered_df)})"
        )

        columns = [
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
            filtered_df[columns],
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # MANAGE FOOD
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "Manage Pantry Items"
        )

        available_items = [
            item
            for item
            in st.session_state[
                "pantry_items"
            ]
            if item[
                "item_status"
            ] == "Available"
        ]

        if available_items:

            options = {
                (
                    f"{item['item_name']} "
                    f"— {item['expiry_date']}"
                ):
                item["id"]
                for item
                in available_items
            }

            selected_label = (
                st.selectbox(
                    "Select Food Item",
                    list(
                        options.keys()
                    )
                )
            )

            selected_id = (
                options[
                    selected_label
                ]
            )

            b1, b2, b3 = (
                st.columns(3)
            )

            if b1.button(
                "✅ Consumed",
                use_container_width=True
            ):

                mark_item(
                    selected_id,
                    "Consumed"
                )

                st.rerun()

            if b2.button(
                "🗑️ Wasted",
                use_container_width=True
            ):

                mark_item(
                    selected_id,
                    "Wasted"
                )

                st.rerun()

            if b3.button(
                "❌ Delete",
                use_container_width=True
            ):

                delete_item(
                    selected_id
                )

                st.rerun()

        else:

            st.info(
                "There are no available "
                "items to manage."
            )

        # -------------------------------------------------
        # BACKUP
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "💾 Pantry Backup"
        )

        st.caption(
            "Download a backup so you can "
            "restore your pantry if the "
            "online application restarts."
        )

        backup_df = (
            raw_backup_dataframe()
        )

        csv_data = (
            backup_df.to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            "⬇️ Download Pantry Backup",
            data=csv_data,
            file_name=(
                "smartpantry_backup.csv"
            ),
            mime="text/csv"
        )

        uploaded_file = (
            st.file_uploader(
                "Restore Pantry Backup",
                type=["csv"]
            )
        )

        if uploaded_file is not None:

            try:

                restored = pd.read_csv(
                    uploaded_file
                )

                required_columns = {
                    "id",
                    "item_name",
                    "category",
                    "quantity",
                    "unit",
                    "purchase_date",
                    "expiry_date",
                    "cost",
                    "storage",
                    "item_status"
                }

                if not (
                    required_columns
                    .issubset(
                        restored.columns
                    )
                ):

                    st.error(
                        "This does not appear "
                        "to be a valid "
                        "SmartPantry backup."
                    )

                else:

                    if st.button(
                        "♻️ Restore Backup"
                    ):

                        records = (
                            restored
                            .fillna("")
                            .to_dict(
                                orient="records"
                            )
                        )

                        for record in records:

                            record[
                                "quantity"
                            ] = int(
                                record[
                                    "quantity"
                                ]
                            )

                            record[
                                "cost"
                            ] = float(
                                record[
                                    "cost"
                                ]
                            )

                            if (
                                "status_date"
                                not in record
                            ):

                                record[
                                    "status_date"
                                ] = ""

                        st.session_state[
                            "pantry_items"
                        ] = records

                        st.success(
                            "Backup restored."
                        )

                        st.rerun()

            except Exception as e:

                st.error(
                    "Unable to restore "
                    "the backup."
                )

                st.caption(
                    str(e)
                )


# =========================================================
# MEAL SUGGESTIONS
# =========================================================

elif page == "🍳 Meal Suggestions":

    st.header(
        "🍳 Smart Meal Suggestions"
    )

    st.write(
        "SmartPantry recommends meals "
        "based on the ingredients you "
        "already have and gives extra "
        "priority to food that should "
        "be consumed soon."
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Add food to your pantry "
            "before generating meal "
            "suggestions."
        )

    else:

        available_df = df[
            df["Item Status"]
            == "Available"
        ]

        if available_df.empty:

            st.warning(
                "There are currently no "
                "available ingredients."
            )

        else:

            st.subheader(
                "Available Ingredients"
            )

            ingredient_text = ", ".join(
                available_df[
                    "Food"
                ].tolist()
            )

            st.write(
                ingredient_text
            )

            st.divider()

            recipe_results = (
                calculate_recipe_matches()
            )

            minimum_match = (
                st.slider(
                    "Minimum Ingredient Match",
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=10
                )
            )

            filtered_recipes = [
                recipe
                for recipe
                in recipe_results
                if recipe[
                    "match_percentage"
                ] >= minimum_match
            ]

            if not filtered_recipes:

                st.warning(
                    "No recipes match the "
                    "selected requirement."
                )

            else:

                st.subheader(
                    "Recommended Meals"
                )

                for number, recipe in (
                    enumerate(
                        filtered_recipes[
                            :8
                        ],
                        start=1
                    )
                ):

                    with st.container(
                        border=True
                    ):

                        title_col, score_col = (
                            st.columns(
                                [4, 1]
                            )
                        )

                        with title_col:

                            st.subheader(
                                f"{number}. "
                                f"{recipe['icon']} "
                                f"{recipe['name']}"
                            )

                            st.caption(
                                recipe[
                                    "category"
                                ]
                            )

                        with score_col:

                            st.metric(
                                "Recommendation",
                                f"{recipe['score']:.0f}"
                            )

                        match_percentage = (
                            recipe[
                                "match_percentage"
                            ]
                        )

                        st.write(
                            "**Ingredient Match:** "
                            f"{match_percentage:.0f}%"
                        )

                        st.progress(
                            min(
                                match_percentage
                                / 100,
                                1.0
                            )
                        )

                        if recipe["matched"]:

                            matched_names = [
                                item.title()
                                for item
                                in recipe[
                                    "matched"
                                ]
                            ]

                            st.write(
                                "✅ **Available:** "
                                +
                                ", ".join(
                                    matched_names
                                )
                            )

                        if recipe["missing"]:

                            missing_names = [
                                item.title()
                                for item
                                in recipe[
                                    "missing"
                                ]
                            ]

                            st.write(
                                "🛒 **Missing:** "
                                +
                                ", ".join(
                                    missing_names
                                )
                            )

                        if (
                            recipe[
                                "expiring_used"
                            ]
                        ):

                            st.write(
                                "⚠️ **Uses food "
                                "expiring soon:**"
                            )

                            for (
                                food_name,
                                days_left
                            ) in recipe[
                                "expiring_used"
                            ]:

                                st.write(
                                    "• "
                                    f"{food_name}: "
                                    f"{expiry_message(days_left)}"
                                )

                            st.success(
                                "SmartPantry has "
                                "ranked this meal "
                                "higher because it "
                                "helps use food "
                                "before expiry."
                            )


# =========================================================
# WASTE ANALYTICS
# =========================================================

elif page == "📊 Waste Analytics":

    st.header(
        "📊 Food Waste Analytics"
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Add pantry records to "
            "view analytics."
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

        available_df = df[
            df["Item Status"]
            == "Available"
        ]

        waste_cost = (
            wasted_df[
                "Cost (RM)"
            ].sum()
        )

        consumed_value = (
            consumed_df[
                "Cost (RM)"
            ].sum()
        )

        finished_items = (
            len(wasted_df)
            +
            len(consumed_df)
        )

        if finished_items > 0:

            waste_rate = (
                len(wasted_df)
                /
                finished_items
                *
                100
            )

        else:

            waste_rate = 0

        # -------------------------------------------------
        # KPI
        # -------------------------------------------------

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "✅ Consumed",
            len(consumed_df)
        )

        c2.metric(
            "🗑️ Wasted",
            len(wasted_df)
        )

        c3.metric(
            "💸 Waste Cost",
            f"RM {waste_cost:.2f}"
        )

        c4.metric(
            "📉 Waste Rate",
            f"{waste_rate:.1f}%"
        )

        st.divider()

        # -------------------------------------------------
        # CONSUMED VS WASTED
        # -------------------------------------------------

        if finished_items > 0:

            outcome_df = pd.DataFrame(
                {
                    "Status": [
                        "Consumed",
                        "Wasted"
                    ],
                    "Items": [
                        len(consumed_df),
                        len(wasted_df)
                    ]
                }
            )

            fig_outcome = px.pie(
                outcome_df,
                names="Status",
                values="Items",
                hole=0.45,
                title=(
                    "Consumed vs Wasted "
                    "Food"
                )
            )

            st.plotly_chart(
                fig_outcome,
                use_container_width=True
            )

        # -------------------------------------------------
        # WASTE BY CATEGORY
        # -------------------------------------------------

        if not wasted_df.empty:

            waste_category = (
                wasted_df
                .groupby("Category")
                .agg(
                    Items_Wasted=(
                        "Food",
                        "count"
                    ),
                    Waste_Cost=(
                        "Cost (RM)",
                        "sum"
                    )
                )
                .reset_index()
            )

            fig_category = px.bar(
                waste_category,
                x="Category",
                y="Items_Wasted",
                title=(
                    "Food Waste "
                    "by Category"
                ),
                labels={
                    "Items_Wasted":
                        "Items Wasted"
                }
            )

            st.plotly_chart(
                fig_category,
                use_container_width=True
            )

            fig_cost = px.bar(
                waste_category,
                x="Category",
                y="Waste_Cost",
                title=(
                    "Estimated Waste Cost "
                    "by Category"
                ),
                labels={
                    "Waste_Cost":
                        "Waste Cost (RM)"
                }
            )

            st.plotly_chart(
                fig_cost,
                use_container_width=True
            )

        else:

            st.success(
                "No food has been marked "
                "as wasted yet."
            )

        # -------------------------------------------------
        # AUTOMATIC INSIGHTS
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "💡 Smart Pantry Insights"
        )

        if wasted_df.empty:

            st.success(
                "No food waste has been "
                "recorded. Continue checking "
                "expiry priorities and meal "
                "recommendations."
            )

        else:

            category_counts = (
                wasted_df[
                    "Category"
                ]
                .value_counts()
            )

            top_category = (
                category_counts
                .idxmax()
            )

            top_count = int(
                category_counts.max()
            )

            st.warning(
                f"**{top_category}** is "
                f"currently your most "
                f"frequently wasted category "
                f"with {top_count} "
                f"wasted item(s)."
            )

            st.write(
                "Consider purchasing smaller "
                "quantities or prioritising "
                "this category in meal "
                "planning."
            )

        if waste_rate <= 10 and (
            finished_items > 0
        ):

            st.success(
                "Your recorded waste rate "
                "is currently low. Keep using "
                "expiry alerts to maintain "
                "this performance."
            )

        elif waste_rate >= 30:

            st.warning(
                "Your waste rate is relatively "
                "high. Check the Dashboard's "
                "'Use These Foods First' "
                "section more frequently."
            )

        if consumed_value > waste_cost:

            st.info(
                f"Recorded consumed food value "
                f"is RM {consumed_value:.2f}, "
                f"compared with RM "
                f"{waste_cost:.2f} recorded "
                f"as waste."
            )
