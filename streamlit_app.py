import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from datetime import date, datetime, timedelta
import uuid


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide"
)


# =========================================================
# INTERFACE STYLE
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.20);
        padding: 18px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "pantry_items" not in st.session_state:
    st.session_state.pantry_items = []

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


# =========================================================
# CONSTANTS
# =========================================================

CATEGORIES = [
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

UNITS = [
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

STORAGE = [
    "Refrigerator",
    "Freezer",
    "Pantry",
    "Kitchen Cabinet",
    "Others"
]


# =========================================================
# FOOD NAME NORMALISATION
# =========================================================

FOOD_ALIASES = {

    "milk": [
        "milk",
        "fresh milk"
    ],

    "egg": [
        "egg",
        "eggs"
    ],

    "bread": [
        "bread",
        "toast"
    ],

    "cheese": [
        "cheese"
    ],

    "chicken": [
        "chicken",
        "chicken breast"
    ],

    "rice": [
        "rice"
    ],

    "carrot": [
        "carrot",
        "carrots"
    ],

    "tomato": [
        "tomato",
        "tomatoes"
    ],

    "potato": [
        "potato",
        "potatoes"
    ],

    "onion": [
        "onion",
        "onions"
    ],

    "pasta": [
        "pasta",
        "spaghetti"
    ],

    "tuna": [
        "tuna",
        "canned tuna"
    ],

    "lettuce": [
        "lettuce"
    ],

    "banana": [
        "banana",
        "bananas"
    ],

    "apple": [
        "apple",
        "apples"
    ],

    "yogurt": [
        "yogurt",
        "yoghurt"
    ],

    "butter": [
        "butter"
    ],

    "noodle": [
        "noodle",
        "noodles"
    ],

    "sausage": [
        "sausage",
        "sausages"
    ],

    "mushroom": [
        "mushroom",
        "mushrooms"
    ],

    "cucumber": [
        "cucumber",
        "cucumbers"
    ]
}


# =========================================================
# RULE-BASED RECIPES
# =========================================================

RECIPES = [

    {
        "name": "Cheese Omelette",
        "icon": "🍳",
        "ingredients": [
            "egg",
            "cheese",
            "milk"
        ]
    },

    {
        "name": "Egg Sandwich",
        "icon": "🥪",
        "ingredients": [
            "bread",
            "egg",
            "cheese"
        ]
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
        ]
    },

    {
        "name": "Tomato Pasta",
        "icon": "🍝",
        "ingredients": [
            "pasta",
            "tomato",
            "onion",
            "cheese"
        ]
    },

    {
        "name": "Tuna Sandwich",
        "icon": "🥪",
        "ingredients": [
            "bread",
            "tuna",
            "lettuce",
            "tomato"
        ]
    },

    {
        "name": "Simple Salad",
        "icon": "🥗",
        "ingredients": [
            "lettuce",
            "tomato",
            "cucumber"
        ]
    },

    {
        "name": "Mashed Potato",
        "icon": "🥔",
        "ingredients": [
            "potato",
            "milk",
            "butter"
        ]
    },

    {
        "name": "Mushroom Omelette",
        "icon": "🍳",
        "ingredients": [
            "egg",
            "mushroom",
            "cheese"
        ]
    }
]


# =========================================================
# ACTIVITY TRACKING
# =========================================================

def add_activity(message):

    st.session_state.activity_log.insert(
        0,
        {
            "time": datetime.now().strftime(
                "%d %b %Y, %H:%M"
            ),
            "message": message
        }
    )

    st.session_state.activity_log = (
        st.session_state.activity_log[:30]
    )


# =========================================================
# DATE FUNCTIONS
# =========================================================

def to_date(value):

    if isinstance(value, date):
        return value

    return datetime.strptime(
        str(value),
        "%Y-%m-%d"
    ).date()


# =========================================================
# EXPIRY TRACKING
# =========================================================

def expiry_info(expiry_date):

    expiry_date = to_date(
        expiry_date
    )

    days_left = (
        expiry_date
        -
        date.today()
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

    return (
        days_left,
        status,
        priority
    )


def expiry_message(days_left):

    if days_left < 0:

        return (
            f"Expired "
            f"{abs(days_left)} day(s) ago"
        )

    if days_left == 0:

        return "Expires today"

    if days_left == 1:

        return "Expires tomorrow"

    return (
        f"Expires in "
        f"{days_left} days"
    )


# =========================================================
# SHELF LIFE PROGRESS
# =========================================================

def shelf_progress(item):

    purchase_date = to_date(
        item["purchase_date"]
    )

    expiry_date = to_date(
        item["expiry_date"]
    )

    total_days = max(
        (
            expiry_date
            -
            purchase_date
        ).days,
        1
    )

    passed_days = max(
        (
            date.today()
            -
            purchase_date
        ).days,
        0
    )

    progress = (
        passed_days
        /
        total_days
    )

    return min(
        max(
            progress,
            0.0
        ),
        1.0
    )


# =========================================================
# NORMALISE FOOD
# =========================================================

def normalize_food(food_name):

    food_name = (
        str(food_name)
        .lower()
        .strip()
    )

    for canonical, aliases in FOOD_ALIASES.items():

        for alias in aliases:

            if alias in food_name:

                return canonical

    return food_name


# =========================================================
# CREATE DATAFRAME
# =========================================================

def create_dataframe():

    rows = []

    for item in st.session_state.pantry_items:

        days_left, expiry_status, priority = (
            expiry_info(
                item["expiry_date"]
            )
        )

        rows.append(
            {
                "ID": item["id"],

                "Food":
                    item["item_name"],

                "Category":
                    item["category"],

                "Quantity":
                    item["quantity"],

                "Unit":
                    item["unit"],

                "Purchase Date":
                    item["purchase_date"],

                "Expiry Date":
                    item["expiry_date"],

                "Days Left":
                    days_left,

                "Expiry Status":
                    expiry_status,

                "Priority":
                    priority,

                "Cost (RM)":
                    float(
                        item["cost"]
                    ),

                "Storage":
                    item["storage"],

                "Item Status":
                    item["item_status"],

                "Status Date":
                    item.get(
                        "status_date",
                        ""
                    )
            }
        )

    return pd.DataFrame(
        rows
    )


# =========================================================
# ITEM STATUS
# =========================================================

def mark_item(
    item_id,
    new_status
):

    for item in st.session_state.pantry_items:

        if item["id"] == item_id:

            item["item_status"] = (
                new_status
            )

            item["status_date"] = str(
                date.today()
            )

            if new_status == "Consumed":

                add_activity(
                    f"✅ "
                    f"{item['item_name']} "
                    f"marked as consumed."
                )

            else:

                add_activity(
                    f"🗑️ "
                    f"{item['item_name']} "
                    f"marked as wasted."
                )

            break


def delete_item(item_id):

    for item in st.session_state.pantry_items:

        if item["id"] == item_id:

            add_activity(
                f"❌ "
                f"{item['item_name']} "
                f"removed from pantry."
            )

            break

    st.session_state.pantry_items = [

        item

        for item
        in st.session_state.pantry_items

        if item["id"] != item_id
    ]


# =========================================================
# PANTRY HEALTH SCORE
# =========================================================

def pantry_health_score(df):

    if df.empty:

        return 100, "Excellent"

    available = df[
        df["Item Status"]
        ==
        "Available"
    ]

    urgent = len(
        available[
            (
                available[
                    "Days Left"
                ]
                >= 0
            )
            &
            (
                available[
                    "Days Left"
                ]
                <= 2
            )
        ]
    )

    expired = len(
        available[
            available[
                "Days Left"
            ]
            < 0
        ]
    )

    wasted = len(
        df[
            df[
                "Item Status"
            ]
            ==
            "Wasted"
        ]
    )

    score = (
        100
        -
        urgent * 3
        -
        expired * 5
        -
        wasted * 2
    )

    score = max(
        0,
        min(
            score,
            100
        )
    )

    if score >= 90:

        label = "Excellent"

    elif score >= 75:

        label = "Good"

    elif score >= 50:

        label = "Needs Attention"

    else:

        label = "High Waste Risk"

    return (
        score,
        label
    )


# =========================================================
# RULE-BASED RECIPE MATCHING
# =========================================================

def calculate_recipe_matches():

    available_items = [

        item

        for item
        in st.session_state.pantry_items

        if item[
            "item_status"
        ]
        ==
        "Available"
    ]

    pantry = {}

    for item in available_items:

        food_key = normalize_food(
            item["item_name"]
        )

        if food_key not in pantry:

            pantry[
                food_key
            ] = []

        pantry[
            food_key
        ].append(
            item
        )

    results = []

    for recipe in RECIPES:

        ingredients = (
            recipe[
                "ingredients"
            ]
        )

        matched = [

            ingredient

            for ingredient
            in ingredients

            if ingredient
            in pantry
        ]

        missing = [

            ingredient

            for ingredient
            in ingredients

            if ingredient
            not in pantry
        ]

        match_percentage = (

            len(matched)
            /
            len(ingredients)
            *
            100
        )

        expiry_bonus = 0

        expiring_ingredients = []

        for ingredient in matched:

            best_days = min(

                expiry_info(
                    food[
                        "expiry_date"
                    ]
                )[0]

                for food
                in pantry[
                    ingredient
                ]
            )

            if (
                best_days >= 0
                and
                best_days <= 2
            ):

                expiry_bonus += 8

                expiring_ingredients.append(
                    (
                        ingredient,
                        best_days
                    )
                )

            elif (
                best_days >= 3
                and
                best_days <= 7
            ):

                expiry_bonus += 5

                expiring_ingredients.append(
                    (
                        ingredient,
                        best_days
                    )
                )

        expiry_bonus = min(
            expiry_bonus,
            20
        )

        score = (

            match_percentage
            *
            0.8

            +

            expiry_bonus
        )

        score = min(
            score,
            100
        )

        results.append(
            {
                "name":
                    recipe["name"],

                "icon":
                    recipe["icon"],

                "ingredients":
                    ingredients,

                "matched":
                    matched,

                "missing":
                    missing,

                "match_percentage":
                    match_percentage,

                "expiry_bonus":
                    expiry_bonus,

                "score":
                    score,

                "expiring":
                    expiring_ingredients
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# =========================================================
# AI MODEL
# =========================================================

def call_ai_model(prompt):

    try:

        api_key = (
            st.secrets[
                "OPENROUTER_API_KEY"
            ]
        )

    except Exception:

        return (
            None,
            "AI is not configured yet. "
            "Add OPENROUTER_API_KEY "
            "to Streamlit Secrets."
        )

    try:

        model = st.secrets.get(
            "OPENROUTER_MODEL",
            "openrouter/free"
        )

    except Exception:

        model = "openrouter/free"

    try:

        response = requests.post(

            "https://openrouter.ai/"
            "api/v1/chat/completions",

            headers={
                "Authorization":
                    f"Bearer {api_key}",

                "Content-Type":
                    "application/json"
            },

            json={
                "model":
                    model,

                "messages": [

                    {
                        "role":
                            "system",

                        "content":
                            (
                                "You are SmartPantry AI, "
                                "a concise household food "
                                "waste reduction assistant. "
                                "Use the pantry information "
                                "provided by the user. "
                                "Prioritize ingredients "
                                "that expire sooner. "
                                "Do not claim a food is safe "
                                "only because its expiry date "
                                "has not passed. Encourage "
                                "normal food-safety checks. "
                                "Keep recommendations "
                                "simple and practical."
                            )
                    },

                    {
                        "role":
                            "user",

                        "content":
                            prompt
                    }
                ],

                "temperature":
                    0.4,

                "max_tokens":
                    700
            },

            timeout=45
        )

        response.raise_for_status()

        data = response.json()

        result = (
            data[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ]
        )

        return (
            result,
            None
        )

    except Exception as error:

        return (
            None,
            f"AI request failed: "
            f"{error}"
        )


# =========================================================
# CREATE AI PANTRY CONTEXT
# =========================================================

def pantry_context():

    df = create_dataframe()

    if df.empty:

        return (
            "The pantry is empty."
        )

    available = df[
        df[
            "Item Status"
        ]
        ==
        "Available"
    ].sort_values(
        "Days Left"
    )

    lines = []

    for _, item in available.iterrows():

        lines.append(

            f"- {item['Food']}: "
            f"{item['Quantity']} "
            f"{item['Unit']}, "
            f"{item['Days Left']} "
            f"days remaining, "
            f"{item['Expiry Status']}, "
            f"RM{item['Cost (RM)']:.2f}"
        )

    return "\n".join(
        lines
    )


# =========================================================
# DEMO DATA
# =========================================================

def load_demo_data():

    today = date.today()

    sample_data = [

        (
            "Fresh Milk",
            "Dairy",
            1,
            "Bottle",
            2,
            7.50,
            "Refrigerator"
        ),

        (
            "Chicken Breast",
            "Meat",
            1,
            "Pack",
            4,
            12.00,
            "Refrigerator"
        ),

        (
            "Eggs",
            "Dairy",
            10,
            "Piece",
            7,
            8.50,
            "Refrigerator"
        ),

        (
            "Bread",
            "Bakery",
            1,
            "Pack",
            3,
            4.50,
            "Pantry"
        ),

        (
            "Cheese",
            "Dairy",
            1,
            "Pack",
            8,
            9.50,
            "Refrigerator"
        ),

        (
            "Tomatoes",
            "Vegetables",
            4,
            "Piece",
            5,
            5.00,
            "Refrigerator"
        ),

        (
            "Rice",
            "Dry Food",
            2,
            "kg",
            120,
            18.00,
            "Pantry"
        ),

        (
            "Carrots",
            "Vegetables",
            3,
            "Piece",
            9,
            4.00,
            "Refrigerator"
        ),

        (
            "Onions",
            "Vegetables",
            4,
            "Piece",
            20,
            4.50,
            "Pantry"
        ),

        (
            "Pasta",
            "Dry Food",
            2,
            "Pack",
            90,
            10.00,
            "Pantry"
        )
    ]

    for (
        name,
        category,
        quantity,
        unit,
        days,
        cost,
        storage
    ) in sample_data:

        st.session_state.pantry_items.append(
            {
                "id":
                    str(
                        uuid.uuid4()
                    ),

                "item_name":
                    name,

                "category":
                    category,

                "quantity":
                    quantity,

                "unit":
                    unit,

                "purchase_date":
                    str(today),

                "expiry_date":
                    str(
                        today
                        +
                        timedelta(
                            days=days
                        )
                    ),

                "cost":
                    cost,

                "storage":
                    storage,

                "item_status":
                    "Available",

                "status_date":
                    ""
            }
        )

    add_activity(
        "🧪 Demo pantry data loaded."
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.title(
    "🥕 SmartPantry"
)

st.caption(
    "Track • Use • Save • Reduce Waste"
)


# =========================================================
# NAVIGATION
# =========================================================

page = st.sidebar.radio(

    "Navigation",

    [
        "🏠 Overview",
        "📍 Food Tracker",
        "➕ Add Item",
        "📅 Expiry Calendar",
        "🍳 Meal Planner",
        "📊 Insights"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "SmartPantry monitors food "
    "through its pantry lifecycle "
    "and helps reduce avoidable waste."
)


if not st.session_state.pantry_items:

    if st.sidebar.button(
        "🧪 Load Demo Data",
        use_container_width=True
    ):

        load_demo_data()

        st.rerun()


# =========================================================
# OVERVIEW PAGE
# =========================================================

if page == "🏠 Overview":

    st.header(
        "🏠 Pantry Overview"
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Your pantry is empty. "
            "Add your first item or "
            "load the demo data."
        )

    else:

        available = df[
            df[
                "Item Status"
            ]
            ==
            "Available"
        ]

        consumed = df[
            df[
                "Item Status"
            ]
            ==
            "Consumed"
        ]

        wasted = df[
            df[
                "Item Status"
            ]
            ==
            "Wasted"
        ]

        attention = available[
            available[
                "Days Left"
            ]
            <= 7
        ]

        health_score, health_label = (
            pantry_health_score(
                df
            )
        )

        pantry_value = available[
            "Cost (RM)"
        ].sum()

        value_at_risk = attention[
            "Cost (RM)"
        ].sum()


        # =================================================
        # HEALTH SCORE
        # =================================================

        left, right = st.columns(
            [2, 1]
        )

        with left:

            st.subheader(
                "Pantry Health"
            )

            st.progress(
                health_score / 100
            )

            st.markdown(
                f"### "
                f"{health_score}/100 "
                f"— {health_label}"
            )

        with right:

            st.metric(
                "💰 Pantry Value",
                f"RM "
                f"{pantry_value:.2f}"
            )

            st.metric(
                "⚠️ Value at Risk",
                f"RM "
                f"{value_at_risk:.2f}"
            )


        # =================================================
        # KPI
        # =================================================

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "🥫 Available",
            len(available)
        )

        col2.metric(
            "🚨 Need Attention",
            len(attention)
        )

        col3.metric(
            "🌱 Food Saved",
            len(consumed)
        )

        col4.metric(
            "🗑️ Wasted",
            len(wasted)
        )


        # =================================================
        # NEEDS ATTENTION
        # =================================================

        st.divider()

        st.subheader(
            "🚨 Needs Attention"
        )

        if attention.empty:

            st.success(
                "No food needs "
                "urgent attention."
            )

        else:

            attention = (
                attention.sort_values(
                    "Days Left"
                )
            )

            for _, item in (
                attention
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

                        st.markdown(
                            f"### "
                            f"{item['Food']}"
                        )

                        st.write(
                            item[
                                "Expiry Status"
                            ]
                        )

                    with c2:

                        st.write(
                            expiry_message(
                                item[
                                    "Days Left"
                                ]
                            )
                        )

                        st.caption(
                            f"{item['Quantity']} "
                            f"{item['Unit']} • "
                            f"{item['Storage']}"
                        )

                    with c3:

                        st.metric(
                            "At Risk",
                            f"RM "
                            f"{item['Cost (RM)']:.2f}"
                        )


        # =================================================
        # COOK FIRST
        # =================================================

        st.divider()

        st.subheader(
            "🍳 Cook These First"
        )

        recommendations = [

            recipe

            for recipe
            in calculate_recipe_matches()

            if recipe[
                "match_percentage"
            ]
            >= 60

        ][:3]

        if not recommendations:

            st.info(
                "Add more ingredients "
                "to receive meal "
                "recommendations."
            )

        else:

            for recipe in recommendations:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### "
                        f"{recipe['icon']} "
                        f"{recipe['name']}"
                    )

                    st.write(
                        "**Ingredient Match:** "
                        f"{recipe['match_percentage']:.0f}%"
                    )

                    st.progress(
                        recipe[
                            "match_percentage"
                        ]
                        /
                        100
                    )

                    if recipe[
                        "expiring"
                    ]:

                        st.caption(
                            "⚠ Uses ingredients "
                            "that are expiring soon."
                        )


        # =================================================
        # ACTIVITY
        # =================================================

        st.divider()

        st.subheader(
            "🕘 Recent Activity"
        )

        if not (
            st.session_state.activity_log
        ):

            st.caption(
                "No activity yet."
            )

        else:

            for activity in (
                st.session_state
                .activity_log[:6]
            ):

                st.write(
                    f"**"
                    f"{activity['time']}"
                    f"** — "
                    f"{activity['message']}"
                )


# =========================================================
# FOOD TRACKER
# =========================================================

elif page == "📍 Food Tracker":

    st.header(
        "📍 Food Tracker"
    )

    st.caption(
        "Follow each food item "
        "through its pantry lifecycle."
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "No pantry items yet."
        )

    else:

        f1, f2, f3 = (
            st.columns(3)
        )

        search = f1.text_input(
            "Search"
        )

        category_filter = (
            f2.selectbox(
                "Category",
                [
                    "All"
                ]
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

        filtered_df = (
            df.copy()
        )

        if search:

            filtered_df = filtered_df[

                filtered_df[
                    "Food"
                ]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":

            filtered_df = filtered_df[
                filtered_df[
                    "Category"
                ]
                ==
                category_filter
            ]

        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df[
                    "Item Status"
                ]
                ==
                status_filter
            ]


        filtered_df = (
            filtered_df
            .sort_values(
                "Days Left"
            )
        )


        for _, row in (
            filtered_df.iterrows()
        ):

            item = next(

                pantry_item

                for pantry_item
                in st.session_state
                .pantry_items

                if pantry_item[
                    "id"
                ]
                ==
                row["ID"]
            )

            with st.container(
                border=True
            ):

                left, right = (
                    st.columns(
                        [4, 1]
                    )
                )

                with left:

                    st.markdown(
                        f"### "
                        f"{row['Food']} "
                        f"· "
                        f"{row['Expiry Status']}"
                    )

                    st.caption(
                        f"{row['Category']} "
                        f"• {row['Storage']} "
                        f"• RM "
                        f"{row['Cost (RM)']:.2f}"
                    )

                    if (
                        row[
                            "Item Status"
                        ]
                        ==
                        "Available"
                    ):

                        progress = (
                            shelf_progress(
                                item
                            )
                        )

                        st.progress(
                            progress
                        )

                        st.write(
                            f"**"
                            f"{progress * 100:.0f}% "
                            f"of usable period passed"
                            f"**"
                        )

                        st.caption(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )

                    else:

                        st.write(
                            "**Status:** "
                            f"{row['Item Status']}"
                        )


                with right:

                    st.metric(
                        "Quantity",
                        f"{row['Quantity']} "
                        f"{row['Unit']}"
                    )


                if (
                    row[
                        "Item Status"
                    ]
                    ==
                    "Available"
                ):

                    b1, b2, b3 = (
                        st.columns(3)
                    )

                    if b1.button(
                        "✅ Consumed",
                        key=(
                            f"consume_"
                            f"{row['ID']}"
                        ),
                        use_container_width=True
                    ):

                        mark_item(
                            row["ID"],
                            "Consumed"
                        )

                        st.rerun()


                    if b2.button(
                        "🗑️ Wasted",
                        key=(
                            f"waste_"
                            f"{row['ID']}"
                        ),
                        use_container_width=True
                    ):

                        mark_item(
                            row["ID"],
                            "Wasted"
                        )

                        st.rerun()


                    if b3.button(
                        "❌ Delete",
                        key=(
                            f"delete_"
                            f"{row['ID']}"
                        ),
                        use_container_width=True
                    ):

                        delete_item(
                            row["ID"]
                        )

                        st.rerun()


# =========================================================
# ADD ITEM
# =========================================================

elif page == "➕ Add Item":

    st.header(
        "➕ Add Pantry Item"
    )

    st.write(
        "Add food to begin tracking "
        "its expiry lifecycle."
    )

    with st.form(
        "add_item",
        clear_on_submit=True
    ):

        left, right = (
            st.columns(2)
        )

        with left:

            food_name = (
                st.text_input(
                    "Food Name *"
                )
            )

            category = (
                st.selectbox(
                    "Category",
                    CATEGORIES
                )
            )

            quantity = (
                st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1
                )
            )

            unit = (
                st.selectbox(
                    "Unit",
                    UNITS
                )
            )


        with right:

            purchase_date = (
                st.date_input(
                    "Purchase Date",
                    value=date.today()
                )
            )

            expiry_date = (
                st.date_input(
                    "Expiry Date",
                    value=(
                        date.today()
                        +
                        timedelta(
                            days=7
                        )
                    )
                )
            )

            cost = (
                st.number_input(
                    "Total Cost (RM)",
                    min_value=0.0,
                    value=0.0,
                    step=0.50
                )
            )

            storage = (
                st.selectbox(
                    "Storage Location",
                    STORAGE
                )
            )


        submitted = (
            st.form_submit_button(
                "➕ Add to Pantry",
                use_container_width=True
            )
        )


        if submitted:

            if not food_name.strip():

                st.error(
                    "Please enter "
                    "a food name."
                )

            elif (
                expiry_date
                <
                purchase_date
            ):

                st.error(
                    "Expiry date cannot "
                    "be earlier than "
                    "purchase date."
                )

            else:

                item = {

                    "id":
                        str(
                            uuid.uuid4()
                        ),

                    "item_name":
                        food_name.strip(),

                    "category":
                        category,

                    "quantity":
                        int(quantity),

                    "unit":
                        unit,

                    "purchase_date":
                        str(
                            purchase_date
                        ),

                    "expiry_date":
                        str(
                            expiry_date
                        ),

                    "cost":
                        float(cost),

                    "storage":
                        storage,

                    "item_status":
                        "Available",

                    "status_date":
                        ""
                }

                st.session_state.pantry_items.append(
                    item
                )

                add_activity(
                    f"➕ "
                    f"{food_name.strip()} "
                    f"added to pantry."
                )

                days_left, status, _ = (
                    expiry_info(
                        expiry_date
                    )
                )

                st.success(
                    f"{food_name.strip()} "
                    f"added successfully."
                )

                st.info(
                    f"{status} — "
                    f"{expiry_message(days_left)}"
                )


# =========================================================
# EXPIRY CALENDAR
# =========================================================

elif page == "📅 Expiry Calendar":

    st.header(
        "📅 Expiry Calendar"
    )

    st.caption(
        "See what needs to be "
        "used today, tomorrow "
        "and later this week."
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "No pantry items yet."
        )

    else:

        available = df[
            df[
                "Item Status"
            ]
            ==
            "Available"
        ].sort_values(
            "Days Left"
        )


        groups = [

            (
                "🚨 Expired",

                available[
                    available[
                        "Days Left"
                    ]
                    < 0
                ]
            ),

            (
                "📍 Today",

                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    0
                ]
            ),

            (
                "🌅 Tomorrow",

                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    1
                ]
            ),

            (
                "📆 Next 7 Days",

                available[
                    (
                        available[
                            "Days Left"
                        ]
                        >= 2
                    )
                    &
                    (
                        available[
                            "Days Left"
                        ]
                        <= 7
                    )
                ]
            ),

            (
                "🗓️ Later",

                available[
                    available[
                        "Days Left"
                    ]
                    > 7
                ]
            )
        ]


        for title, group in groups:

            st.subheader(
                title
            )

            if group.empty:

                st.caption(
                    "No items."
                )

            else:

                for _, row in (
                    group.iterrows()
                ):

                    with st.container(
                        border=True
                    ):

                        c1, c2 = (
                            st.columns(
                                [3, 1]
                            )
                        )

                        c1.write(
                            f"**{row['Food']}**"
                        )

                        c1.caption(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )

                        c2.write(
                            f"{row['Quantity']} "
                            f"{row['Unit']}"
                        )


# =========================================================
# MEAL PLANNER
# =========================================================

elif page == "🍳 Meal Planner":

    st.header(
        "🍳 Meal Planner"
    )

    df = create_dataframe()

    if (
        df.empty
        or
        df[
            df[
                "Item Status"
            ]
            ==
            "Available"
        ].empty
    ):

        st.info(
            "Add available food "
            "before using the "
            "meal planner."
        )

    else:

        # =================================================
        # RULE BASED
        # =================================================

        st.subheader(
            "🎯 Smart Recipe Matches"
        )

        st.caption(
            "These results are calculated "
            "from ingredient availability "
            "and expiry priority."
        )

        minimum_match = (
            st.slider(
                "Minimum Ingredient Match",
                0,
                100,
                50,
                10
            )
        )

        recipes = [

            recipe

            for recipe
            in calculate_recipe_matches()

            if recipe[
                "match_percentage"
            ]
            >= minimum_match
        ]


        for number, recipe in enumerate(
            recipes[:6],
            start=1
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### "
                    f"{number}. "
                    f"{recipe['icon']} "
                    f"{recipe['name']}"
                )

                st.write(
                    "**Ingredient Match:** "
                    f"{recipe['match_percentage']:.0f}%"
                )

                st.write(
                    "**Recommendation Score:** "
                    f"{recipe['score']:.0f}/100"
                )

                st.progress(
                    recipe[
                        "match_percentage"
                    ]
                    /
                    100
                )

                if recipe[
                    "matched"
                ]:

                    st.write(
                        "✅ **Available:** "
                        +
                        ", ".join(
                            ingredient.title()

                            for ingredient
                            in recipe[
                                "matched"
                            ]
                        )
                    )

                if recipe[
                    "missing"
                ]:

                    st.write(
                        "🛒 **Missing:** "
                        +
                        ", ".join(
                            ingredient.title()

                            for ingredient
                            in recipe[
                                "missing"
                            ]
                        )
                    )

                if recipe[
                    "expiring"
                ]:

                    st.warning(
                        "This meal uses "
                        "ingredients that "
                        "are expiring soon."
                    )


        # =================================================
        # AI
        # =================================================

        st.divider()

        st.subheader(
            "✨ AI Kitchen Coach"
        )

        st.caption(
            "AI creates flexible meal ideas. "
            "Expiry tracking and pantry scores "
            "remain rule-based."
        )

        preference = (
            st.text_input(
                "Optional Preference",
                placeholder=(
                    "Example: "
                    "quick meal, "
                    "vegetarian, "
                    "budget meal"
                )
            )
        )


        if st.button(
            "✨ Generate AI Meal Plan",
            use_container_width=True
        ):

            prompt = f"""
My current SmartPantry inventory is:

{pantry_context()}

My preference is:
{preference if preference else "No special preference"}

Generate exactly 3 simple meal ideas.

Prioritize ingredients with fewer days remaining.

For every meal provide:
- Meal name
- Pantry ingredients used
- Additional ingredients needed, if any
- A short reason explaining how the meal helps reduce food waste

Keep the suggestions concise and practical.
"""

            with st.spinner(
                "SmartPantry AI "
                "is preparing ideas..."
            ):

                answer, error = (
                    call_ai_model(
                        prompt
                    )
                )

            if error:

                st.warning(
                    error
                )

            else:

                st.markdown(
                    answer
                )


# =========================================================
# INSIGHTS PAGE
# =========================================================

elif page == "📊 Insights":

    st.header(
        "📊 Tracking Insights"
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Add food records "
            "to view insights."
        )

    else:

        consumed = df[
            df[
                "Item Status"
            ]
            ==
            "Consumed"
        ]

        wasted = df[
            df[
                "Item Status"
            ]
            ==
            "Wasted"
        ]

        available = df[
            df[
                "Item Status"
            ]
            ==
            "Available"
        ]


        completed_items = (
            len(consumed)
            +
            len(wasted)
        )


        if completed_items:

            waste_avoidance = (

                len(consumed)
                /
                completed_items
                *
                100
            )

        else:

            waste_avoidance = 0


        value_saved = (
            consumed[
                "Cost (RM)"
            ].sum()
        )

        waste_cost = (
            wasted[
                "Cost (RM)"
            ].sum()
        )


        # =================================================
        # KPI
        # =================================================

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "🌱 Food Saved",
            len(consumed)
        )

        c2.metric(
            "💚 Value Saved",
            f"RM "
            f"{value_saved:.2f}"
        )

        c3.metric(
            "🗑️ Waste Cost",
            f"RM "
            f"{waste_cost:.2f}"
        )

        c4.metric(
            "📈 Waste Avoidance",
            f"{waste_avoidance:.1f}%"
        )


        # =================================================
        # CONSUMED VS WASTED
        # =================================================

        if completed_items:

            outcome_df = (
                pd.DataFrame(
                    {
                        "Status": [
                            "Consumed",
                            "Wasted"
                        ],

                        "Items": [
                            len(consumed),
                            len(wasted)
                        ]
                    }
                )
            )

            outcome_chart = px.pie(

                outcome_df,

                names="Status",

                values="Items",

                hole=0.45,

                title=(
                    "Consumed vs Wasted"
                )
            )

            st.plotly_chart(
                outcome_chart,
                use_container_width=True
            )


        # =================================================
        # PANTRY CATEGORY VALUE
        # =================================================

        if not available.empty:

            category_value = (

                available
                .groupby(
                    "Category"
                )[
                    "Cost (RM)"
                ]
                .sum()
                .reset_index()
            )

            category_chart = px.bar(

                category_value,

                x="Category",

                y="Cost (RM)",

                title=(
                    "Current Pantry Value "
                    "by Category"
                )
            )

            st.plotly_chart(
                category_chart,
                use_container_width=True
            )


        # =================================================
        # AI INSIGHT
        # =================================================

        st.divider()

        st.subheader(
            "🤖 AI Pantry Insight"
        )

        st.caption(
            "Ask the model to analyse "
            "your current tracking results."
        )


        if st.button(
            "🤖 Generate AI Insight"
        ):

            prompt = f"""
Current available pantry:

{pantry_context()}

Tracking summary:

Consumed items: {len(consumed)}
Wasted items: {len(wasted)}
Food value saved: RM{value_saved:.2f}
Waste cost: RM{waste_cost:.2f}
Waste avoidance rate: {waste_avoidance:.1f}%

Give exactly 3 short and specific actions
that could help reduce household food waste
during the next week.

Base the recommendations on the information above.
"""

            with st.spinner(
                "Analysing pantry..."
            ):

                answer, error = (
                    call_ai_model(
                        prompt
                    )
                )

            if error:

                st.warning(
                    error
                )

            else:

                st.markdown(
                    answer
                )


        # =================================================
        # CSV BACKUP
        # =================================================

        st.divider()

        st.subheader(
            "💾 Pantry Backup"
        )

        backup_df = (
            pd.DataFrame(
                st.session_state
                .pantry_items
            )
        )

        backup_csv = (
            backup_df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )

        st.download_button(

            "⬇️ Download Pantry Backup",

            data=backup_csv,

            file_name=(
                "smartpantry_backup.csv"
            ),

            mime="text/csv"
        )
