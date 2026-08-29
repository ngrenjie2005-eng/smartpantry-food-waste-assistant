import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import uuid
import json
import hashlib
import re

from datetime import date, datetime, timedelta


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SmartPantry",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEME-AWARE WEBSITE CSS
#
# IMPORTANT:
# Uses Streamlit theme variables.
# This allows the interface to automatically adapt
# when Streamlit changes between light and dark themes.
# ============================================================

CUSTOM_CSS = """
<style>

/* =========================================================
   SMARTPANTRY THEME VARIABLES
   ========================================================= */

:root {

    --sp-bg:
        var(--background-color);

    --sp-surface:
        var(--secondary-background-color);

    --sp-text:
        var(--text-color);

    --sp-primary:
        var(--primary-color);

    --sp-border:
        color-mix(
            in srgb,
            var(--text-color) 14%,
            transparent
        );

    --sp-muted:
        color-mix(
            in srgb,
            var(--text-color) 62%,
            transparent
        );

    --sp-soft:
        color-mix(
            in srgb,
            var(--secondary-background-color) 85%,
            var(--background-color)
        );

    --sp-hover:
        color-mix(
            in srgb,
            var(--primary-color) 10%,
            var(--secondary-background-color)
        );

    --sp-primary-soft:
        color-mix(
            in srgb,
            var(--primary-color) 16%,
            var(--secondary-background-color)
        );

    --sp-primary-medium:
        color-mix(
            in srgb,
            var(--primary-color) 35%,
            var(--secondary-background-color)
        );
}


/* =========================================================
   GLOBAL
   ========================================================= */

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


.block-container {

    max-width: 1280px;

    padding-top: 1.4rem;

    padding-bottom: 4rem;
}


/* =========================================================
   HERO
   ========================================================= */

.sp-hero {

    position: relative;

    overflow: hidden;

    padding: 38px 42px;

    margin-bottom: 28px;

    border-radius: 26px;

    background:
        linear-gradient(
            135deg,
            #174b35 0%,
            #2d7250 52%,
            #70a57f 100%
        );

    box-shadow:
        0 16px 42px
        rgba(0, 0, 0, 0.16);

    color: white;
}


.sp-hero::before {

    content: "";

    position: absolute;

    width: 310px;

    height: 310px;

    border-radius: 50%;

    right: -110px;

    top: -150px;

    background:
        rgba(255,255,255,0.08);
}


.sp-hero::after {

    content: "";

    position: absolute;

    width: 160px;

    height: 160px;

    border-radius: 50%;

    right: 180px;

    bottom: -110px;

    background:
        rgba(255,255,255,0.05);
}


.sp-hero-badge {

    display: inline-flex;

    align-items: center;

    gap: 6px;

    padding: 6px 11px;

    margin-bottom: 14px;

    border-radius: 999px;

    border:
        1px solid
        rgba(255,255,255,0.20);

    background:
        rgba(255,255,255,0.10);

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 0.7px;
}


.sp-hero-title {

    position: relative;

    z-index: 2;

    font-size: 43px;

    font-weight: 850;

    letter-spacing: -1px;

    line-height: 1.05;

    margin-bottom: 9px;
}


.sp-hero-subtitle {

    position: relative;

    z-index: 2;

    max-width: 720px;

    font-size: 16px;

    line-height: 1.62;

    color:
        rgba(255,255,255,0.88);
}


/* =========================================================
   PAGE TITLE
   ========================================================= */

.sp-kicker {

    color:
        var(--sp-muted);

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.2px;

    text-transform: uppercase;

    margin-bottom: 4px;
}


.sp-page-title {

    color:
        var(--sp-text);

    font-size: 30px;

    line-height: 1.2;

    font-weight: 850;

    letter-spacing: -0.6px;

    margin-bottom: 5px;
}


.sp-page-description {

    color:
        var(--sp-muted);

    font-size: 14px;

    line-height: 1.55;

    margin-bottom: 22px;
}


/* =========================================================
   CUSTOM KPI CARD
   ========================================================= */

.sp-metric-card {

    min-height: 133px;

    padding: 20px;

    border-radius: 19px;

    border:
        1px solid
        var(--sp-border);

    background:
        var(--sp-surface);

    box-shadow:
        0 8px 28px
        rgba(0,0,0,0.055);

    transition:
        transform .18s ease,
        border-color .18s ease,
        box-shadow .18s ease;
}


.sp-metric-card:hover {

    transform:
        translateY(-3px);

    border-color:
        color-mix(
            in srgb,
            var(--sp-primary) 45%,
            var(--sp-border)
        );

    box-shadow:
        0 12px 32px
        rgba(0,0,0,0.09);
}


.sp-metric-icon {

    font-size: 25px;

    margin-bottom: 10px;
}


.sp-metric-value {

    color:
        var(--sp-text);

    font-size: 27px;

    line-height: 1.15;

    font-weight: 850;

    letter-spacing: -0.4px;

    margin-bottom: 6px;
}


.sp-metric-label {

    color:
        var(--sp-muted);

    font-size: 13px;

    font-weight: 600;
}


/* =========================================================
   AI PANEL
   ========================================================= */

.sp-ai-panel {

    padding: 21px 23px;

    margin:
        10px 0 19px 0;

    border-radius: 19px;

    border:
        1px solid
        color-mix(
            in srgb,
            var(--sp-primary) 30%,
            var(--sp-border)
        );

    background:
        var(--sp-primary-soft);
}


.sp-ai-title {

    color:
        var(--sp-text);

    font-size: 19px;

    font-weight: 850;

    margin-bottom: 5px;
}


.sp-ai-description {

    color:
        var(--sp-muted);

    font-size: 13px;

    line-height: 1.55;
}


/* =========================================================
   STATUS PILLS
   ========================================================= */

.sp-status {

    display: inline-block;

    padding:
        5px 10px;

    border-radius:
        999px;

    font-size:
        11px;

    font-weight:
        800;
}


.sp-fresh {

    color: #166534;

    background: #dcfce7;
}


.sp-use {

    color: #854d0e;

    background: #fef9c3;
}


.sp-soon {

    color: #9a3412;

    background: #ffedd5;
}


.sp-urgent {

    color: #991b1b;

    background: #fee2e2;
}


.sp-expired {

    color: #374151;

    background: #e5e7eb;
}


/* =========================================================
   STREAMLIT CONTAINERS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {

    border-radius: 18px !important;

    border-color:
        var(--sp-border) !important;
}


div[data-testid="stMetric"] {

    border-radius: 15px;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {

    border-radius: 11px;

    font-weight: 650;

    transition:
        all .16s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 6px 20px
        rgba(0,0,0,0.10);
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        color-mix(
            in srgb,
            var(--secondary-background-color) 94%,
            var(--background-color)
        );

    border-right:
        1px solid
        var(--sp-border);
}


section[data-testid="stSidebar"]
div[data-testid="stSidebarContent"] {

    padding-top: 0.45rem;
}


/* =========================================================
   SIDEBAR BRAND
   ========================================================= */

.sp-sidebar-brand {

    padding: 16px;

    margin:
        3px 2px 17px 2px;

    border-radius: 18px;

    border:
        1px solid
        var(--sp-border);

    background:
        linear-gradient(
            135deg,
            var(--sp-primary-soft),
            var(--sp-surface)
        );
}


.sp-sidebar-brand-row {

    display: flex;

    align-items: center;

    gap: 11px;
}


.sp-sidebar-logo {

    width: 43px;

    height: 43px;

    flex-shrink: 0;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 13px;

    font-size: 22px;

    background:
        linear-gradient(
            135deg,
            #5a9a73,
            #2f704f
        );

    box-shadow:
        0 7px 20px
        rgba(0,0,0,0.18);
}


.sp-sidebar-name {

    color:
        var(--sp-text);

    font-size: 18px;

    font-weight: 850;

    line-height: 1.2;
}


.sp-sidebar-sub {

    color:
        var(--sp-muted);

    font-size: 11px;

    margin-top: 2px;
}


.sp-live-badge {

    display: inline-block;

    margin-top: 12px;

    padding:
        5px 9px;

    border-radius:
        999px;

    color:
        #228b4e;

    background:
        color-mix(
            in srgb,
            #54d381 16%,
            var(--sp-surface)
        );

    font-size: 10px;

    font-weight: 800;

    letter-spacing: .4px;
}


/* =========================================================
   SIDEBAR LABEL
   ========================================================= */

.sp-sidebar-section {

    color:
        var(--sp-muted);

    margin:
        17px 10px 6px 10px;

    font-size: 10px;

    font-weight: 850;

    letter-spacing: 1.1px;

    text-transform: uppercase;
}


/* =========================================================
   SIDEBAR RADIO -> WEB NAVIGATION
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
        all .16s ease;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"]:hover {

    background:
        var(--sp-hover);

    border-color:
        var(--sp-border);

    transform:
        translateX(2px);
}


/* Hide default radio circle */

section[data-testid="stSidebar"]
label[data-baseweb="radio"]
div[role="radio"] {

    display: none;
}


/* Selected navigation item */

section[data-testid="stSidebar"]
label[data-baseweb="radio"]:has(input:checked) {

    background:
        var(--sp-primary-soft);

    border-color:
        color-mix(
            in srgb,
            var(--sp-primary) 30%,
            var(--sp-border)
        );

    box-shadow:
        inset 3px 0 0
        var(--sp-primary);
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"] p {

    color:
        var(--sp-text);

    font-size: 14px;

    font-weight: 570;
}


section[data-testid="stSidebar"]
label[data-baseweb="radio"]:has(input:checked) p {

    color:
        var(--sp-text);

    font-weight: 760;
}


/* =========================================================
   SIDEBAR AI STATUS
   ========================================================= */

.sp-ai-status {

    padding: 14px;

    margin:
        7px 2px;

    border-radius: 15px;

    border:
        1px solid
        var(--sp-border);

    background:
        var(--sp-surface);
}


.sp-ai-row {

    display: flex;

    align-items: center;

    justify-content: space-between;
}


.sp-ai-status-title {

    color:
        var(--sp-text);

    font-size: 13px;

    font-weight: 800;
}


.sp-online {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #46d875;

    box-shadow:
        0 0 0 4px
        rgba(70,216,117,0.13);
}


.sp-offline {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #f87171;
}


.sp-ai-model {

    margin-top: 7px;

    color:
        var(--sp-muted);

    font-size: 11px;
}


/* =========================================================
   SIDEBAR FOOTER
   ========================================================= */

.sp-sidebar-footer {

    color:
        var(--sp-muted);

    text-align: center;

    padding:
        18px 4px 5px 4px;

    font-size: 10px;

    line-height: 1.5;
}


section[data-testid="stSidebar"] hr {

    border-color:
        var(--sp-border);
}


/* =========================================================
   LIGHT MODE EXTRA POLISH
   ========================================================= */

@media (prefers-color-scheme: light) {

    .sp-metric-card {

        box-shadow:
            0 8px 25px
            rgba(30,60,40,0.055);
    }

}


/* =========================================================
   DARK MODE EXTRA POLISH
   ========================================================= */

@media (prefers-color-scheme: dark) {

    .sp-hero {

        background:
            linear-gradient(
                135deg,
                #102d23 0%,
                #1c563b 55%,
                #426f53 100%
            );
    }

    .sp-metric-card {

        box-shadow:
            0 9px 28px
            rgba(0,0,0,0.18);
    }

}

</style>
"""


# st.html avoids the raw <div> problem
st.html(CUSTOM_CSS)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {

    "pantry_items": [],

    "activity_log": [],

    "ai_meal_plan": None,

    "ai_plan_raw": "",

    "ai_plan_error": None,

    "ai_plan_signature": "",

    "ai_attempt_signature": "",

    "ai_last_updated": None,

    "planner_preference":
        "Practical everyday meals",

    "planner_servings":
        2,

    "planner_time":
        "30 minutes",

    "auto_ai_planner":
        True,

    "flash_message":
        "",
}


for key, value in (
    DEFAULT_SESSION.items()
):

    if key not in (
        st.session_state
    ):

        st.session_state[
            key
        ] = value


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

    "ml",
]


STORAGE_LOCATIONS = [

    "Refrigerator",

    "Freezer",

    "Pantry",

    "Kitchen Cabinet",

    "Others",
]


# ============================================================
# HTML HELPERS
# ============================================================

def page_header(
    kicker,
    title,
    description
):

    st.html(
        f"""
        <div class="sp-kicker">
            {kicker}
        </div>

        <div class="sp-page-title">
            {title}
        </div>

        <div class="sp-page-description">
            {description}
        </div>
        """
    )


def metric_card(
    icon,
    value,
    label
):

    st.html(
        f"""
        <div class="sp-metric-card">

            <div class="sp-metric-icon">
                {icon}
            </div>

            <div class="sp-metric-value">
                {value}
            </div>

            <div class="sp-metric-label">
                {label}
            </div>

        </div>
        """
    )


def status_badge(
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
            ),
    }


    css_class, text = (
        mapping.get(
            status,
            (
                "sp-expired",
                status
            )
        )
    )


    st.html(
        f"""
        <span
            class="
                sp-status
                {css_class}
            "
        >
            {text}
        </span>
        """
    )


# ============================================================
# ACTIVITY TRACKING
# ============================================================

def add_activity(
    message
):

    st.session_state[
        "activity_log"
    ].insert(
        0,
        {
            "time":
                datetime.now().strftime(
                    "%d %b %Y • %H:%M"
                ),

            "message":
                message,
        }
    )


    st.session_state[
        "activity_log"
    ] = (
        st.session_state[
            "activity_log"
        ][:40]
    )


# ============================================================
# DATE HELPER
# ============================================================

def to_date(
    value
):

    if isinstance(
        value,
        date
    ):

        return value


    return (
        datetime.strptime(
            str(
                value
            ),
            "%Y-%m-%d"
        ).date()
    )


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


def expiry_message(
    days_left
):

    if days_left < 0:

        days = abs(
            days_left
        )

        return (
            f"Expired "
            f"{days} "
            f"day"
            f"{'s' if days != 1 else ''} "
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
# SHELF LIFE PROGRESS
# ============================================================

def shelf_progress(
    item
):

    purchase = (
        to_date(
            item[
                "purchase_date"
            ]
        )
    )


    expiry = (
        to_date(
            item[
                "expiry_date"
            ]
        )
    )


    total_days = max(

        (
            expiry
            -
            purchase
        ).days,

        1
    )


    elapsed_days = max(

        (
            date.today()
            -
            purchase
        ).days,

        0
    )


    progress = (
        elapsed_days
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
        st.session_state[
            "pantry_items"
        ]
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
# PANTRY ACTIONS
# ============================================================

def mark_item(
    item_id,
    new_status
):

    for item in (
        st.session_state[
            "pantry_items"
        ]
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
            ] = (
                new_status
            )


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
                    f"was recorded "
                    f"as wasted."
                )


            break


def delete_item(
    item_id
):

    name = None


    for item in (
        st.session_state[
            "pantry_items"
        ]
    ):


        if (
            item[
                "id"
            ]
            ==
            item_id
        ):


            name = (
                item[
                    "item_name"
                ]
            )


            break


    st.session_state[
        "pantry_items"
    ] = [

        item

        for item
        in st.session_state[
            "pantry_items"
        ]

        if (
            item[
                "id"
            ]
            !=
            item_id
        )
    ]


    if name:


        add_activity(
            f"❌ "
            f"{name} "
            f"was removed "
            f"from the pantry."
        )


# ============================================================
# PANTRY HEALTH
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
# OLLAMA CONFIG
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


def get_ollama_model():

    try:

        return (
            st.secrets.get(
                "OLLAMA_MODEL",
                "gpt-oss:120b"
            )
        )

    except Exception:

        return (
            "gpt-oss:120b"
        )


# ============================================================
# SMARTPANTRY AI SYSTEM PROMPT
# ============================================================

SMARTPANTRY_AI_SYSTEM = """
You are SmartPantry's Autonomous Meal Planning Engine.

You are not a general-purpose chatbot.

You operate only inside the SmartPantry food tracking system.

SmartPantry itself determines:
- expiry dates
- days remaining
- lifecycle status
- food cost
- storage location
- whether food is Available, Consumed, Wasted or Expired

Treat these supplied values as authoritative.

YOUR RESPONSIBILITY

You completely control the meal planning process.

For every current pantry situation, independently determine:

1. pantry urgency;
2. foods that should be prioritised;
3. how many meals should be planned, from 1 to 4;
4. which meal should be prepared first;
5. pantry ingredients allocated to each meal;
6. additional ingredients that are actually necessary;
7. short practical preparation instructions;
8. the most useful next action.

FOOD PRIORITY

Priority 1:
Usable food with 0-2 days remaining.

Priority 2:
Usable food with 3-7 days remaining.

Priority 3:
Usable food with 8-14 days remaining.

Priority 4:
Long-life foods.

Your objective is to reduce avoidable household food waste.

IMPORTANT RULES

Never recommend:
- Consumed items
- Wasted items
- Expired items

Never invent a pantry ingredient.

Missing ingredients may be suggested,
but they must be clearly listed as missing or optional.

Minimise unnecessary purchases.

Do not allocate a clearly limited ingredient
to many meals unless the available quantity supports it.

Use realistic everyday meals.

Do not provide dieting, weight-loss,
calorie restriction or body-weight advice.

FOOD SAFETY

Expiry information alone does not prove that food is safe.

For perishable foods, remind the user to check
normal appearance, smell, freshness and storage condition.

Do not recommend an item SmartPantry identifies as expired.

OUTPUT

Return ONLY valid JSON.

Do not use markdown code fences.

Use this exact structure:

{
  "situation_title": "short title",
  "situation_level": "Low | Moderate | High | Urgent",
  "situation_summary": "brief explanation",
  "planner_strategy": "brief strategy",
  "meals": [
    {
      "meal_name": "name",
      "priority": "Cook today | Cook next | Flexible",
      "why_now": "brief explanation",
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
      "food_safety_note": "short safety reminder"
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

    df = (
        create_dataframe()
    )


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


    result = []


    for _, row in (
        usable.iterrows()
    ):


        result.append(
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


    return result


# ============================================================
# OLLAMA CLOUD API
# ============================================================

def call_ollama_cloud(
    user_prompt
):

    if not (
        ollama_configured()
    ):


        return (
            None,
            (
                "Ollama Cloud is not configured. "
                "Add OLLAMA_API_KEY to "
                "Streamlit Secrets."
            )
        )


    try:


        response = (
            requests.post(

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
        )


        response.raise_for_status()


        result = (
            response.json()
        )


        return (
            result[
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
                "Ollama Cloud took "
                "too long to respond."
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
                "Unable to read "
                "the Ollama response: "
                f"{error}"
            )
        )


# ============================================================
# JSON PARSER
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

        return (
            json.loads(
                cleaned
            )
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

            return (
                json.loads(
                    cleaned[
                        start:
                        end + 1
                    ]
                )
            )

        except Exception:

            return None


    return None


# ============================================================
# VALIDATE AI OUTPUT
# ============================================================

def validate_ai_plan(
    plan
):

    if not isinstance(
        plan,
        dict
    ):

        return None


    meals = (
        plan.get(
            "meals",
            []
        )
    )


    if not isinstance(
        meals,
        list
    ):

        meals = []


    cleaned_meals = []


    for meal in (
        meals[:4]
    ):


        if not isinstance(
            meal,
            dict
        ):

            continue


        preparation = (
            meal.get(
                "preparation",
                []
            )
        )


        if not isinstance(
            preparation,
            list
        ):

            preparation = []


        pantry_ingredients = (
            meal.get(
                "pantry_ingredients",
                []
            )
        )


        if not isinstance(
            pantry_ingredients,
            list
        ):

            pantry_ingredients = []


        missing_ingredients = (
            meal.get(
                "missing_ingredients",
                []
            )
        )


        if not isinstance(
            missing_ingredients,
            list
        ):

            missing_ingredients = []


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
                    [
                        str(x)
                        for x
                        in pantry_ingredients
                    ],

                "missing_ingredients":
                    [
                        str(x)
                        for x
                        in missing_ingredients
                    ],

                "preparation":
                    [
                        str(x)
                        for x
                        in preparation
                    ],

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
                        "Review your "
                        "priority foods."
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


    return (
        hashlib.sha256(
            raw.encode(
                "utf-8"
            )
        ).hexdigest()
    )


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

Reason for this evaluation:
{reason}

Today's date:
{date.today()}

CURRENT USABLE PANTRY

{json.dumps(pantry, indent=2)}

PLANNER SETTINGS

Meal preference:
{st.session_state["planner_preference"]}

Servings:
{st.session_state["planner_servings"]}

Preferred maximum preparation time:
{st.session_state["planner_time"]}

Treat this as a completely new pantry situation.

Autonomously determine:
- pantry urgency
- food priorities
- number of meals
- meal order
- pantry ingredient allocation
- missing ingredients
- preparation approach
- next best action

Main objective:
Reduce avoidable food waste.

Return only the required JSON.
"""


    (
        result,
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
    ] = (
        result
    )


    parsed = (
        parse_ai_json(
            result
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
            "The AI responded, "
            "but SmartPantry could "
            "not read the meal plan."
        )


        return False


    st.session_state[
        "ai_meal_plan"
    ] = (
        parsed
    )


    st.session_state[
        "ai_plan_error"
    ] = None


    st.session_state[
        "ai_plan_signature"
    ] = (
        signature
    )


    st.session_state[
        "ai_last_updated"
    ] = (
        datetime.now()
    )


    add_activity(
        "🤖 AI Meal Planner "
        "adapted to the latest "
        "pantry situation."
    )


    return True


# ============================================================
# AUTOMATIC AI REPLANNING
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
                "SmartPantry detected "
                "a new inventory, expiry, "
                "date, lifecycle or "
                "preference situation."
            )
        )


# ============================================================
# DEMO DATA
# ============================================================

def load_demo_data():

    today = (
        date.today()
    )


    sample = [

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
    ) in sample:


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
        "🧪 Demo pantry "
        "inventory loaded."
    )


    st.session_state[
        "ai_attempt_signature"
    ] = ""


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="sp-hero">

        <div class="sp-hero-badge">
            ✨ AI-POWERED FOOD INTELLIGENCE
        </div>

        <div class="sp-hero-title">
            🥕 SmartPantry
        </div>

        <div class="sp-hero-subtitle">

            Track every food lifecycle,
            identify expiry risk,
            protect pantry value,
            reduce avoidable waste,
            and let an autonomous Ollama Cloud
            planner adapt your meals when
            circumstances change.

        </div>

    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:


    st.html(
        """
        <div class="sp-sidebar-brand">

            <div class="sp-sidebar-brand-row">

                <div class="sp-sidebar-logo">
                    🥕
                </div>

                <div>

                    <div class="sp-sidebar-name">
                        SmartPantry
                    </div>

                    <div class="sp-sidebar-sub">
                        Food Intelligence Platform
                    </div>

                </div>

            </div>

            <div class="sp-live-badge">
                ● LIVE TRACKING
            </div>

        </div>
        """
    )


    st.html(
        """
        <div class="sp-sidebar-section">
            Workspace
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


    st.html(
        """
        <div class="sp-sidebar-section">
            Intelligence
        </div>
        """
    )


    with st.container(
        border=True
    ):


        st.toggle(
            "🤖 Automatic Planning",
            key=
                "auto_ai_planner"
        )


        if (
            st.session_state[
                "auto_ai_planner"
            ]
        ):


            st.caption(
                "The planner reacts "
                "automatically when "
                "pantry conditions change."
            )


        else:


            st.caption(
                "Automatic AI "
                "replanning is paused."
            )


    if ollama_configured():


        st.html(
            f"""
            <div class="sp-ai-status">

                <div class="sp-ai-row">

                    <div class="sp-ai-status-title">
                        Ollama Cloud
                    </div>

                    <div class="sp-online">
                    </div>

                </div>

                <div class="sp-ai-model">
                    Connected •
                    {get_ollama_model()}
                </div>

            </div>
            """
        )


    else:


        st.html(
            """
            <div class="sp-ai-status">

                <div class="sp-ai-row">

                    <div class="sp-ai-status-title">
                        Ollama Cloud
                    </div>

                    <div class="sp-offline">
                    </div>

                </div>

                <div class="sp-ai-model">
                    API key not configured
                </div>

            </div>
            """
        )


    sidebar_df = (
        create_dataframe()
    )


    if not (
        sidebar_df.empty
    ):


        active_sidebar = (
            sidebar_df[
                sidebar_df[
                    "Item Status"
                ]
                ==
                "Available"
            ]
        )


        risk_sidebar = (
            active_sidebar[
                (
                    active_sidebar[
                        "Days Left"
                    ]
                    >=
                    0
                )
                &
                (
                    active_sidebar[
                        "Days Left"
                    ]
                    <=
                    7
                )
            ]
        )


        st.html(
            """
            <div class="sp-sidebar-section">
                Pantry Status
            </div>
            """
        )


        s1, s2 = (
            st.columns(2)
        )


        s1.metric(
            "Items",
            len(
                active_sidebar
            )
        )


        s2.metric(
            "Risk",
            len(
                risk_sidebar
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


    st.html(
        """
        <div class="sp-sidebar-footer">

            SmartPantry Intelligence System

            <br>

            Theme automatically follows
            your Streamlit appearance.

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
# AUTOMATIC AI CHECK
# ============================================================

automatic_ai_update()


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "🏠 Overview":


    page_header(

        "Pantry Command Centre",

        "Overview",

        (
            "See what needs attention, "
            "what value is at risk, and "
            "how SmartPantry is responding."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "Your pantry is empty. "
            "Add an item or use "
            "the Demo Pantry."
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


        (
            health,
            health_label
        ) = pantry_health_score(
            df
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


        pantry_value = (
            available[
                "Cost (RM)"
            ].sum()
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
                "### 🌿 Pantry Health"
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
                "consumption and recorded waste."
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
                    f"RM {risk_value:.2f}"
                )


                st.caption(
                    f"{len(attention)} "
                    f"item(s) expire "
                    f"within seven days."
                )


        st.divider()


        a, b, c, d = (
            st.columns(4)
        )


        with a:

            metric_card(
                "🥫",
                len(
                    available
                ),
                "Available Items"
            )


        with b:

            metric_card(
                "🚨",
                len(
                    attention
                ),
                "Need Attention"
            )


        with c:

            metric_card(
                "💼",
                f"RM {pantry_value:.2f}",
                "Pantry Value"
            )


        with d:

            metric_card(
                "💚",
                f"RM {saved_value:.2f}",
                "Value Saved"
            )


        st.divider()


        st.markdown(
            "### 🚨 Priority Food"
        )


        if (
            attention.empty
        ):


            st.success(
                "No food currently "
                "needs urgent attention."
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


                    x, y, z = (
                        st.columns(
                            [
                                3,
                                2,
                                1
                            ]
                        )
                    )


                    with x:


                        st.markdown(
                            f"#### "
                            f"{row['Food']}"
                        )


                        status_badge(
                            row[
                                "Expiry Status"
                            ]
                        )


                    with y:


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


                    with z:


                        st.metric(
                            "Value",
                            f"RM "
                            f"{row['Cost (RM)']:.2f}"
                        )


        st.divider()


        st.html(
            """
            <div class="sp-ai-panel">

                <div class="sp-ai-title">
                    🤖 Autonomous Meal Intelligence
                </div>

                <div class="sp-ai-description">

                    SmartPantry continuously compares
                    your current pantry with the
                    previous situation.

                    When food is added,
                    consumed, wasted,
                    removed, or moves closer
                    to expiry, the Ollama planner
                    can automatically rebuild
                    the meal strategy.

                </div>

            </div>
            """
        )


        plan = (
            st.session_state[
                "ai_meal_plan"
            ]
        )


        if plan:


            st.markdown(
                f"### "
                f"{plan.get('situation_title', 'Current AI Plan')}"
            )


            st.write(
                "**Situation:** "
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


            if plan.get(
                "planner_strategy"
            ):


                st.info(
                    "🎯 "
                    +
                    plan[
                        "planner_strategy"
                    ]
                )


            st.caption(
                f"{len(plan.get('meals', []))} "
                f"meal(s) currently selected "
                f"by the AI planner."
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
                "No AI plan "
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
                "No activity yet."
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

        "Lifecycle Management",

        "Food Tracker",

        (
            "Monitor every food item "
            "through its complete "
            "pantry lifecycle."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "No food items "
            "are currently tracked."
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


        status_filter = (
            f3.selectbox(

                "Lifecycle Status",

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
            status_filter
            !=
            "All"
        ):


            filtered = filtered[
                filtered[
                    "Item Status"
                ]
                ==
                status_filter
            ]


        filtered = (
            filtered.sort_values(
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


                main_col, qty_col = (
                    st.columns(
                        [
                            4,
                            1
                        ]
                    )
                )


                with main_col:


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


                        status_badge(
                            row[
                                "Expiry Status"
                            ]
                        )


                    else:


                        st.write(
                            "**Lifecycle:** "
                            +
                            row[
                                "Item Status"
                            ]
                        )


                    st.caption(
                        f"{row['Category']} "
                        f"• "
                        f"{row['Storage']} "
                        f"• "
                        f"RM {row['Cost (RM)']:.2f}"
                    )


                with qty_col:


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


                    progress = (
                        shelf_progress(
                            source_item
                        )
                    )


                    st.progress(
                        progress
                    )


                    p1, p2, p3 = (
                        st.columns(3)
                    )


                    p1.caption(
                        "Purchased\n"
                        +
                        str(
                            row[
                                "Purchase Date"
                            ]
                        )
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

                        "✅ Consumed",

                        key=
                            "consume_"
                            +
                            row[
                                "ID"
                            ],

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
                            f"marked consumed."
                        )


                        st.rerun()


                    if b2.button(

                        "🗑️ Wasted",

                        key=
                            "waste_"
                            +
                            row[
                                "ID"
                            ],

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
                            f"marked wasted."
                        )


                        st.rerun()


                    if b3.button(

                        "❌ Remove",

                        key=
                            "remove_"
                            +
                            row[
                                "ID"
                            ],

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
                            f"removed."
                        )


                        st.rerun()


# ============================================================
# ADD ITEM
# ============================================================

elif page == "➕ Add Item":


    page_header(

        "Inventory Entry",

        "Add Food",

        (
            "Add a pantry item "
            "and SmartPantry will immediately "
            "begin monitoring its lifecycle."
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
                        "Storage",
                        STORAGE_LOCATIONS
                    )
                )


            submitted = (
                st.form_submit_button(
                    "➕ Add to SmartPantry",
                    use_container_width=True
                )
            )


            if submitted:


                if not (
                    food_name.strip()
                ):


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
                        "be before "
                        "purchase date."
                    )


                else:


                    st.session_state[
                        "pantry_items"
                    ].append(
                        {
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
                    )


                    add_activity(
                        f"➕ "
                        f"{food_name.strip()} "
                        f"was added."
                    )


                    st.session_state[
                        "ai_attempt_signature"
                    ] = ""


                    st.session_state[
                        "flash_message"
                    ] = (
                        f"{food_name.strip()} "
                        f"added successfully."
                    )


                    st.rerun()


# ============================================================
# EXPIRY TIMELINE
# ============================================================

elif page == "📅 Expiry Timeline":


    page_header(

        "Time-Based Tracking",

        "Expiry Timeline",

        (
            "Organise pantry items "
            "by how soon they need "
            "your attention."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "No tracked food yet."
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


        for title, group in (
            groups
        ):


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


                        t1, t2, t3 = (
                            st.columns(
                                [
                                    3,
                                    2,
                                    1
                                ]
                            )
                        )


                        with t1:


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


                        t2.write(
                            expiry_message(
                                row[
                                    "Days Left"
                                ]
                            )
                        )


                        t3.write(
                            f"{row['Quantity']} "
                            f"{row['Unit']}"
                        )


# ============================================================
# AI MEAL PLANNER
# ============================================================

elif page == "✨ AI Meal Planner":


    page_header(

        "Ollama Cloud",

        "Autonomous Meal Planner",

        (
            "SmartPantry provides verified "
            "pantry tracking data while "
            "the AI controls the meal strategy."
        )
    )


    st.html(
        """
        <div class="sp-ai-panel">

            <div class="sp-ai-title">
                ✨ AI-Controlled Meal Strategy
            </div>

            <div class="sp-ai-description">

                The AI decides meal count,
                food priority,
                meal order,
                ingredient allocation,
                optional purchases,
                preparation guidance,
                and the next recommended action.

                When pantry circumstances change,
                the plan can automatically change too.

            </div>

        </div>
        """
    )


    with st.expander(
        "⚙️ Planner Preferences"
    ):


        with st.form(
            "planner_settings"
        ):


            preference = (
                st.text_input(
                    "Meal Preference",
                    value=
                        st.session_state[
                            "planner_preference"
                        ],
                    placeholder=
                        "Example: quick meals"
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


            current_time = (
                st.session_state[
                    "planner_time"
                ]
            )


            time_index = (

                time_options.index(
                    current_time
                )

                if current_time
                in time_options

                else 1
            )


            selected_time = (
                st.selectbox(
                    "Maximum Preparation Time",
                    time_options,
                    index=
                        time_index
                )
            )


            if st.form_submit_button(

                "Save & Recalculate",

                use_container_width=True
            ):


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
                    selected_time
                )


                st.session_state[
                    "ai_attempt_signature"
                ] = ""


                add_activity(
                    "⚙️ AI planner "
                    "preferences changed."
                )


                st.rerun()


    pantry = (
        ai_pantry_context()
    )


    if not pantry:


        st.warning(
            "There are no usable "
            "non-expired foods "
            "for meal planning."
        )


    else:


        r1, r2 = (
            st.columns(
                [
                    1,
                    2
                ]
            )
        )


        with r1:


            if st.button(

                "🔄 Re-plan Now",

                use_container_width=True
            ):


                with st.spinner(
                    "Ollama Cloud is "
                    "analysing your pantry..."
                ):


                    generate_ai_plan(
                        (
                            "The user manually "
                            "requested a completely "
                            "fresh pantry analysis."
                        ),
                        force=True
                    )


                st.rerun()


        with r2:


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
                    f"{len(pantry)} "
                    f"usable item(s) "
                    f"are available "
                    f"for AI planning."
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
                    "Technical AI response"
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


            s1, s2 = (
                st.columns(
                    [
                        1,
                        2
                    ]
                )
            )


            with s1:


                st.metric(
                    "Situation",
                    plan.get(
                        "situation_level",
                        "Moderate"
                    )
                )


            with s2:


                st.markdown(
                    "### "
                    +
                    plan.get(
                        "situation_title",
                        "Current Pantry Strategy"
                    )
                )


                st.write(
                    plan.get(
                        "situation_summary",
                        ""
                    )
                )


            if (
                plan.get(
                    "planner_strategy"
                )
            ):


                st.info(
                    "🎯 "
                    +
                    plan[
                        "planner_strategy"
                    ]
                )


            meals = (
                plan.get(
                    "meals",
                    []
                )
            )


            st.markdown(
                f"### 🍽️ "
                f"{len(meals)} "
                f"AI-Selected Meal(s)"
            )


            for number, meal in (
                enumerate(
                    meals,
                    start=1
                )
            ):


                with st.container(
                    border=True
                ):


                    m1, m2 = (
                        st.columns(
                            [
                                4,
                                1
                            ]
                        )
                    )


                    with m1:


                        st.markdown(
                            f"### "
                            f"{number}. "
                            f"{meal.get('meal_name', 'Meal')}"
                        )


                    with m2:


                        st.caption(
                            "PRIORITY"
                        )


                        st.write(
                            "**"
                            +
                            meal.get(
                                "priority",
                                "Flexible"
                            )
                            +
                            "**"
                        )


                    st.write(
                        "**Why now**"
                    )


                    st.write(
                        meal.get(
                            "why_now",
                            ""
                        )
                    )


                    i1, i2 = (
                        st.columns(2)
                    )


                    with i1:


                        st.markdown(
                            "#### 🥕 Pantry Items"
                        )


                        pantry_used = (
                            meal.get(
                                "pantry_ingredients",
                                []
                            )
                        )


                        if pantry_used:


                            for ingredient in (
                                pantry_used
                            ):


                                st.write(
                                    "✓ "
                                    +
                                    ingredient
                                )


                        else:


                            st.caption(
                                "No pantry items listed."
                            )


                    with i2:


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


                            for ingredient in (
                                missing
                            ):


                                st.write(
                                    "• "
                                    +
                                    ingredient
                                )


                        else:


                            st.success(
                                "Nothing extra needed."
                            )


                    preparation = (
                        meal.get(
                            "preparation",
                            []
                        )
                    )


                    if preparation:


                        with st.expander(
                            "👨‍🍳 Preparation"
                        ):


                            for index, step in (
                                enumerate(
                                    preparation,
                                    start=1
                                )
                            ):


                                st.write(
                                    f"{index}. "
                                    f"{step}"
                                )


                    safety_note = (
                        meal.get(
                            "food_safety_note",
                            ""
                        )
                    )


                    if safety_note:


                        st.caption(
                            "Food safety: "
                            +
                            safety_note
                        )


            st.divider()


            st.success(
                "✅ **Next Action:** "
                +
                plan.get(
                    "next_action",
                    (
                        "Review the foods "
                        "needing attention."
                    )
                )
            )


        elif not (
            st.session_state[
                "ai_plan_error"
            ]
        ):


            st.info(
                "No plan has been "
                "generated yet. "
                "Select **Re-plan Now**."
            )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "📊 Insights":


    page_header(

        "Performance Analytics",

        "Insights",

        (
            "See how much food you save, "
            "how much value is protected, "
            "and where waste occurs."
        )
    )


    df = (
        create_dataframe()
    )


    if df.empty:


        st.info(
            "Add pantry data "
            "to view analytics."
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


        avoidance_rate = (

            len(
                consumed
            )
            /
            completed
            *
            100

            if completed

            else 0
        )


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


        x1, x2, x3, x4 = (
            st.columns(4)
        )


        with x1:

            metric_card(
                "🌱",
                len(
                    consumed
                ),
                "Food Saved"
            )


        with x2:

            metric_card(
                "💚",
                f"RM {value_saved:.2f}",
                "Value Saved"
            )


        with x3:

            metric_card(
                "🗑️",
                f"RM {waste_cost:.2f}",
                "Waste Cost"
            )


        with x4:

            metric_card(
                "📈",
                f"{avoidance_rate:.1f}%",
                "Waste Avoidance"
            )


        st.divider()


        if completed:


            outcome_df = (
                pd.DataFrame(
                    {
                        "Outcome": [
                            "Consumed",
                            "Wasted"
                        ],

                        "Items": [
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


            fig = (
                px.pie(

                    outcome_df,

                    names=
                        "Outcome",

                    values=
                        "Items",

                    hole=
                        0.50,

                    title=
                        "Food Lifecycle Outcomes"
                )
            )


            # Transparent chart background
            # works better in both themes
            fig.update_layout(
                paper_bgcolor=
                    "rgba(0,0,0,0)",

                plot_bgcolor=
                    "rgba(0,0,0,0)"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


        if not (
            available.empty
        ):


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


            category_fig = (
                px.bar(

                    category_df,

                    x=
                        "Category",

                    y=
                        "Items",

                    title=
                        "Available Pantry by Category"
                )
            )


            category_fig.update_layout(
                paper_bgcolor=
                    "rgba(0,0,0,0)",

                plot_bgcolor=
                    "rgba(0,0,0,0)"
            )


            st.plotly_chart(
                category_fig,
                use_container_width=True
            )


        st.divider()


        st.markdown(
            "### 💾 Pantry Backup"
        )


        backup = (
            pd.DataFrame(
                st.session_state[
                    "pantry_items"
                ]
            )
        )


        csv = (
            backup
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )


        st.download_button(

            "⬇️ Download Backup",

            data=
                csv,

            file_name=
                "smartpantry_backup.csv",

            mime=
                "text/csv"
        )


        uploaded = (
            st.file_uploader(
                "Restore Backup",
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
                    required
                    .issubset(
                        set(
                            restored.columns
                        )
                    )
                ):


                    st.error(
                        "This is not "
                        "a valid "
                        "SmartPantry backup."
                    )


                else:


                    if st.button(
                        "♻️ Restore Pantry"
                    ):


                        records = (

                            restored
                            .fillna("")
                            .to_dict(
                                orient=
                                    "records"
                            )
                        )


                        for record in (
                            records
                        ):


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
                        ] = (
                            records
                        )


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
                            "Pantry restored successfully."
                        )


                        st.rerun()


            except Exception as error:


                st.error(
                    "Unable to restore "
                    f"backup: {error}"
                )
