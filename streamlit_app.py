import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import uuid
import json
import hashlib
import re
import textwrap

from datetime import date, datetime, timedelta


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HTML HELPER
# Prevents HTML from appearing as <div> code blocks
# ============================================================

def render_html(html: str):

    st.markdown(
        textwrap.dedent(html).strip(),
        unsafe_allow_html=True
    )


# ============================================================
# WEBSITE CSS
# ============================================================

CUSTOM_CSS = """
<style>

:root {
    --sp-green-900: #10271f;
    --sp-green-800: #16372b;
    --sp-green-700: #24553f;
    --sp-green-600: #39785a;
    --sp-green-500: #5a9a73;
    --sp-green-300: #9ac5a7;
    --sp-green-100: #e8f3eb;
    --sp-border: rgba(127, 127, 127, 0.18);
}


/* =========================================================
   MAIN PAGE
   ========================================================= */

.block-container {

    max-width: 1280px;

    padding-top: 1.3rem;

    padding-bottom: 4rem;
}


html,
body,
[class*="css"] {

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


/* =========================================================
   HERO
   ========================================================= */

.sp-hero {

    position: relative;

    overflow: hidden;

    border-radius: 26px;

    padding: 38px 42px;

    margin-bottom: 26px;

    background:
        linear-gradient(
            135deg,
            #102d23 0%,
            #265b43 50%,
            #7ba083 100%
        );

    color: #ffffff;

    box-shadow:
        0 16px 40px
        rgba(0, 0, 0, 0.18);
}


.sp-hero::before {

    content: "";

    position: absolute;

    width: 280px;

    height: 280px;

    right: -90px;

    top: -120px;

    border-radius: 50%;

    background:
        rgba(255,255,255,0.08);
}


.sp-hero::after {

    content: "";

    position: absolute;

    width: 160px;

    height: 160px;

    right: 130px;

    bottom: -100px;

    border-radius: 50%;

    background:
        rgba(255,255,255,0.05);
}


.sp-hero-badge {

    display: inline-block;

    padding: 6px 11px;

    border:
        1px solid
        rgba(255,255,255,0.19);

    border-radius: 999px;

    background:
        rgba(255,255,255,0.10);

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 0.7px;

    margin-bottom: 14px;
}


.sp-hero-title {

    font-size: 42px;

    font-weight: 850;

    line-height: 1.05;

    letter-spacing: -1.2px;

    margin-bottom: 10px;
}


.sp-hero-subtitle {

    max-width: 720px;

    font-size: 16px;

    line-height: 1.6;

    color:
        rgba(255,255,255,0.86);
}


/* =========================================================
   PAGE HEADER
   ========================================================= */

.sp-page-kicker {

    font-size: 12px;

    text-transform: uppercase;

    font-weight: 800;

    letter-spacing: 1.1px;

    opacity: 0.58;

    margin-bottom: 4px;
}


.sp-page-title {

    font-size: 29px;

    font-weight: 820;

    letter-spacing: -0.6px;

    margin-bottom: 4px;
}


.sp-page-subtitle {

    opacity: 0.68;

    margin-bottom: 20px;
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

.sp-card {

    border:
        1px solid
        var(--sp-border);

    border-radius: 20px;

    padding: 20px;

    min-height: 132px;

    background:
        rgba(255,255,255,0.025);

    box-shadow:
        0 7px 25px
        rgba(0,0,0,0.055);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        box-shadow 0.18s ease;
}


.sp-card:hover {

    transform:
        translateY(-2px);

    border-color:
        rgba(90,154,115,0.42);

    box-shadow:
        0 11px 30px
        rgba(0,0,0,0.09);
}


.sp-card-icon {

    font-size: 25px;

    margin-bottom: 10px;
}


.sp-card-value {

    font-size: 27px;

    font-weight: 850;

    line-height: 1.15;

    margin-bottom: 5px;
}


.sp-card-label {

    font-size: 13px;

    font-weight: 600;

    opacity: 0.62;
}


/* =========================================================
   AI BANNER
   ========================================================= */

.sp-ai-banner {

    border:
        1px solid
        rgba(91,166,116,0.30);

    border-radius: 20px;

    padding: 20px 22px;

    background:
        linear-gradient(
            120deg,
            rgba(54,121,80,0.15),
            rgba(121,167,132,0.05)
        );

    margin:
        8px 0 18px 0;
}


.sp-ai-title {

    font-size: 19px;

    font-weight: 820;

    margin-bottom: 5px;
}


.sp-ai-subtitle {

    opacity: 0.70;

    line-height: 1.55;
}


/* =========================================================
   STATUS PILLS
   ========================================================= */

.sp-pill {

    display: inline-block;

    padding:
        5px 10px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 800;
}


.sp-fresh {

    background: #dcfce7;

    color: #166534;
}


.sp-use {

    background: #fef3c7;

    color: #92400e;
}


.sp-soon {

    background: #ffedd5;

    color: #9a3412;
}


.sp-urgent {

    background: #fee2e2;

    color: #991b1b;
}


.sp-expired {

    background: #e5e7eb;

    color: #374151;
}


/* =========================================================
   STREAMLIT CONTAINERS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {

    border-radius: 18px;
}


div[data-testid="stMetric"] {

    border-radius: 16px;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {

    border-radius: 12px;

    font-weight: 650;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 6px 18px
        rgba(0,0,0,0.10);
}


/* =========================================================
   SIDEBAR BACKGROUND
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #11251d 0%,
            #142c22 48%,
            #0f2019 100%
        );

    border-right:
        1px solid
        rgba(255,255,255,0.06);
}


section[data-testid="stSidebar"]
div[data-testid="stSidebarContent"] {

    padding-top: 0.5rem;
}


/* =========================================================
   SIDEBAR BRAND
   ========================================================= */

.sp-side-brand {

    padding: 16px;

    margin:
        3px 2px 16px 2px;

    border:
        1px solid
        rgba(162,211,177,0.16);

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            rgba(89,162,113,0.22),
            rgba(255,255,255,0.03)
        );
}


.sp-side-brand-row {

    display: flex;

    align-items: center;

    gap: 11px;
}


.sp-side-logo {

    width: 43px;

    height: 43px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 13px;

    font-size: 23px;

    background:
        linear-gradient(
            135deg,
            #79bf91,
            #387759
        );

    box-shadow:
        0 8px 20px
        rgba(0,0,0,0.22);
}


.sp-side-name {

    color: #ffffff;

    font-size: 18px;

    font-weight: 850;
}


.sp-side-sub {

    color:
        rgba(255,255,255,0.56);

    font-size: 11px;

    margin-top: 1px;
}


.sp-side-live {

    margin-top: 12px;

    display: inline-block;

    padding:
        5px 9px;

    border-radius: 999px;

    background:
        rgba(103,207,137,0.10);

    color: #a9e7bc;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 0.4px;
}


/* =========================================================
   SIDEBAR SECTION LABEL
   ========================================================= */

.sp-side-label {

    color:
        rgba(255,255,255,0.38);

    font-size: 10px;

    font-weight: 850;

    text-transform: uppercase;

    letter-spacing: 1.15px;

    margin:
        17px 9px 6px 9px;
}


/* =========================================================
   SIDEBAR AI STATUS
   ========================================================= */

.sp-side-ai {

    padding: 14px;

    margin:
        7px 2px;

    border-radius: 15px;

    border:
        1px solid
        rgba(255,255,255,0.07);

    background:
        rgba(255,255,255,0.04);
}


.sp-side-ai-row {

    display: flex;

    align-items: center;

    justify-content: space-between;
}


.sp-side-ai-title {

    color: #ffffff;

    font-size: 13px;

    font-weight: 800;
}


.sp-side-dot {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #5ee58a;

    box-shadow:
        0 0 0 4px
        rgba(94,229,138,0.10);
}


.sp-side-muted {

    color:
        rgba(255,255,255,0.48);

    font-size: 11px;

    margin-top: 7px;
}


/* =========================================================
   SIDEBAR FOOTER
   ========================================================= */

.sp-side-footer {

    text-align: center;

    color:
        rgba(255,255,255,0.28);

    font-size: 10px;

    padding:
        18px 5px 5px 5px;
}


/* =========================================================
   SIDEBAR NAVIGATION
   ========================================================= */

section[data-testid="stSidebar"]
div[role="radiogroup"] {

    gap: 4px;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"] {

    padding:
        10px 12px;

    margin:
        1px 2px;

    border-radius: 12px;

    border:
        1px solid
        transparent;

    cursor: pointer;

    transition:
        all 0.16s ease;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"]:hover {

    background:
        rgba(255,255,255,0.055);

    border-color:
        rgba(255,255,255,0.06);

    transform:
        translateX(2px);
}


/* Hide original circle */

section[data-testid="stSidebar"]
label[data-baseweb="radio"]
div[role="radio"] {

    display: none;
}


/* Active navigation */

section[data-testid="stSidebar"]
label[data-baseweb="radio"]:has(input:checked) {

    background:
        linear-gradient(
            90deg,
            rgba(79,165,109,0.33),
            rgba(79,165,109,0.08)
        );

    border-color:
        rgba(126,210,151,0.24);

    box-shadow:
        inset 3px 0 0
        #76d394;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"] p {

    color:
        rgba(255,255,255,0.82);

    font-size: 14px;

    font-weight: 570;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"]:has(input:checked) p {

    color: #ffffff;

    font-weight: 760;
}


/* Sidebar widget labels */

section[data-testid="stSidebar"]
[data-testid="stWidgetLabel"] p {

    color:
        rgba(255,255,255,0.82);
}


section[data-testid="stSidebar"] hr {

    border-color:
        rgba(255,255,255,0.08);
}

</style>
"""


st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "pantry_items" not in st.session_state:

    st.session_state.pantry_items = []


if "activity_log" not in st.session_state:

    st.session_state.activity_log = []


if "ai_meal_plan" not in st.session_state:

    st.session_state.ai_meal_plan = None


if "ai_plan_raw" not in st.session_state:

    st.session_state.ai_plan_raw = ""


if "ai_plan_error" not in st.session_state:

    st.session_state.ai_plan_error = None


if "ai_plan_signature" not in st.session_state:

    st.session_state.ai_plan_signature = ""


if "ai_attempt_signature" not in st.session_state:

    st.session_state.ai_attempt_signature = ""


if "ai_last_updated" not in st.session_state:

    st.session_state.ai_last_updated = None


if "planner_preference" not in st.session_state:

    st.session_state.planner_preference = (
        "Practical everyday meals"
    )


if "planner_servings" not in st.session_state:

    st.session_state.planner_servings = 2


if "planner_time" not in st.session_state:

    st.session_state.planner_time = (
        "30 minutes"
    )


if "auto_ai_planner" not in st.session_state:

    st.session_state.auto_ai_planner = True


if "flash_message" not in st.session_state:

    st.session_state.flash_message = ""


# ============================================================
# CONSTANTS
# ============================================================

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

    "Others",
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


STORAGE_LOCATIONS = [

    "Refrigerator",

    "Freezer",

    "Pantry",

    "Kitchen Cabinet",

    "Others"
]


# ============================================================
# ACTIVITY LOG
# ============================================================

def add_activity(message):

    st.session_state.activity_log.insert(
        0,
        {
            "time":
                datetime.now().strftime(
                    "%d %b %Y • %H:%M"
                ),

            "message":
                message,
        },
    )

    st.session_state.activity_log = (
        st.session_state.activity_log[:40]
    )


# ============================================================
# DATE HELPERS
# ============================================================

def to_date(value):

    if isinstance(
        value,
        date
    ):

        return value

    return datetime.strptime(
        str(value),
        "%Y-%m-%d"
    ).date()


# ============================================================
# EXPIRY ENGINE
# ============================================================

def expiry_info(
    expiry_date
):

    days_left = (
        to_date(
            expiry_date
        )
        -
        date.today()
    ).days


    if days_left < 0:

        return (
            days_left,
            "Expired",
            100
        )


    if days_left <= 2:

        return (
            days_left,
            "Urgent",
            90
        )


    if days_left <= 7:

        return (
            days_left,
            "Expiring Soon",
            75
        )


    if days_left <= 14:

        return (
            days_left,
            "Use Soon",
            40
        )


    return (
        days_left,
        "Fresh",
        20
    )


# ============================================================
# EXPIRY MESSAGE
# ============================================================

def expiry_message(
    days_left
):

    if days_left < 0:

        number = abs(
            days_left
        )

        return (
            f"Expired "
            f"{number} "
            f"day"
            f"{'s' if number != 1 else ''} "
            f"ago"
        )


    if days_left == 0:

        return (
            "Expires today"
        )


    if days_left == 1:

        return (
            "Expires tomorrow"
        )


    return (
        f"Expires in "
        f"{days_left} days"
    )


# ============================================================
# STATUS BADGE
# ============================================================

def status_html(
    status
):

    mapping = {

        "Fresh":
            (
                "sp-fresh",
                "🟢 Fresh"
            ),

        "Use Soon":
            (
                "sp-use",
                "🟡 Use Soon"
            ),

        "Expiring Soon":
            (
                "sp-soon",
                "🟠 Expiring Soon"
            ),

        "Urgent":
            (
                "sp-urgent",
                "🔴 Urgent"
            ),

        "Expired":
            (
                "sp-expired",
                "⚫ Expired"
            )
    }


    css_class, label = (
        mapping.get(
            status,
            (
                "sp-expired",
                status
            )
        )
    )


    return (
        f'<span class="sp-pill '
        f'{css_class}">'
        f'{label}'
        f'</span>'
    )


# ============================================================
# SHELF-LIFE PROGRESS
# ============================================================

def shelf_progress(
    item
):

    purchase = to_date(
        item[
            "purchase_date"
        ]
    )

    expiry = to_date(
        item[
            "expiry_date"
        ]
    )


    total_days = max(
        (
            expiry
            -
            purchase
        ).days,
        1
    )


    elapsed = max(
        (
            date.today()
            -
            purchase
        ).days,
        0
    )


    progress = (
        elapsed
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


# ============================================================
# DATAFRAME
# ============================================================

def create_dataframe():

    rows = []


    for item in (
        st.session_state
        .pantry_items
    ):

        (
            days_left,
            expiry_status,
            priority
        ) = expiry_info(
            item[
                "expiry_date"
            ]
        )


        rows.append(
            {
                "ID":
                    item[
                        "id"
                    ],

                "Food":
                    item[
                        "item_name"
                    ],

                "Category":
                    item[
                        "category"
                    ],

                "Quantity":
                    item[
                        "quantity"
                    ],

                "Unit":
                    item[
                        "unit"
                    ],

                "Purchase Date":
                    item[
                        "purchase_date"
                    ],

                "Expiry Date":
                    item[
                        "expiry_date"
                    ],

                "Days Left":
                    days_left,

                "Expiry Status":
                    expiry_status,

                "Priority":
                    priority,

                "Cost (RM)":
                    float(
                        item[
                            "cost"
                        ]
                    ),

                "Storage":
                    item[
                        "storage"
                    ],

                "Item Status":
                    item[
                        "item_status"
                    ],

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


# ============================================================
# UPDATE FOOD STATUS
# ============================================================

def mark_item(
    item_id,
    new_status
):

    for item in (
        st.session_state
        .pantry_items
    ):

        if (
            item[
                "id"
            ]
            ==
            item_id
        ):

            item[
                "item_status"
            ] = new_status


            item[
                "status_date"
            ] = str(
                date.today()
            )


            if (
                new_status
                ==
                "Consumed"
            ):

                add_activity(
                    f"✅ "
                    f"{item['item_name']} "
                    f"was consumed."
                )


            elif (
                new_status
                ==
                "Wasted"
            ):

                add_activity(
                    f"🗑️ "
                    f"{item['item_name']} "
                    f"was recorded as wasted."
                )


            break


# ============================================================
# DELETE FOOD
# ============================================================

def delete_item(
    item_id
):

    item_name = None


    for item in (
        st.session_state
        .pantry_items
    ):

        if (
            item[
                "id"
            ]
            ==
            item_id
        ):

            item_name = (
                item[
                    "item_name"
                ]
            )

            break


    st.session_state.pantry_items = [

        item

        for item
        in st.session_state.pantry_items

        if (
            item[
                "id"
            ]
            !=
            item_id
        )
    ]


    if item_name:

        add_activity(
            f"❌ "
            f"{item_name} "
            f"was removed from "
            f"the pantry."
        )


# ============================================================
# PANTRY HEALTH SCORE
# ============================================================

def pantry_health_score(
    df
):

    if df.empty:

        return (
            100,
            "Excellent"
        )


    available = df[
        df[
            "Item Status"
        ]
        ==
        "Available"
    ]


    urgent = len(
        available[
            (
                available[
                    "Days Left"
                ]
                >=
                0
            )
            &
            (
                available[
                    "Days Left"
                ]
                <=
                2
            )
        ]
    )


    expired = len(
        available[
            available[
                "Days Left"
            ]
            <
            0
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

        urgent
        *
        3

        -

        expired
        *
        5

        -

        wasted
        *
        2
    )


    score = max(
        0,
        min(
            score,
            100
        )
    )


    if score >= 90:

        label = (
            "Excellent"
        )


    elif score >= 75:

        label = (
            "Good"
        )


    elif score >= 50:

        label = (
            "Needs Attention"
        )


    else:

        label = (
            "High Waste Risk"
        )


    return (
        score,
        label
    )


# ============================================================
# CUSTOM METRIC CARD
# ============================================================

def metric_card(
    icon,
    label,
    value
):

    render_html(
        f"""
        <div class="sp-card">

            <div class="sp-card-icon">
                {icon}
            </div>

            <div class="sp-card-value">
                {value}
            </div>

            <div class="sp-card-label">
                {label}
            </div>

        </div>
        """
    )


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(
    kicker,
    title,
    subtitle
):

    render_html(
        f"""
        <div class="sp-page-kicker">
            {kicker}
        </div>

        <div class="sp-page-title">
            {title}
        </div>

        <div class="sp-page-subtitle">
            {subtitle}
        </div>
        """
    )


# ============================================================
# OLLAMA CLOUD CONFIG
# ============================================================

def ollama_configured():

    try:

        return bool(
            st.secrets[
                "OLLAMA_API_KEY"
            ]
        )

    except Exception:

        return False


# ============================================================
# GET OLLAMA MODEL
# ============================================================

def get_ollama_model():

    try:

        return st.secrets.get(
            "OLLAMA_MODEL",
            "gpt-oss:120b"
        )

    except Exception:

        return (
            "gpt-oss:120b"
        )


# ============================================================
# SMARTPANTRY AI BEHAVIOUR
# ============================================================

SMARTPANTRY_AI_SYSTEM = """
You are the SmartPantry Autonomous Meal Planning Engine.

You are not a general chatbot.

You operate only inside the SmartPantry food tracking system.

SMARTPANTRY ITSELF determines:

- expiry dates
- days remaining
- item lifecycle status
- storage location
- pantry cost
- whether an item is Available, Consumed, Wasted, or Expired

Treat those supplied values as authoritative.

YOUR JOB

You fully control meal planning for the CURRENT pantry situation.

You must independently decide:

1. the urgency of the pantry situation;
2. which usable foods should be prioritised;
3. how many meals are appropriate from 1 to 4;
4. which meals should be prepared first;
5. which pantry ingredients should be allocated to each meal;
6. which additional ingredients are actually necessary;
7. a short practical preparation plan;
8. the next best action for reducing avoidable food waste.

PRIORITY RULES

Priority 1:
Usable foods with 0 to 2 days remaining.

Priority 2:
Usable foods with 3 to 7 days remaining.

Priority 3:
Usable foods with 8 to 14 days remaining.

Priority 4:
Long-life fresh foods.

SYSTEM RULES

Never recommend an item marked:

- Consumed
- Wasted
- Expired

Never claim that a pantry ingredient exists if it is not present
in the supplied inventory.

You may recommend missing ingredients, but clearly classify them
as missing or optional ingredients.

Minimise unnecessary purchases.

Do not allocate a limited ingredient to several different meals
unless its available quantity reasonably supports that usage.

Prefer realistic, ordinary household meals.

Do not provide weight-loss, dieting, calorie-restriction,
or body-weight advice.

FOOD SAFETY

An expiry date alone does not prove food is safe.

For perishable foods, remind the user to check normal freshness,
appearance, smell and storage condition before preparation.

If SmartPantry says an item is expired, do not use it.

OUTPUT

Return ONLY valid JSON.

Do not use Markdown code fences.

Use exactly this structure:

{
  "situation_title": "short title",
  "situation_level": "Low | Moderate | High | Urgent",
  "situation_summary": "brief explanation",
  "planner_strategy": "brief explanation of what the planner prioritised",
  "meals": [
    {
      "meal_name": "name",
      "priority": "Cook today | Cook next | Flexible",
      "why_now": "why this meal is useful now",
      "pantry_ingredients": [
        "ingredient"
      ],
      "missing_ingredients": [
        "ingredient"
      ],
      "preparation": [
        "step",
        "step",
        "step"
      ],
      "food_safety_note": "short practical reminder"
    }
  ],
  "next_action": "single most useful next action"
}

Return JSON only.
"""


# ============================================================
# AI PANTRY CONTEXT
# ============================================================

def ai_pantry_context():

    df = create_dataframe()


    if df.empty:

        return []


    usable = df[
        (
            df[
                "Item Status"
            ]
            ==
            "Available"
        )
        &
        (
            df[
                "Days Left"
            ]
            >=
            0
        )
    ].sort_values(
        [
            "Days Left",
            "Priority"
        ],
        ascending=[
            True,
            False
        ]
    )


    context = []


    for _, row in (
        usable.iterrows()
    ):

        context.append(
            {
                "food":
                    row[
                        "Food"
                    ],

                "category":
                    row[
                        "Category"
                    ],

                "quantity":
                    row[
                        "Quantity"
                    ],

                "unit":
                    row[
                        "Unit"
                    ],

                "days_remaining":
                    int(
                        row[
                            "Days Left"
                        ]
                    ),

                "expiry_status":
                    row[
                        "Expiry Status"
                    ],

                "storage":
                    row[
                        "Storage"
                    ],

                "cost_rm":
                    round(
                        float(
                            row[
                                "Cost (RM)"
                            ]
                        ),
                        2
                    )
            }
        )


    return context


# ============================================================
# OLLAMA CLOUD REQUEST
# ============================================================

def call_ollama_cloud(
    user_prompt
):

    if not ollama_configured():

        return (
            None,
            (
                "Ollama Cloud is not configured. "
                "Add OLLAMA_API_KEY in "
                "Streamlit Secrets."
            )
        )


    try:

        response = requests.post(

            "https://ollama.com/api/chat",

            headers={
                "Authorization":
                    (
                        "Bearer "
                        +
                        st.secrets[
                            "OLLAMA_API_KEY"
                        ]
                    ),

                "Content-Type":
                    "application/json"
            },

            json={
                "model":
                    get_ollama_model(),

                "messages": [

                    {
                        "role":
                            "system",

                        "content":
                            SMARTPANTRY_AI_SYSTEM
                    },

                    {
                        "role":
                            "user",

                        "content":
                            user_prompt
                    }
                ],

                "stream":
                    False,

                "options": {
                    "temperature":
                        0.2
                }
            },

            timeout=90
        )


        response.raise_for_status()


        data = (
            response.json()
        )


        return (
            data[
                "message"
            ][
                "content"
            ],
            None
        )


    except requests.exceptions.Timeout:

        return (
            None,
            (
                "Ollama Cloud took too "
                "long to respond."
            )
        )


    except requests.exceptions.RequestException as error:

        return (
            None,
            (
                "Ollama Cloud request "
                f"failed: {error}"
            )
        )


    except Exception as error:

        return (
            None,
            (
                "Unable to read the "
                "Ollama response: "
                f"{error}"
            )
        )


# ============================================================
# AI JSON PARSER
# ============================================================

def parse_ai_json(
    text
):

    if not text:

        return None


    cleaned = (
        text.strip()
    )


    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE
    )


    cleaned = re.sub(
        r"```$",
        "",
        cleaned
    ).strip()


    try:

        return json.loads(
            cleaned
        )

    except Exception:

        pass


    start = (
        cleaned.find(
            "{"
        )
    )


    end = (
        cleaned.rfind(
            "}"
        )
    )


    if (
        start != -1
        and
        end != -1
        and
        end > start
    ):

        try:

            return json.loads(
                cleaned[
                    start:
                    end + 1
                ]
            )

        except Exception:

            return None


    return None


# ============================================================
# VALIDATE AI PLAN
# ============================================================

def validate_ai_plan(
    plan
):

    if not isinstance(
        plan,
        dict
    ):

        return None


    current_pantry = {

        item[
            "food"
        ].strip().lower()

        for item
        in ai_pantry_context()
    }


    meals = plan.get(
        "meals",
        []
    )


    if not isinstance(
        meals,
        list
    ):

        meals = []


    cleaned_meals = []


    for meal in meals[:4]:

        if not isinstance(
            meal,
            dict
        ):

            continue


        pantry_used = (
            meal.get(
                "pantry_ingredients",
                []
            )
        )


        missing = (
            meal.get(
                "missing_ingredients",
                []
            )
        )


        if not isinstance(
            pantry_used,
            list
        ):

            pantry_used = []


        if not isinstance(
            missing,
            list
        ):

            missing = []


        valid_used = []


        moved_to_missing = list(
            missing
        )


        for ingredient in (
            pantry_used
        ):

            ingredient_text = (
                str(
                    ingredient
                ).strip()
            )


            ingredient_lower = (
                ingredient_text.lower()
            )


            matches = [

                pantry_name

                for pantry_name
                in current_pantry

                if (
                    ingredient_lower
                    in
                    pantry_name
                    or
                    pantry_name
                    in
                    ingredient_lower
                )
            ]


            if matches:

                valid_used.append(
                    ingredient_text
                )


            else:

                if (
                    ingredient_text
                    not in
                    moved_to_missing
                ):

                    moved_to_missing.append(
                        ingredient_text
                    )


        cleaned_meals.append(
            {
                "meal_name":
                    str(
                        meal.get(
                            "meal_name",
                            "Meal"
                        )
                    ),

                "priority":
                    str(
                        meal.get(
                            "priority",
                            "Flexible"
                        )
                    ),

                "why_now":
                    str(
                        meal.get(
                            "why_now",
                            ""
                        )
                    ),

                "pantry_ingredients":
                    valid_used,

                "missing_ingredients":
                    moved_to_missing,

                "preparation":
                    (
                        meal.get(
                            "preparation",
                            []
                        )

                        if isinstance(
                            meal.get(
                                "preparation",
                                []
                            ),
                            list
                        )

                        else []
                    ),

                "food_safety_note":
                    str(
                        meal.get(
                            "food_safety_note",
                            ""
                        )
                    )
            }
        )


    return {
        "situation_title":
            str(
                plan.get(
                    "situation_title",
                    "Current Pantry Plan"
                )
            ),

        "situation_level":
            str(
                plan.get(
                    "situation_level",
                    "Moderate"
                )
            ),

        "situation_summary":
            str(
                plan.get(
                    "situation_summary",
                    ""
                )
            ),

        "planner_strategy":
            str(
                plan.get(
                    "planner_strategy",
                    ""
                )
            ),

        "meals":
            cleaned_meals,

        "next_action":
            str(
                plan.get(
                    "next_action",
                    (
                        "Review the highest-risk "
                        "foods first."
                    )
                )
            )
    }


# ============================================================
# AI SITUATION SIGNATURE
# ============================================================

def planner_signature():

    payload = {
        "date":
            str(
                date.today()
            ),

        "pantry":
            ai_pantry_context(),

        "preference":
            st.session_state[
                "planner_preference"
            ],

        "servings":
            st.session_state[
                "planner_servings"
            ],

        "time":
            st.session_state[
                "planner_time"
            ]
    }


    raw = json.dumps(
        payload,
        sort_keys=True
    )


    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# GENERATE AI PLAN
# ============================================================

def generate_ai_plan(
    reason,
    force=False
):

    pantry = (
        ai_pantry_context()
    )


    if not pantry:

        st.session_state[
            "ai_meal_plan"
        ] = None


        st.session_state[
            "ai_plan_error"
        ] = None


        st.session_state[
            "ai_plan_signature"
        ] = ""


        return False


    signature = (
        planner_signature()
    )


    if (
        not force
        and
        st.session_state[
            "ai_attempt_signature"
        ]
        ==
        signature
    ):

        return False


    st.session_state[
        "ai_attempt_signature"
    ] = signature


    prompt = f"""
SMARTPANTRY EVENT

{reason}

TODAY

{date.today()}

CURRENT USABLE PANTRY INVENTORY

{json.dumps(pantry, indent=2)}

USER PREFERENCES

Meal style:
{st.session_state["planner_preference"]}

Servings:
{st.session_state["planner_servings"]}

Preferred maximum preparation time:
{st.session_state["planner_time"]}

Treat this as a completely new pantry situation.

Autonomously decide:

- urgency
- ingredient priorities
- number of meals
- meal order
- ingredient allocation
- missing ingredients
- preparation strategy
- next action

Your main objective is to reduce avoidable household food waste.

Return only the required JSON.
"""


    (
        content,
        error
    ) = call_ollama_cloud(
        prompt
    )


    if error:

        st.session_state[
            "ai_plan_error"
        ] = error


        return False


    st.session_state[
        "ai_plan_raw"
    ] = content


    parsed = (
        parse_ai_json(
            content
        )
    )


    parsed = (
        validate_ai_plan(
            parsed
        )
    )


    if parsed is None:

        st.session_state[
            "ai_plan_error"
        ] = (
            "The AI responded, but "
            "SmartPantry could not read "
            "the meal-plan format."
        )


        return False


    st.session_state[
        "ai_meal_plan"
    ] = parsed


    st.session_state[
        "ai_plan_error"
    ] = None


    st.session_state[
        "ai_plan_signature"
    ] = signature


    st.session_state[
        "ai_last_updated"
    ] = datetime.now()


    add_activity(
        "🤖 AI Meal Planner adapted "
        "to the latest pantry situation."
    )


    return True


# ============================================================
# AUTOMATIC AI UPDATE
# ============================================================

def automatic_ai_update():

    if not (
        st.session_state[
            "auto_ai_planner"
        ]
    ):

        return


    if not (
        ollama_configured()
    ):

        return


    if not (
        ai_pantry_context()
    ):

        return


    current_signature = (
        planner_signature()
    )


    if (
        current_signature
        !=
        st.session_state[
            "ai_plan_signature"
        ]
        and
        current_signature
        !=
        st.session_state[
            "ai_attempt_signature"
        ]
    ):

        generate_ai_plan(
            (
                "SmartPantry detected a change "
                "in inventory, expiry timing, "
                "lifecycle status, date, or "
                "planner preferences."
            )
        )


# ============================================================
# DEMO DATA
# ============================================================

def load_demo_data():

    today = (
        date.today()
    )


    sample_data = [

        (
            "Fresh Milk",
            "Dairy",
            1,
            "Bottle",
            1,
            7.50,
            "Refrigerator"
        ),

        (
            "Chicken Breast",
            "Meat",
            1,
            "Pack",
            2,
            12.00,
            "Refrigerator"
        ),

        (
            "Eggs",
            "Dairy",
            8,
            "Piece",
            6,
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
            "Tomatoes",
            "Vegetables",
            4,
            "Piece",
            4,
            5.00,
            "Refrigerator"
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
            8,
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


        st.session_state[
            "pantry_items"
        ].append(
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
                    str(
                        today
                    ),

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
        "🧪 Demo pantry inventory loaded."
    )


    st.session_state[
        "ai_attempt_signature"
    ] = ""


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="sp-hero">

        <div class="sp-hero-badge">
            ✨ AI-POWERED PANTRY INTELLIGENCE
        </div>

        <div class="sp-hero-title">
            🥕 SmartPantry
        </div>

        <div class="sp-hero-subtitle">

            Track food lifecycles,
            identify expiry risk,
            reduce avoidable waste,
            and let an autonomous
            Ollama Cloud meal planner
            continuously adapt to your
            current pantry situation.

        </div>

    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:


    render_html(
        """
        <div class="sp-side-brand">

            <div class="sp-side-brand-row">

                <div class="sp-side-logo">
                    🥕
                </div>

                <div>

                    <div class="sp-side-name">
                        SmartPantry
                    </div>

                    <div class="sp-side-sub">
                        AI Food Intelligence
                    </div>

                </div>

            </div>

            <div class="sp-side-live">
                ● LIVE TRACKING SYSTEM
            </div>

        </div>
        """
    )


    render_html(
        """
        <div class="sp-side-label">
            Navigation
        </div>
        """
    )


    page = st.radio(

        "Navigation",

        [
            "🏠 Overview",
            "📍 Food Tracker",
            "➕ Add Item",
            "📅 Expiry Timeline",
            "✨ AI Meal Planner",
            "📊 Insights"
        ],

        label_visibility=
            "collapsed"
    )


    render_html(
        """
        <div class="sp-side-label">
            Intelligence
        </div>
        """
    )


    with st.container(
        border=True
    ):


        st.toggle(
            "🤖 Automatic AI Planning",
            key="auto_ai_planner"
        )


        if (
            st.session_state[
                "auto_ai_planner"
            ]
        ):

            st.caption(
                "Adapts when pantry or "
                "expiry conditions change."
            )


        else:

            st.caption(
                "Automatic replanning "
                "is paused."
            )


    if (
        ollama_configured()
    ):


        render_html(
            f"""
            <div class="sp-side-ai">

                <div class="sp-side-ai-row">

                    <div class="sp-side-ai-title">
                        Ollama Cloud
                    </div>

                    <div class="sp-side-dot">
                    </div>

                </div>

                <div class="sp-side-muted">

                    Connected •
                    {get_ollama_model()}

                </div>

            </div>
            """
        )


    else:


        render_html(
            """
            <div class="sp-side-ai">

                <div class="sp-side-ai-row">

                    <div class="sp-side-ai-title">
                        Ollama Cloud
                    </div>

                </div>

                <div class="sp-side-muted">
                    ⚠ Not configured
                </div>

            </div>
            """
        )


    sidebar_df = (
        create_dataframe()
    )


    if not sidebar_df.empty:


        sidebar_available = (
            sidebar_df[
                sidebar_df[
                    "Item Status"
                ]
                ==
                "Available"
            ]
        )


        sidebar_risk = (
            sidebar_available[
                (
                    sidebar_available[
                        "Days Left"
                    ]
                    >=
                    0
                )
                &
                (
                    sidebar_available[
                        "Days Left"
                    ]
                    <=
                    7
                )
            ]
        )


        render_html(
            """
            <div class="sp-side-label">
                Pantry Status
            </div>
            """
        )


        side_a, side_b = (
            st.columns(2)
        )


        side_a.metric(
            "Items",
            len(
                sidebar_available
            )
        )


        side_b.metric(
            "Risk",
            len(
                sidebar_risk
            )
        )


    if not (
        st.session_state[
            "pantry_items"
        ]
    ):


        st.divider()


        if st.button(

            "🧪 Load Demo Pantry",

            use_container_width=True
        ):


            load_demo_data()


            st.session_state[
                "flash_message"
            ] = (
                "Demo pantry loaded."
            )


            st.rerun()


    render_html(
        """
        <div class="sp-side-footer">

            SmartPantry Intelligence System

            <br>

            AI-assisted food waste reduction

        </div>
        """
    )


# ============================================================
# FLASH MESSAGE
# ============================================================

if (
    st.session_state[
        "flash_message"
    ]
):


    st.toast(
        st.session_state[
            "flash_message"
        ]
    )


    st.session_state[
        "flash_message"
    ] = ""


# ============================================================
# AUTOMATIC AI PLANNING
# ============================================================

automatic_ai_update()


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":


    page_header(

        "Today",

        "Good to see you 👋",

        (
            "Here is what is happening "
            "inside your pantry right now."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "Your pantry is empty. "
            "Add your first item or "
            "load the demo pantry."
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


        attention = (
            available[
                (
                    available[
                        "Days Left"
                    ]
                    >=
                    0
                )
                &
                (
                    available[
                        "Days Left"
                    ]
                    <=
                    7
                )
            ]
            .sort_values(
                "Days Left"
            )
        )


        pantry_value = (
            available[
                "Cost (RM)"
            ].sum()
        )


        risk_value = (
            attention[
                "Cost (RM)"
            ].sum()
        )


        saved_value = (
            consumed[
                "Cost (RM)"
            ].sum()
        )


        (
            health,
            health_label
        ) = pantry_health_score(
            df
        )


        health_col, risk_col = (
            st.columns(
                [
                    2,
                    1
                ]
            )
        )


        with health_col:


            st.markdown(
                "### 🌿 Pantry Health Score"
            )


            st.progress(
                health
                /
                100
            )


            st.markdown(
                f"## "
                f"{health}/100 "
                f"— "
                f"{health_label}"
            )


            st.caption(
                "Based on expiry risk, "
                "food usage and recorded waste."
            )


        with risk_col:


            with st.container(
                border=True
            ):


                st.markdown(
                    "#### ⚠️ Current Risk"
                )


                st.metric(
                    "Value at Risk",
                    (
                        f"RM "
                        f"{risk_value:.2f}"
                    )
                )


                st.caption(
                    f"{len(attention)} "
                    f"item(s) expire "
                    f"within 7 days."
                )


        st.divider()


        c1, c2, c3, c4 = (
            st.columns(4)
        )


        with c1:

            metric_card(
                "🥫",
                "Available Items",
                len(
                    available
                )
            )


        with c2:

            metric_card(
                "🚨",
                "Need Attention",
                len(
                    attention
                )
            )


        with c3:

            metric_card(
                "🌱",
                "Food Saved",
                len(
                    consumed
                )
            )


        with c4:

            metric_card(
                "💚",
                "Value Saved",
                (
                    f"RM "
                    f"{saved_value:.2f}"
                )
            )


        st.divider()


        st.markdown(
            "### 🚨 Needs Attention"
        )


        if attention.empty:


            st.success(
                "Nothing currently requires "
                "urgent attention."
            )


        else:


            for _, row in (
                attention
                .head(5)
                .iterrows()
            ):


                with st.container(
                    border=True
                ):


                    left, middle, right = (
                        st.columns(
                            [
                                3,
                                2,
                                1
                            ]
                        )
                    )


                    with left:


                        st.markdown(
                            f"#### "
                            f"{row['Food']}"
                        )


                        render_html(
                            status_html(
                                row[
                                    "Expiry Status"
                                ]
                            )
                        )


                    with middle:


                        st.write(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )


                        st.caption(
                            f"{row['Quantity']} "
                            f"{row['Unit']} "
                            f"• "
                            f"{row['Storage']}"
                        )


                    with right:


                        st.metric(
                            "Value",
                            (
                                f"RM "
                                f"{row['Cost (RM)']:.2f}"
                            )
                        )


        st.divider()


        render_html(
            """
            <div class="sp-ai-banner">

                <div class="sp-ai-title">
                    🤖 Autonomous Meal Planner
                </div>

                <div class="sp-ai-subtitle">

                    SmartPantry AI automatically
                    rebuilds its meal strategy when
                    your usable inventory,
                    expiry timing,
                    lifecycle status,
                    date,
                    or planner preferences change.

                </div>

            </div>
            """
        )


        if (
            st.session_state[
                "ai_meal_plan"
            ]
        ):


            plan = (
                st.session_state[
                    "ai_meal_plan"
                ]
            )


            st.markdown(
                f"### "
                f"{plan.get('situation_title', 'Current Meal Strategy')}"
            )


            st.write(
                "**Situation level:** "
                +
                plan.get(
                    "situation_level",
                    "Moderate"
                )
            )


            st.write(
                plan.get(
                    "situation_summary",
                    ""
                )
            )


            st.info(
                plan.get(
                    "planner_strategy",
                    ""
                )
            )


            meals = (
                plan.get(
                    "meals",
                    []
                )
            )


            st.caption(
                f"AI currently recommends "
                f"{len(meals)} meal(s)."
            )


        elif (
            st.session_state[
                "ai_plan_error"
            ]
        ):


            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )


        else:


            st.caption(
                "No AI meal plan "
                "is available yet."
            )


        st.divider()


        st.markdown(
            "### 🕘 Recent Activity"
        )


        if not (
            st.session_state[
                "activity_log"
            ]
        ):


            st.caption(
                "No tracked activity yet."
            )


        else:


            for event in (
                st.session_state[
                    "activity_log"
                ][:6]
            ):


                st.write(
                    f"**"
                    f"{event['time']}"
                    f"**"
                )


                st.caption(
                    event[
                        "message"
                    ]
                )


# ============================================================
# FOOD TRACKER
# ============================================================

elif page == "📍 Food Tracker":


    page_header(

        "Lifecycle Tracking",

        "Food Tracker",

        (
            "Follow each pantry item "
            "from entry until consumption "
            "or waste."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "There are no pantry items yet."
        )


    else:


        f1, f2, f3 = (
            st.columns(3)
        )


        search = (
            f1.text_input(
                "🔍 Search food"
            )
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


        lifecycle_filter = (
            f3.selectbox(

                "Lifecycle",

                [
                    "All",
                    "Available",
                    "Consumed",
                    "Wasted"
                ]
            )
        )


        filtered = (
            df.copy()
        )


        if search:


            filtered = filtered[
                filtered[
                    "Food"
                ]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]


        if (
            category_filter
            !=
            "All"
        ):


            filtered = filtered[
                filtered[
                    "Category"
                ]
                ==
                category_filter
            ]


        if (
            lifecycle_filter
            !=
            "All"
        ):


            filtered = filtered[
                filtered[
                    "Item Status"
                ]
                ==
                lifecycle_filter
            ]


        filtered = (
            filtered
            .sort_values(
                [
                    "Item Status",
                    "Days Left"
                ]
            )
        )


        for _, row in (
            filtered.iterrows()
        ):


            source_item = next(

                item

                for item
                in st.session_state[
                    "pantry_items"
                ]

                if (
                    item[
                        "id"
                    ]
                    ==
                    row[
                        "ID"
                    ]
                )
            )


            with st.container(
                border=True
            ):


                (
                    title_col,
                    qty_col
                ) = st.columns(
                    [
                        4,
                        1
                    ]
                )


                with title_col:


                    st.markdown(
                        f"### "
                        f"{row['Food']}"
                    )


                    if (
                        row[
                            "Item Status"
                        ]
                        ==
                        "Available"
                    ):


                        render_html(
                            status_html(
                                row[
                                    "Expiry Status"
                                ]
                            )
                        )


                    else:


                        st.markdown(
                            f"**"
                            f"{row['Item Status']}"
                            f"**"
                        )


                    st.caption(
                        f"{row['Category']} "
                        f"• "
                        f"{row['Storage']} "
                        f"• "
                        f"RM "
                        f"{row['Cost (RM)']:.2f}"
                    )


                with qty_col:


                    st.metric(
                        "Quantity",
                        (
                            f"{row['Quantity']} "
                            f"{row['Unit']}"
                        )
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
                            source_item
                        )
                    )


                    st.caption(
                        "Shelf-life tracking"
                    )


                    st.progress(
                        progress
                    )


                    p1, p2, p3 = (
                        st.columns(3)
                    )


                    p1.caption(
                        f"Purchased\n"
                        f"{row['Purchase Date']}"
                    )


                    p2.caption(
                        f"{progress * 100:.0f}% "
                        f"of tracked shelf life passed"
                    )


                    p3.caption(
                        expiry_message(
                            row[
                                "Days Left"
                            ]
                        )
                    )


                    b1, b2, b3 = (
                        st.columns(3)
                    )


                    if b1.button(

                        "✅ Mark Consumed",

                        key=
                            (
                                f"consume_"
                                f"{row['ID']}"
                            ),

                        use_container_width=True
                    ):


                        mark_item(
                            row[
                                "ID"
                            ],
                            "Consumed"
                        )


                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""


                        st.session_state[
                            "flash_message"
                        ] = (
                            f"{row['Food']} "
                            f"marked as consumed."
                        )


                        st.rerun()


                    if b2.button(

                        "🗑️ Mark Wasted",

                        key=
                            (
                                f"waste_"
                                f"{row['ID']}"
                            ),

                        use_container_width=True
                    ):


                        mark_item(
                            row[
                                "ID"
                            ],
                            "Wasted"
                        )


                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""


                        st.session_state[
                            "flash_message"
                        ] = (
                            f"{row['Food']} "
                            f"marked as wasted."
                        )


                        st.rerun()


                    if b3.button(

                        "❌ Delete",

                        key=
                            (
                                f"delete_"
                                f"{row['ID']}"
                            ),

                        use_container_width=True
                    ):


                        delete_item(
                            row[
                                "ID"
                            ]
                        )


                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""


                        st.session_state[
                            "flash_message"
                        ] = (
                            f"{row['Food']} "
                            f"deleted."
                        )


                        st.rerun()


# ============================================================
# ADD ITEM
# ============================================================

elif page == "➕ Add Item":


    page_header(

        "Pantry Entry",

        "Add a Food Item",

        (
            "Start tracking a new item "
            "and immediately include it "
            "in SmartPantry intelligence."
        )
    )


    with st.container(
        border=True
    ):


        with st.form(
            "add_food",
            clear_on_submit=True
        ):


            left, right = (
                st.columns(2)
            )


            with left:


                food_name = (
                    st.text_input(
                        "Food Name *",
                        placeholder=
                            "Example: Fresh Milk"
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
                        value=
                            date.today()
                    )
                )


                expiry_date = (
                    st.date_input(
                        "Expiry Date",
                        value=
                            (
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
                        step=0.50,
                        format="%.2f"
                    )
                )


                storage = (
                    st.selectbox(
                        "Storage Location",
                        STORAGE_LOCATIONS
                    )
                )


            submit = (
                st.form_submit_button(
                    "➕ Add to SmartPantry",
                    use_container_width=True
                )
            )


            if submit:


                if not (
                    food_name.strip()
                ):


                    st.error(
                        "Please enter a food name."
                    )


                elif (
                    expiry_date
                    <
                    purchase_date
                ):


                    st.error(
                        "Expiry date cannot "
                        "be earlier than the "
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
                            int(
                                quantity
                            ),

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
                            float(
                                cost
                            ),

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
                        item
                    )


                    add_activity(
                        f"➕ "
                        f"{food_name.strip()} "
                        f"was added to "
                        f"the pantry."
                    )


                    st.session_state[
                        "ai_attempt_signature"
                    ] = ""


                    st.session_state[
                        "flash_message"
                    ] = (
                        f"{food_name.strip()} "
                        f"added. SmartPantry "
                        f"will re-evaluate "
                        f"the meal plan."
                    )


                    st.rerun()


# ============================================================
# EXPIRY TIMELINE
# ============================================================

elif page == "📅 Expiry Timeline":


    page_header(

        "Expiry Tracking",

        "Expiry Timeline",

        (
            "See what needs attention "
            "today, tomorrow, this week, "
            "and later."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "No food is currently "
            "being tracked."
        )


    else:


        available = (
            df[
                df[
                    "Item Status"
                ]
                ==
                "Available"
            ]
            .sort_values(
                "Days Left"
            )
        )


        groups = [

            (
                "⚫ Expired",

                available[
                    available[
                        "Days Left"
                    ]
                    <
                    0
                ]
            ),

            (
                "🔴 Today",

                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    0
                ]
            ),

            (
                "🟠 Tomorrow",

                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    1
                ]
            ),

            (
                "🟡 Next 7 Days",

                available[
                    (
                        available[
                            "Days Left"
                        ]
                        >=
                        2
                    )
                    &
                    (
                        available[
                            "Days Left"
                        ]
                        <=
                        7
                    )
                ]
            ),

            (
                "🟢 Later",

                available[
                    available[
                        "Days Left"
                    ]
                    >
                    7
                ]
            )
        ]


        for (
            title,
            group
        ) in groups:


            st.markdown(
                f"### "
                f"{title}"
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


                        c1, c2, c3 = (
                            st.columns(
                                [
                                    3,
                                    2,
                                    1
                                ]
                            )
                        )


                        with c1:


                            st.markdown(
                                f"**"
                                f"{row['Food']}"
                                f"**"
                            )


                            st.caption(
                                f"{row['Category']} "
                                f"• "
                                f"{row['Storage']}"
                            )


                        c2.write(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )


                        c3.write(
                            f"{row['Quantity']} "
                            f"{row['Unit']}"
                        )


# ============================================================
# AI MEAL PLANNER
# ============================================================

elif page == "✨ AI Meal Planner":


    page_header(

        "Ollama Cloud Intelligence",

        "Autonomous AI Meal Planner",

        (
            "The AI decides what to cook, "
            "what to prioritise, and how "
            "the plan should change as "
            "your pantry changes."
        )
    )


    render_html(
        """
        <div class="sp-ai-banner">

            <div class="sp-ai-title">
                ✨ Fully AI-Controlled Meal Strategy
            </div>

            <div class="sp-ai-subtitle">

                SmartPantry provides verified
                tracking data.

                Ollama Cloud decides the situation
                level, meal count, meal order,
                ingredient allocation,
                missing ingredients,
                and next best action.

            </div>

        </div>
        """
    )


    with st.expander(
        "⚙️ Planner Preferences"
    ):


        with st.form(
            "planner_preferences"
        ):


            preference = (
                st.text_input(

                    "Meal Preference",

                    value=
                        st.session_state[
                            "planner_preference"
                        ],

                    placeholder=
                        (
                            "Example: "
                            "quick everyday meals"
                        )
                )
            )


            servings = (
                st.number_input(

                    "Servings",

                    min_value=1,

                    max_value=8,

                    value=
                        st.session_state[
                            "planner_servings"
                        ]
                )
            )


            time_options = [

                "15 minutes",

                "30 minutes",

                "45 minutes",

                "60 minutes"
            ]


            if (
                st.session_state[
                    "planner_time"
                ]
                in
                time_options
            ):


                current_index = (
                    time_options.index(
                        st.session_state[
                            "planner_time"
                        ]
                    )
                )


            else:


                current_index = 1


            time_limit = (
                st.selectbox(

                    "Preferred Maximum Time",

                    time_options,

                    index=
                        current_index
                )
            )


            save_settings = (
                st.form_submit_button(

                    "Save & Recalculate Plan",

                    use_container_width=True
                )
            )


            if save_settings:


                st.session_state[
                    "planner_preference"
                ] = (
                    preference.strip()
                    or
                    "Practical everyday meals"
                )


                st.session_state[
                    "planner_servings"
                ] = int(
                    servings
                )


                st.session_state[
                    "planner_time"
                ] = (
                    time_limit
                )


                st.session_state[
                    "ai_attempt_signature"
                ] = ""


                add_activity(
                    "⚙️ AI meal-planner "
                    "preferences were updated."
                )


                st.session_state[
                    "flash_message"
                ] = (
                    "Planner preferences updated."
                )


                st.rerun()


    pantry = (
        ai_pantry_context()
    )


    if not pantry:


        st.warning(
            "There are no usable, "
            "non-expired pantry items "
            "for meal planning."
        )


    else:


        top1, top2 = (
            st.columns(
                [
                    1,
                    2
                ]
            )
        )


        with top1:


            if st.button(

                "🔄 Re-plan Now",

                use_container_width=True
            ):


                with st.spinner(
                    "Ollama Cloud is analysing "
                    "your latest pantry situation..."
                ):


                    generate_ai_plan(

                        (
                            "The user manually requested "
                            "a fresh evaluation of the "
                            "current pantry."
                        ),

                        force=True
                    )


                st.rerun()


        with top2:


            if (
                st.session_state[
                    "ai_last_updated"
                ]
            ):


                st.info(
                    "Last AI adaptation: "
                    +
                    st.session_state[
                        "ai_last_updated"
                    ].strftime(
                        "%d %b %Y • %H:%M"
                    )
                )


            else:


                st.info(
                    f"AI can analyse "
                    f"{len(pantry)} "
                    f"usable pantry item(s)."
                )


        if (
            st.session_state[
                "ai_plan_error"
            ]
        ):


            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )


            if (
                st.session_state[
                    "ai_plan_raw"
                ]
            ):


                with st.expander(
                    "Technical response "
                    "for troubleshooting"
                ):


                    st.code(
                        st.session_state[
                            "ai_plan_raw"
                        ]
                    )


        plan = (
            st.session_state[
                "ai_meal_plan"
            ]
        )


        if plan:


            st.divider()


            plan_a, plan_b = (
                st.columns(
                    [
                        1,
                        2
                    ]
                )
            )


            with plan_a:


                st.markdown(
                    "#### Situation Level"
                )


                st.metric(
                    "AI Assessment",
                    plan.get(
                        "situation_level",
                        "Moderate"
                    )
                )


            with plan_b:


                st.markdown(
                    "#### "
                    +
                    plan.get(
                        "situation_title",
                        (
                            "Current Pantry "
                            "Strategy"
                        )
                    )
                )


                st.write(
                    plan.get(
                        "situation_summary",
                        ""
                    )
                )


            st.info(
                "🎯 "
                +
                plan.get(
                    "planner_strategy",
                    ""
                )
            )


            meals = (
                plan.get(
                    "meals",
                    []
                )
            )


            st.markdown(
                f"### 🍽️ AI Selected "
                f"{len(meals)} Meal(s)"
            )


            for (
                index,
                meal
            ) in enumerate(
                meals,
                start=1
            ):


                with st.container(
                    border=True
                ):


                    (
                        title_col,
                        priority_col
                    ) = st.columns(
                        [
                            4,
                            1
                        ]
                    )


                    with title_col:


                        st.markdown(
                            f"### "
                            f"{index}. "
                            f"{meal.get('meal_name', 'Meal')}"
                        )


                    with priority_col:


                        st.caption(
                            "PRIORITY"
                        )


                        st.write(
                            f"**"
                            f"{meal.get('priority', 'Flexible')}"
                            f"**"
                        )


                    st.write(
                        "**Why SmartPantry chose this**"
                    )


                    st.write(
                        meal.get(
                            "why_now",
                            ""
                        )
                    )


                    ingredient_col, missing_col = (
                        st.columns(2)
                    )


                    with ingredient_col:


                        st.markdown(
                            "#### 🥕 Pantry Items Used"
                        )


                        ingredients = (
                            meal.get(
                                "pantry_ingredients",
                                []
                            )
                        )


                        if ingredients:


                            for ingredient in (
                                ingredients
                            ):


                                st.write(
                                    f"✓ "
                                    f"{ingredient}"
                                )


                        else:


                            st.caption(
                                "No pantry ingredients listed."
                            )


                    with missing_col:


                        st.markdown(
                            "#### 🛒 Missing / Optional"
                        )


                        missing = (
                            meal.get(
                                "missing_ingredients",
                                []
                            )
                        )


                        if missing:


                            for ingredient in missing:


                                st.write(
                                    f"• "
                                    f"{ingredient}"
                                )


                        else:


                            st.success(
                                "No extra ingredients needed."
                            )


                    preparation = (
                        meal.get(
                            "preparation",
                            []
                        )
                    )


                    if preparation:


                        with st.expander(
                            "👨‍🍳 Preparation Plan"
                        ):


                            for (
                                number,
                                step
                            ) in enumerate(
                                preparation,
                                start=1
                            ):


                                st.write(
                                    f"{number}. "
                                    f"{step}"
                                )


                    if (
                        meal.get(
                            "food_safety_note"
                        )
                    ):


                        st.caption(
                            "Food safety: "
                            +
                            meal.get(
                                "food_safety_note",
                                ""
                            )
                        )


            st.divider()


            st.success(
                "✅ **SmartPantry Next Action:** "
                +
                plan.get(
                    "next_action",
                    (
                        "Review your "
                        "priority foods."
                    )
                )
            )


        elif not (
            st.session_state[
                "ai_plan_error"
            ]
        ):


            st.info(
                "No AI plan has been "
                "generated yet. "
                "Select **Re-plan Now**."
            )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "📊 Insights":


    page_header(

        "Performance Tracking",

        "Pantry Insights",

        (
            "Measure food saved, "
            "money protected, waste outcomes, "
            "and current pantry composition."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "Add pantry data before "
            "viewing insights."
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


        completed = (
            len(
                consumed
            )
            +
            len(
                wasted
            )
        )


        if completed:


            avoidance_rate = (
                len(
                    consumed
                )
                /
                completed
                *
                100
            )


        else:


            avoidance_rate = 0


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


        c1, c2, c3, c4 = (
            st.columns(4)
        )


        with c1:


            metric_card(
                "🌱",
                "Food Saved",
                len(
                    consumed
                )
            )


        with c2:


            metric_card(
                "💚",
                "Value Saved",
                (
                    f"RM "
                    f"{value_saved:.2f}"
                )
            )


        with c3:


            metric_card(
                "🗑️",
                "Waste Cost",
                (
                    f"RM "
                    f"{waste_cost:.2f}"
                )
            )


        with c4:


            metric_card(
                "📈",
                "Waste Avoidance",
                (
                    f"{avoidance_rate:.1f}%"
                )
            )


        st.divider()


        if completed:


            outcome_df = (
                pd.DataFrame(
                    {
                        "Outcome":
                            [
                                "Consumed",
                                "Wasted"
                            ],

                        "Items":
                            [
                                len(
                                    consumed
                                ),

                                len(
                                    wasted
                                )
                            ]
                    }
                )
            )


            figure = (
                px.pie(

                    outcome_df,

                    names="Outcome",

                    values="Items",

                    hole=0.48,

                    title=
                        "Food Lifecycle Outcomes"
                )
            )


            st.plotly_chart(
                figure,
                use_container_width=True
            )


        if not available.empty:


            category_df = (

                available
                .groupby(
                    "Category"
                )
                .agg(
                    Items=
                        (
                            "Food",
                            "count"
                        ),

                    Value=
                        (
                            "Cost (RM)",
                            "sum"
                        )
                )
                .reset_index()
            )


            category_figure = (
                px.bar(

                    category_df,

                    x="Category",

                    y="Items",

                    title=
                        (
                            "Available Pantry "
                            "by Category"
                        )
                )
            )


            st.plotly_chart(
                category_figure,
                use_container_width=True
            )


        st.divider()


        st.markdown(
            "### 💾 Data Backup"
        )


        backup_df = (
            pd.DataFrame(
                st.session_state[
                    "pantry_items"
                ]
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

            data=
                backup_csv,

            file_name=
                "smartpantry_backup.csv",

            mime=
                "text/csv"
        )


        uploaded = (
            st.file_uploader(

                "Restore SmartPantry Backup",

                type=[
                    "csv"
                ]
            )
        )


        if (
            uploaded
            is not None
        ):


            try:


                restored = (
                    pd.read_csv(
                        uploaded
                    )
                )


                required = {

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
                    required.issubset(
                        set(
                            restored.columns
                        )
                    )
                ):


                    st.error(
                        "This file is not "
                        "a valid SmartPantry backup."
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


                            record.setdefault(
                                "status_date",
                                ""
                            )


                        st.session_state[
                            "pantry_items"
                        ] = records


                        st.session_state[
                            "ai_plan_signature"
                        ] = ""


                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""


                        add_activity(
                            "♻️ Pantry backup restored."
                        )


                        st.session_state[
                            "flash_message"
                        ] = (
                            "Pantry backup restored."
                        )


                        st.rerun()


            except Exception as error:


                st.error(
                    "Unable to restore "
                    f"the backup: {error}"
                )
