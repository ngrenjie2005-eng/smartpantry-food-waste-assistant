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
    initial_sidebar_state="expanded"
)


# ============================================================
# ATTRACTIVE INTERFACE STYLE
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        max-width: 1250px;
    }

    /* Hero */

    .hero-box {
        padding: 34px 38px;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                #12372A 0%,
                #436850 55%,
                #ADBC9F 100%
            );
        color: white;
        margin-bottom: 25px;
        box-shadow:
            0px 12px 30px
            rgba(0, 0, 0, 0.12);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin: 0;
    }

    .hero-subtitle {
        font-size: 17px;
        opacity: 0.90;
        margin-top: 7px;
    }

    /* Section header */

    .section-title {
        font-size: 24px;
        font-weight: 750;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    /* Metric cards */

    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid
            rgba(128, 128, 128, 0.20);
        border-radius: 18px;
        padding: 20px;
        min-height: 125px;
        box-shadow:
            0px 5px 18px
            rgba(0, 0, 0, 0.06);
        margin-bottom: 10px;
    }

    .metric-icon {
        font-size: 25px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        margin-top: 7px;
    }

    .metric-label {
        font-size: 14px;
        opacity: 0.75;
    }

    /* Status pills */

    .status-fresh {
        background: #DFF3E4;
        color: #166534;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }

    .status-soon {
        background: #FFF3CD;
        color: #7C5E10;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }

    .status-warning {
        background: #FFE5C2;
        color: #9A4D00;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }

    .status-urgent {
        background: #FDE2E2;
        color: #A61B1B;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }

    .status-expired {
        background: #E5E7EB;
        color: #374151;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }

    /* AI banner */

    .ai-banner {
        border-radius: 20px;
        padding: 22px 26px;
        background:
            linear-gradient(
                120deg,
                rgba(67, 104, 80, 0.15),
                rgba(173, 188, 159, 0.12)
            );
        border: 1px solid
            rgba(67, 104, 80, 0.30);
        margin-bottom: 18px;
    }

    .ai-title {
        font-size: 21px;
        font-weight: 800;
    }

    /* Streamlit containers */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }

    div[data-testid="stMetric"] {
        border-radius: 15px;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 12px;
    }

    .stDownloadButton > button {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATES = {
    "pantry_items": [],
    "activity_log": [],

    # AI meal planner
    "ai_meal_plan": None,
    "ai_plan_raw": "",
    "ai_plan_error": None,

    # Signature of latest successful AI plan
    "ai_plan_signature": "",

    # Prevent repeated API calls after an error
    "ai_attempt_signature": "",

    "ai_last_updated": None,

    # Meal preferences
    "planner_preference": "Practical everyday meals",
    "planner_servings": 2,
    "planner_time": "30 minutes",

    # Automatic AI behaviour
    "auto_ai_planner": True
}


for key, value in DEFAULT_STATES.items():

    if key not in st.session_state:
        st.session_state[key] = value


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


STORAGE_LOCATIONS = [
    "Refrigerator",
    "Freezer",
    "Pantry",
    "Kitchen Cabinet",
    "Others"
]


# ============================================================
# HELPER — ACTIVITY LOG
# ============================================================

def add_activity(message):

    st.session_state.activity_log.insert(
        0,
        {
            "time": datetime.now().strftime(
                "%d %b %Y • %H:%M"
            ),
            "message": message
        }
    )

    # Keep only newest 40 activities
    st.session_state.activity_log = (
        st.session_state.activity_log[:40]
    )


# ============================================================
# DATE CONVERSION
# ============================================================

def to_date(value):

    if isinstance(value, date):
        return value

    return datetime.strptime(
        str(value),
        "%Y-%m-%d"
    ).date()


# ============================================================
# EXPIRY INTELLIGENCE
# ============================================================

def expiry_info(expiry_date):

    expiry_date = to_date(
        expiry_date
    )

    days_left = (
        expiry_date - date.today()
    ).days

    if days_left < 0:

        status = "Expired"
        priority = 100

    elif days_left <= 2:

        status = "Urgent"
        priority = 90

    elif days_left <= 7:

        status = "Expiring Soon"
        priority = 75

    elif days_left <= 14:

        status = "Use Soon"
        priority = 40

    else:

        status = "Fresh"
        priority = 20

    return (
        days_left,
        status,
        priority
    )


def expiry_message(days_left):

    if days_left < 0:

        days = abs(days_left)

        if days == 1:
            return "Expired 1 day ago"

        return f"Expired {days} days ago"

    elif days_left == 0:

        return "Expires today"

    elif days_left == 1:

        return "Expires tomorrow"

    else:

        return f"Expires in {days_left} days"


# ============================================================
# EXPIRY STATUS VISUAL
# ============================================================

def status_html(status):

    mappings = {

        "Fresh":
            (
                "status-fresh",
                "🟢 Fresh"
            ),

        "Use Soon":
            (
                "status-soon",
                "🟡 Use Soon"
            ),

        "Expiring Soon":
            (
                "status-warning",
                "🟠 Expiring Soon"
            ),

        "Urgent":
            (
                "status-urgent",
                "🔴 Urgent"
            ),

        "Expired":
            (
                "status-expired",
                "⚫ Expired"
            )
    }

    css_class, text = mappings.get(
        status,
        (
            "status-expired",
            status
        )
    )

    return (
        f'<span class="{css_class}">'
        f'{text}'
        f'</span>'
    )


# ============================================================
# SHELF-LIFE PROGRESS
# ============================================================

def shelf_progress(item):

    purchase = to_date(
        item["purchase_date"]
    )

    expiry = to_date(
        item["expiry_date"]
    )

    total = max(
        (
            expiry - purchase
        ).days,
        1
    )

    passed = max(
        (
            date.today()
            -
            purchase
        ).days,
        0
    )

    progress = (
        passed / total
    )

    return min(
        max(progress, 0),
        1
    )


# ============================================================
# DATAFRAME
# ============================================================

def create_dataframe():

    rows = []

    for item in st.session_state.pantry_items:

        days_left, status, priority = (
            expiry_info(
                item["expiry_date"]
            )
        )

        rows.append(
            {
                "ID":
                    item["id"],

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
                    status,

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

    return pd.DataFrame(rows)


# ============================================================
# MODIFY FOOD STATUS
# ============================================================

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
                    f"✅ {item['item_name']} "
                    f"was consumed."
                )

            elif new_status == "Wasted":

                add_activity(
                    f"🗑️ {item['item_name']} "
                    f"was recorded as wasted."
                )

            break


def delete_item(item_id):

    target = None

    for item in st.session_state.pantry_items:

        if item["id"] == item_id:

            target = item["item_name"]

            break

    st.session_state.pantry_items = [
        item
        for item in st.session_state.pantry_items
        if item["id"] != item_id
    ]

    if target:

        add_activity(
            f"❌ {target} was removed "
            f"from the pantry."
        )


# ============================================================
# PANTRY HEALTH SCORE
# ============================================================

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
                available["Days Left"] >= 0
            )
            &
            (
                available["Days Left"] <= 2
            )
        ]
    )

    expired = len(
        available[
            available["Days Left"] < 0
        ]
    )

    wasted = len(
        df[
            df["Item Status"]
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
        min(score, 100)
    )

    if score >= 90:
        label = "Excellent"

    elif score >= 75:
        label = "Good"

    elif score >= 50:
        label = "Needs Attention"

    else:
        label = "High Waste Risk"

    return score, label


# ============================================================
# METRIC CARD
# ============================================================

def metric_card(
    icon,
    label,
    value
):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">
                {icon}
            </div>

            <div class="metric-value">
                {value}
            </div>

            <div class="metric-label">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# OLLAMA CLOUD CONFIGURATION
# ============================================================

def ollama_configured():

    try:

        api_key = st.secrets[
            "OLLAMA_API_KEY"
        ]

        return bool(api_key)

    except Exception:

        return False


def get_ollama_model():

    try:

        return st.secrets.get(
            "OLLAMA_MODEL",
            "gpt-oss:120b"
        )

    except Exception:

        return "gpt-oss:120b"


# ============================================================
# AI SYSTEM BEHAVIOUR
# ============================================================

SMARTPANTRY_AI_SYSTEM = """
You are the SmartPantry Autonomous Meal Planning Engine.

You are not a general chatbot.

Your only role is to analyse the current SmartPantry food
inventory and autonomously create the most useful meal plan
for the user's CURRENT pantry situation.

SMARTPANTRY SYSTEM RESPONSIBILITIES

The SmartPantry software, not you, determines:
- expiry dates
- days remaining
- food lifecycle status
- pantry cost
- consumed status
- wasted status
- expired status

Treat those supplied values as authoritative.

YOUR RESPONSIBILITY

You completely control meal planning.

You must determine:
1. whether the pantry situation requires urgent action;
2. which foods should be prioritised;
3. how many meals are appropriate;
4. which meals should be prepared first;
5. which available ingredients should be allocated to each meal;
6. whether extra ingredients are required;
7. when each proposed meal should ideally be prepared;
8. the practical reason for each recommendation.

PRIORITY RULES

Follow this priority:

Priority 1:
Usable food with 0-2 days remaining.

Priority 2:
Usable food with 3-7 days remaining.

Priority 3:
Usable food with 8-14 days remaining.

Priority 4:
Fresh long-life foods.

Your goal is to reduce avoidable food waste while producing
practical everyday meals.

IMPORTANT RESTRICTIONS

Never recommend using:
- items marked Consumed;
- items marked Wasted;
- items marked Expired;
- items that are not present in the provided pantry.

Expired items will normally already be excluded from your input.

Do not invent pantry ingredients.

You may recommend missing ingredients, but clearly label them
as optional purchases or missing ingredients.

Minimise unnecessary extra purchases.

Do not repeatedly allocate a very limited pantry item to many
different meals unless the available quantity appears adequate.

FOOD SAFETY

An expiry date alone does not prove that food is safe.

For perishable food, remind the user to check normal freshness
and storage conditions before preparation.

If food shows signs of spoilage or has been stored improperly,
recommend discarding it.

Never suggest using food identified by SmartPantry as expired.

MEAL PLAN BEHAVIOUR

You may create between 1 and 4 meals.

YOU decide the number based on the current situation.

When several urgent ingredients exist, create meals that use
as many compatible urgent ingredients as practical.

When there is little expiry pressure, create fewer,
more flexible suggestions.

Meals should be realistic, ordinary and practical.

Do not provide dieting, weight-loss or calorie-restriction advice.

OUTPUT

Return ONLY valid JSON.

Do not include Markdown fences.

Use this exact structure:

{
  "situation_title": "short situation title",
  "situation_level": "Low | Moderate | High | Urgent",
  "situation_summary": "brief explanation",
  "planner_strategy": "what the planner decided to prioritise",
  "meals": [
    {
      "meal_name": "name",
      "priority": "Cook today | Cook next | Flexible",
      "why_now": "why SmartPantry selected this meal",
      "pantry_ingredients": [
        "ingredient"
      ],
      "missing_ingredients": [
        "ingredient"
      ],
      "preparation": [
        "short step",
        "short step",
        "short step"
      ],
      "food_safety_note": "short safety reminder"
    }
  ],
  "next_action": "single most useful next action"
}

Return JSON only.
"""


# ============================================================
# CREATE AI PANTRY CONTEXT
# ============================================================

def ai_pantry_context():

    df = create_dataframe()

    if df.empty:

        return []

    # Only available AND non-expired food
    usable = df[
        (
            df["Item Status"]
            ==
            "Available"
        )
        &
        (
            df["Days Left"]
            >= 0
        )
    ].sort_values(
        "Days Left"
    )

    context = []

    for _, row in usable.iterrows():

        context.append(
            {
                "food":
                    row["Food"],

                "category":
                    row["Category"],

                "quantity":
                    row["Quantity"],

                "unit":
                    row["Unit"],

                "days_remaining":
                    int(
                        row["Days Left"]
                    ),

                "expiry_status":
                    row[
                        "Expiry Status"
                    ],

                "storage":
                    row["Storage"],

                "cost_rm":
                    round(
                        float(
                            row["Cost (RM)"]
                        ),
                        2
                    )
            }
        )

    return context


# ============================================================
# OLLAMA CLOUD API
# ============================================================

def call_ollama_cloud(
    user_prompt
):

    if not ollama_configured():

        return (
            None,
            "Ollama Cloud has not been configured. "
            "Add OLLAMA_API_KEY to Streamlit Secrets."
        )

    api_key = st.secrets[
        "OLLAMA_API_KEY"
    ]

    model = get_ollama_model()

    try:

        response = requests.post(

            "https://ollama.com/api/chat",

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
                        0.20
                }
            },

            timeout=90
        )

        response.raise_for_status()

        result = response.json()

        content = (
            result[
                "message"
            ][
                "content"
            ]
        )

        return content, None

    except requests.exceptions.Timeout:

        return (
            None,
            "Ollama Cloud took too long to respond."
        )

    except requests.exceptions.RequestException as error:

        return (
            None,
            f"Ollama Cloud request failed: {error}"
        )

    except Exception as error:

        return (
            None,
            f"Unable to read the Ollama response: {error}"
        )


# ============================================================
# JSON PARSER
# ============================================================

def parse_ai_json(text):

    if not text:

        return None

    cleaned = text.strip()

    # Remove code fences if model unexpectedly used them
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
    )

    cleaned = cleaned.strip()

    # First direct attempt
    try:

        return json.loads(
            cleaned
        )

    except Exception:
        pass

    # Second attempt:
    # extract from first { to last }
    try:

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if (
            start != -1
            and
            end != -1
            and
            end > start
        ):

            json_text = cleaned[
                start:end + 1
            ]

            return json.loads(
                json_text
            )

    except Exception:
        pass

    return None


# ============================================================
# AI PLANNER SIGNATURE
# ============================================================

def planner_signature():

    context = ai_pantry_context()

    payload = {
        "date":
            str(
                date.today()
            ),

        "pantry":
            context,

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
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# GENERATE AUTONOMOUS AI PLAN
# ============================================================

def generate_ai_plan(
    reason,
    force=False
):

    pantry = ai_pantry_context()

    if not pantry:

        st.session_state[
            "ai_meal_plan"
        ] = None

        st.session_state[
            "ai_plan_raw"
        ] = ""

        st.session_state[
            "ai_plan_error"
        ] = None

        return False

    signature = planner_signature()

    if not force:

        # Already attempted this exact situation
        if (
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

Reason this plan is being evaluated:
{reason}

Today's date:
{date.today()}

CURRENT USABLE PANTRY INVENTORY

{json.dumps(pantry, indent=2)}

USER PLANNER SETTINGS

Preferred meal style:
{st.session_state["planner_preference"]}

Number of servings:
{st.session_state["planner_servings"]}

Preferred maximum preparation time:
{st.session_state["planner_time"]}

AUTONOMOUS TASK

Analyse this as a NEW pantry situation.

You decide:
- how urgent the situation is;
- which ingredients need priority;
- how many meals should be planned;
- what the meals should be;
- which meal should be prepared first;
- which ingredients should be allocated to each meal;
- what should be purchased only if necessary.

Your main objective is to reduce avoidable food waste.

Return only the required JSON.
"""

    content, error = (
        call_ollama_cloud(
            prompt
        )
    )

    if error:

        st.session_state[
            "ai_plan_error"
        ] = error

        return False

    parsed = parse_ai_json(
        content
    )

    st.session_state[
        "ai_plan_raw"
    ] = content

    if parsed is None:

        st.session_state[
            "ai_plan_error"
        ] = (
            "The AI produced a response, "
            "but SmartPantry could not parse "
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
        "🤖 AI Meal Planner automatically "
        "adapted to the latest pantry situation."
    )

    return True


# ============================================================
# AUTOMATIC SITUATION DETECTION
# ============================================================

def automatic_ai_update():

    if not st.session_state[
        "auto_ai_planner"
    ]:

        return

    if not ollama_configured():

        return

    if not ai_pantry_context():

        return

    current_signature = (
        planner_signature()
    )

    previous_signature = (
        st.session_state[
            "ai_plan_signature"
        ]
    )

    attempted_signature = (
        st.session_state[
            "ai_attempt_signature"
        ]
    )

    # New situation detected
    if (
        current_signature
        != previous_signature
        and
        current_signature
        != attempted_signature
    ):

        generate_ai_plan(
            reason=(
                "SmartPantry detected a change "
                "in inventory, expiry situation, "
                "date, item lifecycle, or planner "
                "preferences."
            )
        )


# ============================================================
# DEMO DATA
# ============================================================

def load_demo_data():

    today = date.today()

    data = [
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
    ) in data:

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
        "🧪 SmartPantry demo inventory loaded."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero-box">

        <div class="hero-title">
            🥕 SmartPantry
        </div>

        <div class="hero-subtitle">
            Intelligent food tracking powered by
            autonomous AI meal planning
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

page = st.sidebar.radio(
    "SmartPantry",
    [
        "🏠 Overview",
        "📍 Food Tracker",
        "➕ Add Item",
        "📅 Expiry Timeline",
        "✨ AI Meal Planner",
        "📊 Insights"
    ]
)


st.sidebar.divider()


# Automatic AI toggle

st.sidebar.toggle(
    "🤖 Automatic AI Planning",
    key="auto_ai_planner"
)


if st.session_state[
    "auto_ai_planner"
]:

    st.sidebar.caption(
        "AI automatically adapts when "
        "the pantry situation changes."
    )


# AI connection indicator

if ollama_configured():

    st.sidebar.success(
        "Ollama Cloud connected"
    )

    st.sidebar.caption(
        f"Model: {get_ollama_model()}"
    )

else:

    st.sidebar.warning(
        "Ollama Cloud not configured"
    )


# Demo button

if not st.session_state[
    "pantry_items"
]:

    if st.sidebar.button(
        "🧪 Load Demo Pantry",
        use_container_width=True
    ):

        load_demo_data()

        st.session_state[
            "ai_attempt_signature"
        ] = ""

        st.rerun()


# ============================================================
# AUTOMATIC AI UPDATE
# ============================================================

automatic_ai_update()


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.markdown(
        '<div class="section-title">'
        'Pantry Overview'
        '</div>',
        unsafe_allow_html=True
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Your pantry is currently empty. "
            "Add your first item or load "
            "the demo pantry."
        )

    else:

        available = df[
            df["Item Status"]
            ==
            "Available"
        ]

        consumed = df[
            df["Item Status"]
            ==
            "Consumed"
        ]

        wasted = df[
            df["Item Status"]
            ==
            "Wasted"
        ]

        attention = available[
            (
                available["Days Left"] >= 0
            )
            &
            (
                available["Days Left"] <= 7
            )
        ]

        expired = available[
            available["Days Left"] < 0
        ]

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

        health, health_label = (
            pantry_health_score(
                df
            )
        )


        # ------------------------------------------------
        # HEALTH AREA
        # ------------------------------------------------

        health_col, risk_col = (
            st.columns(
                [2, 1]
            )
        )

        with health_col:

            st.markdown(
                "### 🌿 Pantry Health"
            )

            st.progress(
                health / 100
            )

            st.markdown(
                f"## {health}/100 "
                f"— {health_label}"
            )

            st.caption(
                "Calculated from urgent, "
                "expired and wasted food."
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
                    f"{len(attention)} item(s) "
                    f"expire within 7 days."
                )


        st.divider()


        # ------------------------------------------------
        # METRICS
        # ------------------------------------------------

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        with c1:

            metric_card(
                "🥫",
                "Available Items",
                len(available)
            )

        with c2:

            metric_card(
                "🚨",
                "Need Attention",
                len(attention)
            )

        with c3:

            metric_card(
                "🌱",
                "Food Saved",
                len(consumed)
            )

        with c4:

            metric_card(
                "💚",
                "Value Saved",
                f"RM {saved_value:.2f}"
            )


        # ------------------------------------------------
        # NEEDS ATTENTION
        # ------------------------------------------------

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

            attention = (
                attention
                .sort_values(
                    "Days Left"
                )
            )

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
                            [3, 2, 1]
                        )
                    )

                    with left:

                        st.markdown(
                            f"#### {row['Food']}"
                        )

                        st.markdown(
                            status_html(
                                row[
                                    "Expiry Status"
                                ]
                            ),
                            unsafe_allow_html=True
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
                            f"{row['Unit']} • "
                            f"{row['Storage']}"
                        )

                    with right:

                        st.metric(
                            "Value",
                            f"RM "
                            f"{row['Cost (RM)']:.2f}"
                        )


        # ------------------------------------------------
        # AI STATUS
        # ------------------------------------------------

        st.divider()

        st.markdown(
            """
            <div class="ai-banner">
                <div class="ai-title">
                    🤖 Autonomous Meal Planner
                </div>
                SmartPantry AI continuously adapts its
                meal strategy whenever your tracked
                pantry situation changes.
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state[
            "ai_meal_plan"
        ]:

            plan = st.session_state[
                "ai_meal_plan"
            ]

            st.markdown(
                f"### "
                f"{plan.get('situation_title', 'Current Plan')}"
            )

            level = plan.get(
                "situation_level",
                "Moderate"
            )

            st.write(
                f"**Situation:** {level}"
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

            meals = plan.get(
                "meals",
                []
            )

            if meals:

                st.caption(
                    f"AI currently recommends "
                    f"{len(meals)} meal(s)."
                )

        elif st.session_state[
            "ai_plan_error"
        ]:

            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )

        else:

            st.caption(
                "No AI plan is available yet."
            )


        # ------------------------------------------------
        # RECENT ACTIVITY
        # ------------------------------------------------

        st.divider()

        st.markdown(
            "### 🕘 Recent Activity"
        )

        if not st.session_state[
            "activity_log"
        ]:

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
                    f"**{event['time']}**"
                )

                st.caption(
                    event["message"]
                )


# ============================================================
# FOOD TRACKER
# ============================================================

elif page == "📍 Food Tracker":

    st.markdown(
        "## 📍 Food Lifecycle Tracker"
    )

    st.caption(
        "Track each item from pantry entry "
        "until consumption or waste."
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "There are no pantry items."
        )

    else:

        search_col, category_col, status_col = (
            st.columns(3)
        )

        search = search_col.text_input(
            "🔍 Search"
        )

        category_filter = (
            category_col.selectbox(
                "Category",
                [
                    "All"
                ]
                +
                sorted(
                    df[
                        "Category"
                    ].unique().tolist()
                )
            )
        )

        lifecycle_filter = (
            status_col.selectbox(
                "Lifecycle",
                [
                    "All",
                    "Available",
                    "Consumed",
                    "Wasted"
                ]
            )
        )


        filtered = df.copy()

        if search:

            filtered = filtered[
                filtered[
                    "Food"
                ].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":

            filtered = filtered[
                filtered[
                    "Category"
                ]
                ==
                category_filter
            ]

        if lifecycle_filter != "All":

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
                "Days Left"
            )
        )


        for _, row in filtered.iterrows():

            source_item = next(
                item
                for item
                in st.session_state[
                    "pantry_items"
                ]
                if item["id"]
                ==
                row["ID"]
            )

            with st.container(
                border=True
            ):

                title_col, qty_col = (
                    st.columns(
                        [4, 1]
                    )
                )

                with title_col:

                    st.markdown(
                        f"### {row['Food']}"
                    )

                    if (
                        row["Item Status"]
                        ==
                        "Available"
                    ):

                        st.markdown(
                            status_html(
                                row[
                                    "Expiry Status"
                                ]
                            ),
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"**{row['Item Status']}**"
                        )

                    st.caption(
                        f"{row['Category']} • "
                        f"{row['Storage']} • "
                        f"RM {row['Cost (RM)']:.2f}"
                    )

                with qty_col:

                    st.metric(
                        "Quantity",
                        f"{row['Quantity']} "
                        f"{row['Unit']}"
                    )


                if (
                    row["Item Status"]
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


                    action1, action2, action3 = (
                        st.columns(3)
                    )

                    if action1.button(
                        "✅ Consumed",
                        key=(
                            "consume_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True
                    ):

                        mark_item(
                            row["ID"],
                            "Consumed"
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()


                    if action2.button(
                        "🗑️ Wasted",
                        key=(
                            "waste_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True
                    ):

                        mark_item(
                            row["ID"],
                            "Wasted"
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()


                    if action3.button(
                        "❌ Delete",
                        key=(
                            "delete_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True
                    ):

                        delete_item(
                            row["ID"]
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()


# ============================================================
# ADD ITEM
# ============================================================

elif page == "➕ Add Item":

    st.markdown(
        "## ➕ Add Pantry Item"
    )

    st.caption(
        "SmartPantry starts tracking the "
        "food lifecycle immediately."
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
                        placeholder=(
                            "Example: Fresh Milk"
                        )
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
                    "Add to SmartPantry",
                    use_container_width=True
                )
            )


            if submit:

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


                    days_left, status, _ = (
                        expiry_info(
                            expiry_date
                        )
                    )


                    add_activity(
                        f"➕ {food_name.strip()} "
                        f"was added to the pantry."
                    )


                    # Forces AI to recognise
                    # the new situation
                    st.session_state[
                        "ai_attempt_signature"
                    ] = ""


                    st.success(
                        f"{food_name.strip()} "
                        f"added successfully."
                    )

                    st.info(
                        f"{status} — "
                        f"{expiry_message(days_left)}"
                    )


# ============================================================
# EXPIRY TIMELINE
# ============================================================

elif page == "📅 Expiry Timeline":

    st.markdown(
        "## 📅 Expiry Timeline"
    )

    st.caption(
        "A tracking view of what needs "
        "attention and when."
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "No food is currently being tracked."
        )

    else:

        available = df[
            df["Item Status"]
            ==
            "Available"
        ].sort_values(
            "Days Left"
        )


        timeline_groups = [
            (
                "⚫ Expired",
                available[
                    available[
                        "Days Left"
                    ] < 0
                ]
            ),

            (
                "🔴 Today",
                available[
                    available[
                        "Days Left"
                    ] == 0
                ]
            ),

            (
                "🟠 Tomorrow",
                available[
                    available[
                        "Days Left"
                    ] == 1
                ]
            ),

            (
                "🟡 Next 7 Days",
                available[
                    (
                        available[
                            "Days Left"
                        ] >= 2
                    )
                    &
                    (
                        available[
                            "Days Left"
                        ] <= 7
                    )
                ]
            ),

            (
                "🟢 Later",
                available[
                    available[
                        "Days Left"
                    ] > 7
                ]
            )
        ]


        for title, group in timeline_groups:

            st.markdown(
                f"### {title}"
            )

            if group.empty:

                st.caption(
                    "No items."
                )

            else:

                for _, item in group.iterrows():

                    with st.container(
                        border=True
                    ):

                        c1, c2, c3 = (
                            st.columns(
                                [3, 2, 1]
                            )
                        )

                        c1.markdown(
                            f"**{item['Food']}**"
                        )

                        c1.caption(
                            f"{item['Category']} • "
                            f"{item['Storage']}"
                        )

                        c2.write(
                            expiry_message(
                                item[
                                    "Days Left"
                                ]
                            )
                        )

                        c3.write(
                            f"{item['Quantity']} "
                            f"{item['Unit']}"
                        )


# ============================================================
# AUTONOMOUS AI MEAL PLANNER
# ============================================================

elif page == "✨ AI Meal Planner":

    st.markdown(
        "## ✨ Autonomous AI Meal Planner"
    )

    st.markdown(
        """
        <div class="ai-banner">
            <div class="ai-title">
                🤖 Ollama Cloud Meal Intelligence
            </div>
            The meal planner is now fully controlled by
            the AI model. SmartPantry supplies the tracking
            situation; the model decides what the meal plan
            should become.
        </div>
        """,
        unsafe_allow_html=True
    )


    # ----------------------------------------------------
    # PLANNER SETTINGS
    # ----------------------------------------------------

    with st.expander(
        "⚙️ Planner Preferences"
    ):

        with st.form(
            "planner_preferences"
        ):

            preference = (
                st.text_input(
                    "Meal Preference",
                    value=(
                        st.session_state[
                            "planner_preference"
                        ]
                    ),
                    placeholder=(
                        "Example: quick everyday meals"
                    )
                )
            )

            servings = (
                st.number_input(
                    "Servings",
                    min_value=1,
                    max_value=8,
                    value=(
                        st.session_state[
                            "planner_servings"
                        ]
                    )
                )
            )

            time_limit = (
                st.selectbox(
                    "Preferred Maximum Time",
                    [
                        "15 minutes",
                        "30 minutes",
                        "45 minutes",
                        "60 minutes"
                    ],
                    index=[
                        "15 minutes",
                        "30 minutes",
                        "45 minutes",
                        "60 minutes"
                    ].index(
                        st.session_state[
                            "planner_time"
                        ]
                    )
                    if
                    st.session_state[
                        "planner_time"
                    ]
                    in
                    [
                        "15 minutes",
                        "30 minutes",
                        "45 minutes",
                        "60 minutes"
                    ]
                    else 1
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
                    if preference.strip()
                    else
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

                st.rerun()


    # ----------------------------------------------------
    # SITUATION INPUT
    # ----------------------------------------------------

    pantry = ai_pantry_context()

    if not pantry:

        st.warning(
            "There are no usable, "
            "non-expired pantry items "
            "available for meal planning."
        )

    else:

        st.caption(
            f"AI is currently analysing "
            f"{len(pantry)} usable "
            f"pantry item(s)."
        )


        # ------------------------------------------------
        # MANUAL FORCE REFRESH
        # ------------------------------------------------

        refresh_col, status_col = (
            st.columns(
                [1, 2]
            )
        )

        with refresh_col:

            if st.button(
                "🔄 Re-plan Now",
                use_container_width=True
            ):

                with st.spinner(
                    "Ollama Cloud is analysing "
                    "the latest pantry situation..."
                ):

                    generate_ai_plan(
                        reason=(
                            "The user manually requested "
                            "a completely new evaluation "
                            "of the current pantry."
                        ),
                        force=True
                    )

                st.rerun()


        with status_col:

            if st.session_state[
                "ai_last_updated"
            ]:

                st.info(
                    "Last AI adaptation: "
                    +
                    st.session_state[
                        "ai_last_updated"
                    ].strftime(
                        "%d %b %Y • %H:%M"
                    )
                )


        # ------------------------------------------------
        # ERRORS
        # ------------------------------------------------

        if st.session_state[
            "ai_plan_error"
        ]:

            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )


        # ------------------------------------------------
        # DISPLAY PLAN
        # ------------------------------------------------

        plan = st.session_state[
            "ai_meal_plan"
        ]

        if plan:

            st.divider()


            # Situation assessment

            situation_col, strategy_col = (
                st.columns(
                    [1, 2]
                )
            )

            with situation_col:

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

            with strategy_col:

                st.markdown(
                    "#### "
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


            st.info(
                "🎯 "
                +
                plan.get(
                    "planner_strategy",
                    "Use priority food first."
                )
            )


            # --------------------------------------------
            # MEAL CARDS
            # --------------------------------------------

            meals = plan.get(
                "meals",
                []
            )

            st.markdown(
                f"### 🍽️ AI Selected "
                f"{len(meals)} Meal(s)"
            )


            for index, meal in enumerate(
                meals,
                start=1
            ):

                with st.container(
                    border=True
                ):

                    title_col, priority_col = (
                        st.columns(
                            [4, 1]
                        )
                    )

                    with title_col:

                        st.markdown(
                            f"### {index}. "
                            f"{meal.get('meal_name', 'Meal')}"
                        )

                    with priority_col:

                        st.markdown(
                            "**Priority**"
                        )

                        st.write(
                            meal.get(
                                "priority",
                                "Flexible"
                            )
                        )


                    st.write(
                        "**Why SmartPantry chose this:**"
                    )

                    st.write(
                        meal.get(
                            "why_now",
                            ""
                        )
                    )


                    ingredients_col, missing_col = (
                        st.columns(2)
                    )


                    with ingredients_col:

                        st.markdown(
                            "#### 🥕 Pantry Items Used"
                        )

                        pantry_ingredients = (
                            meal.get(
                                "pantry_ingredients",
                                []
                            )
                        )

                        if pantry_ingredients:

                            for ingredient in (
                                pantry_ingredients
                            ):

                                st.write(
                                    f"✓ {ingredient}"
                                )

                        else:

                            st.caption(
                                "None listed."
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
                                    f"• {ingredient}"
                                )

                        else:

                            st.success(
                                "No extra ingredients needed."
                            )


                    preparation = meal.get(
                        "preparation",
                        []
                    )

                    if preparation:

                        with st.expander(
                            "👨‍🍳 Preparation Plan"
                        ):

                            for number, step in enumerate(
                                preparation,
                                start=1
                            ):

                                st.write(
                                    f"{number}. {step}"
                                )


                    safety_note = meal.get(
                        "food_safety_note",
                        ""
                    )

                    if safety_note:

                        st.caption(
                            "Food safety: "
                            +
                            safety_note
                        )


            # --------------------------------------------
            # NEXT ACTION
            # --------------------------------------------

            st.divider()

            st.success(
                "✅ **SmartPantry Next Action:** "
                +
                plan.get(
                    "next_action",
                    "Review your priority foods."
                )
            )


        elif (
            not st.session_state[
                "ai_plan_error"
            ]
        ):

            st.info(
                "The AI planner has not generated "
                "a plan yet. Select **Re-plan Now**."
            )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "📊 Insights":

    st.markdown(
        "## 📊 Pantry Tracking Insights"
    )

    df = create_dataframe()

    if df.empty:

        st.info(
            "Add pantry data before "
            "viewing insights."
        )

    else:

        consumed = df[
            df["Item Status"]
            ==
            "Consumed"
        ]

        wasted = df[
            df["Item Status"]
            ==
            "Wasted"
        ]

        available = df[
            df["Item Status"]
            ==
            "Available"
        ]

        total_completed = (
            len(consumed)
            +
            len(wasted)
        )

        if total_completed:

            avoidance_rate = (
                len(consumed)
                /
                total_completed
                *
                100
            )

        else:

            avoidance_rate = 0


        saved_value = (
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
                len(consumed)
            )

        with c2:

            metric_card(
                "💚",
                "Value Saved",
                f"RM {saved_value:.2f}"
            )

        with c3:

            metric_card(
                "🗑️",
                "Waste Cost",
                f"RM {waste_cost:.2f}"
            )

        with c4:

            metric_card(
                "📈",
                "Waste Avoidance",
                f"{avoidance_rate:.1f}%"
            )


        st.divider()


        # ------------------------------------------------
        # OUTCOME CHART
        # ------------------------------------------------

        if total_completed:

            outcome = pd.DataFrame(
                {
                    "Outcome": [
                        "Consumed",
                        "Wasted"
                    ],

                    "Items": [
                        len(consumed),
                        len(wasted)
                    ]
                }
            )

            fig = px.pie(
                outcome,
                names="Outcome",
                values="Items",
                hole=0.48,
                title=(
                    "Food Lifecycle Outcomes"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        # ------------------------------------------------
        # CATEGORY TRACKING
        # ------------------------------------------------

        if not available.empty:

            category = (
                available
                .groupby(
                    "Category"
                )
                .agg(
                    Items=(
                        "Food",
                        "count"
                    ),

                    Value=(
                        "Cost (RM)",
                        "sum"
                    )
                )
                .reset_index()
            )

            fig2 = px.bar(
                category,
                x="Category",
                y="Items",
                title=(
                    "Available Pantry "
                    "by Category"
                )
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )


        # ------------------------------------------------
        # BACKUP
        # ------------------------------------------------

        st.divider()

        st.markdown(
            "### 💾 Data Backup"
        )

        backup_df = pd.DataFrame(
            st.session_state[
                "pantry_items"
            ]
        )

        csv = (
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
            data=csv,
            file_name=(
                "smartpantry_backup.csv"
            ),
            mime="text/csv"
        )


        uploaded = st.file_uploader(
            "Restore SmartPantry Backup",
            type=["csv"]
        )


        if uploaded is not None:

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


                if not required.issubset(
                    set(
                        restored.columns
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

                        st.session_state[
                            "ai_plan_signature"
                        ] = ""

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""


                        add_activity(
                            "♻️ Pantry backup restored."
                        )


                        st.success(
                            "Pantry restored."
                        )

                        st.rerun()


            except Exception as error:

                st.error(
                    f"Unable to restore "
                    f"the backup: {error}"
                )
