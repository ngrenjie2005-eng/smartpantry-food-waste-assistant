import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import uuid
import json
import hashlib
import re

from datetime import date, datetime, timedelta, timezone
from supabase import create_client, Client


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
# THEME-AWARE WEBSITE CSS
# ============================================================

CUSTOM_CSS = """
<style>
:root {
    --sp-surface: var(--secondary-background-color);
    --sp-text: var(--text-color);
    --sp-border: color-mix(in srgb, var(--text-color) 14%, transparent);
    --sp-muted: color-mix(in srgb, var(--text-color) 62%, transparent);
    --sp-green-soft: color-mix(in srgb, #4f946a 14%, var(--secondary-background-color));
    --sp-hover: color-mix(in srgb, #4f946a 11%, var(--secondary-background-color));
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.block-container {
    max-width: 1280px;
    padding-top: 3.2rem !important;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: color-mix(in srgb, var(--background-color) 94%, transparent);
}

/* Hero */
.sp-hero {
    width: 100%;
    box-sizing: border-box;
    padding: 35px 40px;
    margin: 0.4rem 0 32px 0;
    border-radius: 24px;
    background: linear-gradient(135deg, #123e2d 0%, #245e43 58%, #578a69 100%);
    box-shadow: 0 14px 36px rgba(0,0,0,.14);
    color: white;
}
.sp-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 11px;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 999px;
    background: rgba(255,255,255,.10);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .6px;
}
.sp-hero-title {
    font-size: 42px;
    font-weight: 850;
    line-height: 1.06;
    letter-spacing: -1px;
    margin-bottom: 9px;
}
.sp-hero-subtitle {
    max-width: 780px;
    font-size: 16px;
    line-height: 1.6;
    color: rgba(255,255,255,.88);
}

/* Page headings */
.sp-kicker {
    color: var(--sp-muted);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.15px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.sp-page-title {
    color: var(--sp-text);
    font-size: 30px;
    line-height: 1.2;
    font-weight: 850;
    letter-spacing: -.6px;
    margin-bottom: 5px;
}
.sp-page-description {
    color: var(--sp-muted);
    font-size: 14px;
    line-height: 1.55;
    margin-bottom: 22px;
}

/* Metric cards */
.sp-metric-card {
    min-height: 132px;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid var(--sp-border);
    background: var(--sp-surface);
    box-shadow: 0 8px 24px rgba(0,0,0,.055);
    transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.sp-metric-card:hover {
    transform: translateY(-2px);
    border-color: color-mix(in srgb, #4f946a 44%, var(--sp-border));
    box-shadow: 0 12px 30px rgba(0,0,0,.09);
}
.sp-metric-icon { font-size: 25px; margin-bottom: 10px; }
.sp-metric-value {
    color: var(--sp-text);
    font-size: 27px;
    font-weight: 850;
    line-height: 1.15;
    margin-bottom: 6px;
}
.sp-metric-label {
    color: var(--sp-muted);
    font-size: 13px;
    font-weight: 600;
}

/* Status pills */
.sp-status {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
}
.sp-fresh { color: #166534; background: #dcfce7; }
.sp-use { color: #854d0e; background: #fef9c3; }
.sp-soon { color: #9a3412; background: #ffedd5; }
.sp-urgent { color: #991b1b; background: #fee2e2; }
.sp-expired { color: #374151; background: #e5e7eb; }

/* AI panel */
.sp-ai-panel {
    padding: 20px 22px;
    margin: 10px 0 18px 0;
    border-radius: 18px;
    border: 1px solid color-mix(in srgb, #4f946a 32%, var(--sp-border));
    background: var(--sp-green-soft);
}
.sp-ai-title {
    color: var(--sp-text);
    font-size: 19px;
    font-weight: 850;
    margin-bottom: 5px;
}
.sp-ai-description {
    color: var(--sp-muted);
    font-size: 13px;
    line-height: 1.55;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    border-color: var(--sp-border) !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    font-weight: 650;
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(0,0,0,.10);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: color-mix(in srgb, var(--secondary-background-color) 96%, var(--background-color));
    border-right: 1px solid var(--sp-border);
}
section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
    padding-top: .45rem;
}
.sp-sidebar-brand {
    padding: 16px;
    margin: 3px 2px 17px 2px;
    border-radius: 18px;
    border: 1px solid var(--sp-border);
    background: linear-gradient(135deg, var(--sp-green-soft), var(--sp-surface));
}
.sp-sidebar-brand-row {
    display: flex;
    align-items: center;
    gap: 11px;
}
.sp-sidebar-logo {
    width: 43px;
    height: 43px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    font-size: 22px;
    background: linear-gradient(135deg, #65aa7d, #2f704f);
    box-shadow: 0 7px 18px rgba(0,0,0,.18);
}
.sp-sidebar-name {
    color: var(--sp-text);
    font-size: 18px;
    font-weight: 850;
    line-height: 1.2;
}
.sp-sidebar-sub {
    color: var(--sp-muted);
    font-size: 11px;
    margin-top: 2px;
}
.sp-live-badge {
    display: inline-block;
    margin-top: 12px;
    padding: 5px 9px;
    border-radius: 999px;
    background: color-mix(in srgb, #54d381 15%, var(--sp-surface));
    color: #269655;
    font-size: 10px;
    font-weight: 800;
}
.sp-sidebar-section {
    color: var(--sp-muted);
    margin: 17px 10px 6px 10px;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.1px;
    text-transform: uppercase;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 42px;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: .55rem .8rem !important;
    margin: 2px 0 !important;
    border-radius: 11px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--sp-text) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(2px);
    background: var(--sp-hover) !important;
    border-color: var(--sp-border) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(
        90deg,
        color-mix(in srgb, #4f946a 24%, var(--sp-surface)),
        color-mix(in srgb, #4f946a 8%, var(--sp-surface))
    ) !important;
    border-color: color-mix(in srgb, #4f946a 32%, var(--sp-border)) !important;
    box-shadow: inset 3px 0 0 #4f946a !important;
    color: var(--sp-text) !important;
    font-weight: 780 !important;
}
.sp-ai-status {
    padding: 14px;
    margin: 7px 2px;
    border-radius: 15px;
    border: 1px solid var(--sp-border);
    background: var(--sp-surface);
}
.sp-ai-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.sp-ai-status-title {
    color: var(--sp-text);
    font-size: 13px;
    font-weight: 800;
}
.sp-online {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #46d875;
    box-shadow: 0 0 0 4px rgba(70,216,117,.13);
}
.sp-offline {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #f87171;
}
.sp-ai-model {
    margin-top: 7px;
    color: var(--sp-muted);
    font-size: 11px;
}
.sp-sidebar-footer {
    color: var(--sp-muted);
    text-align: center;
    padding: 18px 4px 5px 4px;
    font-size: 10px;
    line-height: 1.5;
}

@media (prefers-color-scheme: dark) {
    .sp-hero {
        background: linear-gradient(135deg, #0f3326 0%, #1d573c 58%, #476f56 100%);
    }
}
</style>
"""

st.html(CUSTOM_CSS)


# ============================================================
# TNG-STYLE MONEY COMPONENT
# ============================================================

MONEY_HTML = """
<div class="money-component">
    <label class="money-label">Total Cost (RM) <span>*</span></label>
    <div class="money-field">
        <div class="money-prefix">RM</div>
        <input
            id="smartpantry-money"
            type="text"
            inputmode="numeric"
            autocomplete="off"
            spellcheck="false"
            aria-label="Total Cost"
        />
    </div>
    <div class="money-help">
        Type numbers only: 1 → 0.01, 12 → 0.12, 123 → 1.23.
    </div>
</div>
"""

MONEY_CSS = """
.money-component {
    width: 100%;
    font-family: var(--st-font), Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.money-label {
    display: block;
    color: var(--st-text-color);
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 7px;
}
.money-label span { color: #ef4444; }
.money-field {
    width: 100%;
    height: 42px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border: 1px solid color-mix(in srgb, var(--st-text-color) 18%, transparent);
    border-radius: .5rem;
    background: var(--st-secondary-background-color);
}
.money-field:focus-within {
    border-color: var(--st-primary-color);
    box-shadow: 0 0 0 1px var(--st-primary-color);
}
.money-prefix {
    flex-shrink: 0;
    padding-left: 13px;
    padding-right: 7px;
    color: var(--st-text-color);
    font-size: 14px;
    font-weight: 700;
}
#smartpantry-money {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    border: none;
    outline: none;
    background: transparent;
    color: var(--st-text-color);
    padding: 0 13px 0 4px;
    font-family: var(--st-font), Inter, sans-serif;
    font-size: 16px;
    font-weight: 600;
    text-align: right;
    font-variant-numeric: tabular-nums;
    caret-color: transparent;
}
.money-help {
    margin-top: 5px;
    color: color-mix(in srgb, var(--st-text-color) 58%, transparent);
    font-size: 11px;
    line-height: 1.4;
}
"""

MONEY_JS = """
export default function({ parentElement, data, setStateValue }) {
    const input = parentElement.querySelector("#smartpantry-money");

    let centsValue = Number.isFinite(Number(data?.cents))
        ? Math.max(0, Math.trunc(Number(data.cents)))
        : 0;

    let digits = centsValue === 0 ? "" : String(centsValue);
    const MAX_DIGITS = 11;

    function cleanDigits(value) {
        return String(value ?? "").replace(/\\D/g, "").slice(0, MAX_DIGITS);
    }

    function formatMoney(rawDigits) {
        let raw = cleanDigits(rawDigits);

        if (raw === "") {
            return "0.00";
        }

        const padded = raw.padStart(3, "0");
        let whole = padded.slice(0, -2);
        const cents = padded.slice(-2);

        whole = String(parseInt(whole, 10) || 0);
        const formattedWhole = Number(whole).toLocaleString("en-MY");

        return formattedWhole + "." + cents;
    }

    function updateDisplay() {
        input.value = formatMoney(digits);
        requestAnimationFrame(() => {
            try {
                const end = input.value.length;
                input.setSelectionRange(end, end);
            } catch (_) {}
        });
    }

    function commit() {
        const numericCents = digits === "" ? 0 : (parseInt(digits, 10) || 0);
        updateDisplay();
        setStateValue("cents", numericCents);
    }

    updateDisplay();

    input.onkeydown = (event) => {
        const key = event.key;

        if (/^[0-9]$/.test(key)) {
            event.preventDefault();
            if (digits.length < MAX_DIGITS) {
                digits += key;
                commit();
            }
            return;
        }

        if (key === "Backspace") {
            event.preventDefault();
            digits = digits.slice(0, -1);
            commit();
            return;
        }

        if (key === "Delete" || key === "Escape") {
            event.preventDefault();
            digits = "";
            commit();
            return;
        }

        if (key === "Tab" || key === "Shift") {
            return;
        }

        if ((event.ctrlKey || event.metaKey) && ["a", "c", "v"].includes(key.toLowerCase())) {
            return;
        }

        event.preventDefault();
    };

    input.onpaste = (event) => {
        event.preventDefault();
        const pasted = event.clipboardData?.getData("text") ?? "";
        const clean = cleanDigits(pasted);

        if (clean !== "") {
            digits = clean.slice(-MAX_DIGITS);
            commit();
        }
    };

    input.onbeforeinput = (event) => {
        if (event.inputType === "insertText") {
            const value = event.data ?? "";

            if (/^[0-9]$/.test(value)) {
                event.preventDefault();
                if (digits.length < MAX_DIGITS) {
                    digits += value;
                    commit();
                }
            } else {
                event.preventDefault();
            }
        }

        if (event.inputType === "deleteContentBackward") {
            event.preventDefault();
            digits = digits.slice(0, -1);
            commit();
        }
    };

    input.onclick = input.onfocus = () => {
        const end = input.value.length;
        input.setSelectionRange(end, end);
    };
}
"""

money_component = st.components.v2.component(
    name="smartpantry_money_input",
    html=MONEY_HTML,
    css=MONEY_CSS,
    js=MONEY_JS,
)


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
    "planner_preference": "Practical everyday meals",
    "planner_servings": 2,
    "planner_time": "30 minutes",
    "auto_ai_planner": True,
    "flash_message": "",
    "active_page": "Overview",
    "cost_component_nonce": 0,
}

for key, value in DEFAULT_SESSION.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "Dairy", "Meat", "Vegetables", "Fruits", "Bakery",
    "Frozen Food", "Beverages", "Snacks", "Canned Food",
    "Dry Food", "Others",
]

UNITS = [
    "Piece", "Pack", "Bottle", "Can", "Box",
    "kg", "g", "L", "ml",
]

STORAGE_LOCATIONS = [
    "Refrigerator", "Freezer", "Pantry",
    "Kitchen Cabinet", "Others",
]

NAV_ITEMS = [
    ("Overview", "🏠"),
    ("Food Tracker", "📍"),
    ("Add Item", "➕"),
    ("Expiry Timeline", "📅"),
    ("AI Meal Planner", "✨"),
    ("Insights", "📊"),
]


# ============================================================
# SUPABASE CONFIG
# ============================================================

def db_configured():
    try:
        return all([
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_SECRET_KEY"],
            st.secrets["APP_WORKSPACE_ID"],
        ])
    except Exception:
        return False


def workspace_id():
    return str(st.secrets["APP_WORKSPACE_ID"])


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SECRET_KEY"],
    )


def db_get_pantry_items():
    response = (
        get_supabase()
        .table("pantry_items")
        .select("*")
        .eq("workspace_id", workspace_id())
        .order("created_at", desc=False)
        .execute()
    )

    rows = response.data or []

    for row in rows:
        row["id"] = str(row["id"])
        row["quantity"] = int(row["quantity"])
        row["cost"] = float(row["cost"])

    return rows


def db_insert_pantry_item(item):
    row = dict(item)
    row["workspace_id"] = workspace_id()

    response = (
        get_supabase()
        .table("pantry_items")
        .insert(row)
        .execute()
    )

    return response.data


def db_insert_pantry_items(items):
    if not items:
        return []

    rows = []

    for item in items:
        row = dict(item)
        row["workspace_id"] = workspace_id()
        rows.append(row)

    response = (
        get_supabase()
        .table("pantry_items")
        .insert(rows)
        .execute()
    )

    return response.data


def db_update_item_status(item_id, new_status):
    payload = {
        "item_status": new_status,
        "status_date": str(date.today()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    (
        get_supabase()
        .table("pantry_items")
        .update(payload)
        .eq("workspace_id", workspace_id())
        .eq("id", item_id)
        .execute()
    )


def db_delete_item(item_id):
    (
        get_supabase()
        .table("pantry_items")
        .delete()
        .eq("workspace_id", workspace_id())
        .eq("id", item_id)
        .execute()
    )


def db_clear_pantry():
    (
        get_supabase()
        .table("pantry_items")
        .delete()
        .eq("workspace_id", workspace_id())
        .execute()
    )


def db_add_activity(message):
    (
        get_supabase()
        .table("activity_log")
        .insert({
            "workspace_id": workspace_id(),
            "message": message,
        })
        .execute()
    )


def db_get_activity():
    response = (
        get_supabase()
        .table("activity_log")
        .select("*")
        .eq("workspace_id", workspace_id())
        .order("event_time", desc=True)
        .limit(40)
        .execute()
    )

    return response.data or []


def db_get_settings():
    response = (
        get_supabase()
        .table("planner_settings")
        .select("*")
        .eq("workspace_id", workspace_id())
        .limit(1)
        .execute()
    )

    rows = response.data or []

    if rows:
        return rows[0]

    default_row = {
        "workspace_id": workspace_id(),
        "meal_preference": "Practical everyday meals",
        "servings": 2,
        "max_prep_time": "30 minutes",
        "auto_ai_planner": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    (
        get_supabase()
        .table("planner_settings")
        .insert(default_row)
        .execute()
    )

    return default_row


def db_save_settings(
    meal_preference=None,
    servings=None,
    max_prep_time=None,
    auto_ai_planner=None,
):
    current = db_get_settings()

    row = {
        "workspace_id": workspace_id(),
        "meal_preference": (
            current["meal_preference"]
            if meal_preference is None
            else meal_preference
        ),
        "servings": (
            int(current["servings"])
            if servings is None
            else int(servings)
        ),
        "max_prep_time": (
            current["max_prep_time"]
            if max_prep_time is None
            else max_prep_time
        ),
        "auto_ai_planner": (
            bool(current["auto_ai_planner"])
            if auto_ai_planner is None
            else bool(auto_ai_planner)
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    (
        get_supabase()
        .table("planner_settings")
        .upsert(row, on_conflict="workspace_id")
        .execute()
    )

    return row


def db_save_ai_plan(signature, reason, plan):
    (
        get_supabase()
        .table("ai_meal_plans")
        .insert({
            "workspace_id": workspace_id(),
            "pantry_signature": signature,
            "trigger_reason": reason,
            "plan_json": plan,
        })
        .execute()
    )


def db_get_latest_ai_plan():
    response = (
        get_supabase()
        .table("ai_meal_plans")
        .select("*")
        .eq("workspace_id", workspace_id())
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    rows = response.data or []

    if not rows:
        return None

    row = rows[0]

    if isinstance(row.get("plan_json"), str):
        try:
            row["plan_json"] = json.loads(row["plan_json"])
        except Exception:
            row["plan_json"] = None

    return row


def db_replace_pantry(records):
    db_clear_pantry()

    cleaned = []

    for record in records:
        row = {
            "item_name": str(record["item_name"]),
            "category": str(record["category"]),
            "quantity": int(record["quantity"]),
            "unit": str(record["unit"]),
            "purchase_date": str(record["purchase_date"]),
            "expiry_date": str(record["expiry_date"]),
            "cost": float(record["cost"]),
            "storage": str(record["storage"]),
            "item_status": str(record.get("item_status", "Available")),
            "status_date": (
                None
                if str(record.get("status_date", "")).strip() == ""
                else str(record.get("status_date"))
            ),
        }

        record_id = str(record.get("id", "")).strip()

        try:
            uuid.UUID(record_id)
            row["id"] = record_id
        except Exception:
            pass

        cleaned.append(row)

    db_insert_pantry_items(cleaned)


def refresh_persistent_state():
    settings = db_get_settings()

    st.session_state["pantry_items"] = db_get_pantry_items()
    st.session_state["activity_log"] = db_get_activity()

    st.session_state["planner_preference"] = str(
        settings.get("meal_preference", "Practical everyday meals")
    )

    st.session_state["planner_servings"] = int(
        settings.get("servings", 2)
    )

    st.session_state["planner_time"] = str(
        settings.get("max_prep_time", "30 minutes")
    )

    st.session_state["auto_ai_planner"] = bool(
        settings.get("auto_ai_planner", True)
    )

    latest_plan = db_get_latest_ai_plan()

    if latest_plan and latest_plan.get("plan_json"):
        st.session_state["ai_meal_plan"] = latest_plan["plan_json"]
        st.session_state["ai_plan_signature"] = str(
            latest_plan.get("pantry_signature", "")
        )

        created_at = latest_plan.get("created_at")

        if created_at:
            try:
                st.session_state["ai_last_updated"] = datetime.fromisoformat(
                    str(created_at).replace("Z", "+00:00")
                )
            except Exception:
                st.session_state["ai_last_updated"] = None
    else:
        st.session_state["ai_meal_plan"] = None
        st.session_state["ai_plan_signature"] = ""


# ============================================================
# GENERAL HELPERS
# ============================================================

def page_header(kicker, title, description):
    st.html(
        f"""
        <div class="sp-kicker">{kicker}</div>
        <div class="sp-page-title">{title}</div>
        <div class="sp-page-description">{description}</div>
        """
    )


def metric_card(icon, value, label):
    st.html(
        f"""
        <div class="sp-metric-card">
            <div class="sp-metric-icon">{icon}</div>
            <div class="sp-metric-value">{value}</div>
            <div class="sp-metric-label">{label}</div>
        </div>
        """
    )


def status_badge(status):
    mapping = {
        "Fresh": ("sp-fresh", "🟢 Fresh"),
        "Use Soon": ("sp-use", "🟡 Use Soon"),
        "Expiring Soon": ("sp-soon", "🟠 Expiring Soon"),
        "Urgent": ("sp-urgent", "🔴 Urgent"),
        "Expired": ("sp-expired", "⚫ Expired"),
    }

    css_class, label = mapping.get(
        status,
        ("sp-expired", status),
    )

    st.html(
        f"""
        <span class="sp-status {css_class}">
            {label}
        </span>
        """
    )


def tng_money_input(key):
    component_state = st.session_state.get(key, {})

    if isinstance(component_state, dict):
        current_cents = int(component_state.get("cents", 0) or 0)
    else:
        current_cents = int(getattr(component_state, "cents", 0) or 0)

    result = money_component(
        data={"cents": current_cents},
        default={"cents": current_cents},
        key=key,
        on_cents_change=lambda: None,
    )

    returned_cents = int(
        getattr(result, "cents", current_cents) or 0
    )

    return returned_cents / 100


def to_date(value):
    if isinstance(value, date):
        return value

    return datetime.strptime(
        str(value),
        "%Y-%m-%d",
    ).date()


def expiry_info(expiry_date):
    days_left = (
        to_date(expiry_date)
        -
        date.today()
    ).days

    if days_left < 0:
        return days_left, "Expired", 100

    if days_left <= 2:
        return days_left, "Urgent", 90

    if days_left <= 7:
        return days_left, "Expiring Soon", 75

    if days_left <= 14:
        return days_left, "Use Soon", 40

    return days_left, "Fresh", 20


def expiry_message(days_left):
    if days_left < 0:
        number = abs(days_left)

        return (
            f"Expired {number} day"
            f"{'s' if number != 1 else ''} ago"
        )

    if days_left == 0:
        return "Expires today"

    if days_left == 1:
        return "Expires tomorrow"

    return f"Expires in {days_left} days"


def shelf_progress(item):
    purchase = to_date(item["purchase_date"])
    expiry = to_date(item["expiry_date"])

    total_days = max(
        (expiry - purchase).days,
        1,
    )

    elapsed = max(
        (date.today() - purchase).days,
        0,
    )

    progress = elapsed / total_days

    return min(
        max(progress, 0.0),
        1.0,
    )


def create_dataframe():
    rows = []

    for item in st.session_state["pantry_items"]:
        days_left, status, priority = expiry_info(
            item["expiry_date"]
        )

        rows.append({
            "ID": item["id"],
            "Food": item["item_name"],
            "Category": item["category"],
            "Quantity": item["quantity"],
            "Unit": item["unit"],
            "Purchase Date": item["purchase_date"],
            "Expiry Date": item["expiry_date"],
            "Days Left": days_left,
            "Expiry Status": status,
            "Priority": priority,
            "Cost (RM)": float(item["cost"]),
            "Storage": item["storage"],
            "Item Status": item["item_status"],
            "Status Date": item.get("status_date") or "",
        })

    return pd.DataFrame(rows)


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
            (available["Days Left"] >= 0)
            &
            (available["Days Left"] <= 2)
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

    score = max(0, min(score, 100))

    if score >= 90:
        label = "Excellent"
    elif score >= 75:
        label = "Good"
    elif score >= 50:
        label = "Needs Attention"
    else:
        label = "High Waste Risk"

    return score, label


def format_db_time(value):
    if not value:
        return ""

    try:
        dt = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        return dt.strftime(
            "%d %b %Y • %H:%M UTC"
        )
    except Exception:
        return str(value)


def clear_add_item_inputs():
    keys = [
        "add_food_name",
        "add_category",
        "add_quantity",
        "add_unit",
        "add_purchase",
        "add_expiry",
        "add_storage",
    ]

    for key in keys:
        st.session_state.pop(key, None)

    st.session_state["cost_component_nonce"] += 1


# ============================================================
# OLLAMA CLOUD
# ============================================================

def ollama_configured():
    try:
        return bool(
            st.secrets["OLLAMA_API_KEY"]
        )
    except Exception:
        return False


def get_ollama_model():
    try:
        return st.secrets.get(
            "OLLAMA_MODEL",
            "gpt-oss:120b",
        )
    except Exception:
        return "gpt-oss:120b"


SMARTPANTRY_AI_SYSTEM = """
You are SmartPantry's Autonomous Meal Planning Engine.

You are not a general chatbot.

SmartPantry itself determines:
- expiry dates
- days remaining
- lifecycle status
- food cost
- storage location
- whether food is Available, Consumed, Wasted or Expired

Treat those supplied values as authoritative.

You completely control meal planning.

For the current pantry situation determine:
1. pantry urgency;
2. food priorities;
3. between 1 and 4 meals;
4. meal order;
5. pantry ingredient allocation;
6. necessary missing ingredients;
7. practical preparation steps;
8. the next most useful action.

PRIORITY
Priority 1: 0-2 days remaining.
Priority 2: 3-7 days remaining.
Priority 3: 8-14 days remaining.
Priority 4: Long-life food.

Never recommend:
- Consumed items
- Wasted items
- Expired items

Never invent pantry ingredients.
Items not in the pantry must be listed as missing ingredients.
Minimise unnecessary purchases.
Use realistic household meals.

Do not provide dieting, weight-loss, calorie-restriction
or body-weight advice.

FOOD SAFETY
Expiry information alone does not prove food is safe.
For perishable foods remind the user to check appearance,
smell, freshness and storage condition.

Return ONLY valid JSON using this structure:

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
      "pantry_ingredients": ["ingredient"],
      "missing_ingredients": ["ingredient"],
      "preparation": ["step", "step", "step"],
      "food_safety_note": "short reminder"
    }
  ],
  "next_action": "single most useful next action"
}
"""


def ai_pantry_context():
    df = create_dataframe()

    if df.empty:
        return []

    usable = (
        df[
            (df["Item Status"] == "Available")
            &
            (df["Days Left"] >= 0)
        ]
        .sort_values("Days Left")
    )

    context = []

    for _, row in usable.iterrows():
        context.append({
            "food": row["Food"],
            "category": row["Category"],
            "quantity": row["Quantity"],
            "unit": row["Unit"],
            "days_remaining": int(row["Days Left"]),
            "expiry_status": row["Expiry Status"],
            "storage": row["Storage"],
            "cost_rm": round(
                float(row["Cost (RM)"]),
                2,
            ),
        })

    return context


def call_ollama_cloud(prompt):
    if not ollama_configured():
        return None, "Ollama Cloud is not configured."

    try:
        response = requests.post(
            "https://ollama.com/api/chat",
            headers={
                "Authorization": (
                    "Bearer "
                    +
                    st.secrets["OLLAMA_API_KEY"]
                ),
                "Content-Type": "application/json",
            },
            json={
                "model": get_ollama_model(),
                "messages": [
                    {
                        "role": "system",
                        "content": SMARTPANTRY_AI_SYSTEM,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=90,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["message"]["content"],
            None,
        )

    except requests.exceptions.Timeout:
        return None, "Ollama Cloud timed out."

    except requests.exceptions.RequestException as error:
        return None, f"Ollama request failed: {error}"

    except Exception as error:
        return None, f"Unable to read AI response: {error}"


def parse_ai_json(text):
    if not text:
        return None

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"```$",
        "",
        cleaned,
    ).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end > start:
        try:
            return json.loads(
                cleaned[start:end + 1]
            )
        except Exception:
            pass

    return None


def normalise_name(value):
    return re.sub(
        r"[^a-z0-9 ]+",
        "",
        str(value).lower(),
    ).strip()


def validate_ai_plan(plan):
    if not isinstance(plan, dict):
        return None

    current_pantry = [
        item["food"]
        for item in ai_pantry_context()
    ]

    normalised_pantry = {
        normalise_name(name): name
        for name in current_pantry
    }

    meals = plan.get("meals", [])

    if not isinstance(meals, list):
        meals = []

    cleaned_meals = []

    for meal in meals[:4]:
        if not isinstance(meal, dict):
            continue

        used = meal.get(
            "pantry_ingredients",
            [],
        )

        missing = meal.get(
            "missing_ingredients",
            [],
        )

        preparation = meal.get(
            "preparation",
            [],
        )

        if not isinstance(used, list):
            used = []

        if not isinstance(missing, list):
            missing = []

        if not isinstance(preparation, list):
            preparation = []

        valid_used = []
        cleaned_missing = [
            str(item)
            for item in missing
        ]

        for ingredient in used:
            raw = str(ingredient).strip()
            normalised = normalise_name(raw)
            matched = False

            for pantry_key, pantry_display in normalised_pantry.items():
                if (
                    normalised
                    and
                    (
                        normalised in pantry_key
                        or
                        pantry_key in normalised
                    )
                ):
                    valid_used.append(
                        pantry_display
                    )
                    matched = True
                    break

            if (
                not matched
                and
                raw
                and
                raw not in cleaned_missing
            ):
                cleaned_missing.append(raw)

        cleaned_meals.append({
            "meal_name": str(
                meal.get(
                    "meal_name",
                    "Meal",
                )
            ),
            "priority": str(
                meal.get(
                    "priority",
                    "Flexible",
                )
            ),
            "why_now": str(
                meal.get(
                    "why_now",
                    "",
                )
            ),
            "pantry_ingredients": valid_used,
            "missing_ingredients": cleaned_missing,
            "preparation": [
                str(item)
                for item in preparation
            ],
            "food_safety_note": str(
                meal.get(
                    "food_safety_note",
                    "",
                )
            ),
        })

    return {
        "situation_title": str(
            plan.get(
                "situation_title",
                "Current Pantry Plan",
            )
        ),
        "situation_level": str(
            plan.get(
                "situation_level",
                "Moderate",
            )
        ),
        "situation_summary": str(
            plan.get(
                "situation_summary",
                "",
            )
        ),
        "planner_strategy": str(
            plan.get(
                "planner_strategy",
                "",
            )
        ),
        "meals": cleaned_meals,
        "next_action": str(
            plan.get(
                "next_action",
                "Review priority food.",
            )
        ),
    }


def planner_signature():
    payload = {
        "date": str(date.today()),
        "pantry": ai_pantry_context(),
        "preference": st.session_state[
            "planner_preference"
        ],
        "servings": st.session_state[
            "planner_servings"
        ],
        "time": st.session_state[
            "planner_time"
        ],
    }

    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def generate_ai_plan(reason, force=False):
    pantry = ai_pantry_context()

    if not pantry:
        st.session_state["ai_meal_plan"] = None
        st.session_state["ai_plan_signature"] = ""
        return False

    signature = planner_signature()

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
Reason:
{reason}

Today:
{date.today()}

Current usable pantry:
{json.dumps(pantry, indent=2)}

Preference:
{st.session_state["planner_preference"]}

Servings:
{st.session_state["planner_servings"]}

Maximum preparation time:
{st.session_state["planner_time"]}

Create the best current SmartPantry meal strategy.
Return only the required JSON.
"""

    result, error = call_ollama_cloud(
        prompt
    )

    if error:
        st.session_state[
            "ai_plan_error"
        ] = error

        return False

    st.session_state[
        "ai_plan_raw"
    ] = result

    plan = validate_ai_plan(
        parse_ai_json(result)
    )

    if plan is None:
        st.session_state[
            "ai_plan_error"
        ] = (
            "SmartPantry could not "
            "read the AI response."
        )

        return False

    st.session_state[
        "ai_meal_plan"
    ] = plan

    st.session_state[
        "ai_plan_error"
    ] = None

    st.session_state[
        "ai_plan_signature"
    ] = signature

    st.session_state[
        "ai_last_updated"
    ] = datetime.now(timezone.utc)

    db_save_ai_plan(
        signature,
        reason,
        plan,
    )

    db_add_activity(
        "🤖 AI Meal Planner adapted its strategy."
    )

    st.session_state[
        "activity_log"
    ] = db_get_activity()

    return True


def automatic_ai_update():
    if not st.session_state[
        "auto_ai_planner"
    ]:
        return

    if not ollama_configured():
        return

    if not ai_pantry_context():
        return

    signature = planner_signature()

    if (
        signature
        !=
        st.session_state[
            "ai_plan_signature"
        ]
        and
        signature
        !=
        st.session_state[
            "ai_attempt_signature"
        ]
    ):
        generate_ai_plan(
            "SmartPantry detected a changed pantry situation."
        )


# ============================================================
# DEMO DATA
# ============================================================

def load_demo_data():
    today = date.today()

    sample = [
        (
            "Fresh Milk", "Dairy", 1, "Bottle",
            1, 7.50, "Refrigerator"
        ),
        (
            "Chicken Breast", "Meat", 1, "Pack",
            2, 12.00, "Refrigerator"
        ),
        (
            "Eggs", "Dairy", 8, "Piece",
            6, 8.50, "Refrigerator"
        ),
        (
            "Bread", "Bakery", 1, "Pack",
            3, 4.50, "Pantry"
        ),
        (
            "Tomatoes", "Vegetables", 4, "Piece",
            4, 5.00, "Refrigerator"
        ),
        (
            "Cheese", "Dairy", 1, "Pack",
            8, 9.50, "Refrigerator"
        ),
        (
            "Rice", "Dry Food", 2, "kg",
            120, 18.00, "Pantry"
        ),
        (
            "Carrots", "Vegetables", 3, "Piece",
            8, 4.00, "Refrigerator"
        ),
        (
            "Onions", "Vegetables", 4, "Piece",
            20, 4.50, "Pantry"
        ),
    ]

    rows = []

    for (
        name,
        category,
        quantity,
        unit,
        days,
        cost,
        storage,
    ) in sample:
        rows.append({
            "item_name": name,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "purchase_date": str(today),
            "expiry_date": str(
                today
                +
                timedelta(days=days)
            ),
            "cost": cost,
            "storage": storage,
            "item_status": "Available",
            "status_date": None,
        })

    db_insert_pantry_items(rows)

    db_add_activity(
        "🧪 Demo pantry loaded into Supabase."
    )


# ============================================================
# DATABASE STARTUP
# ============================================================

if not db_configured():
    st.error(
        "Supabase is not configured. Add SUPABASE_URL, "
        "SUPABASE_SECRET_KEY and APP_WORKSPACE_ID "
        "to Streamlit Secrets."
    )
    st.stop()

try:
    refresh_persistent_state()
except Exception as error:
    st.error(
        "SmartPantry could not connect to the Supabase database."
    )

    with st.expander(
        "Database error details"
    ):
        st.code(
            str(error)
        )

    st.stop()


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
            Track every food lifecycle, identify expiry risk,
            protect pantry value, reduce avoidable waste,
            and let an autonomous Ollama Cloud planner adapt
            your meals when circumstances change.
        </div>
    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

def save_auto_ai_setting():
    db_save_settings(
        auto_ai_planner=bool(
            st.session_state[
                "auto_ai_planner"
            ]
        )
    )


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
                ● DATABASE CONNECTED
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

    for label, icon in NAV_ITEMS:
        active = (
            st.session_state[
                "active_page"
            ]
            ==
            label
        )

        if st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type=(
                "primary"
                if active
                else
                "secondary"
            ),
        ):
            st.session_state[
                "active_page"
            ] = label

            st.rerun()

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
            key="auto_ai_planner",
            on_change=save_auto_ai_setting,
        )

        if st.session_state[
            "auto_ai_planner"
        ]:
            st.caption(
                "Automatically replans when "
                "pantry conditions change."
            )
        else:
            st.caption(
                "Automatic planning is paused."
            )

    if ollama_configured():
        st.html(
            f"""
            <div class="sp-ai-status">
                <div class="sp-ai-row">
                    <div class="sp-ai-status-title">
                        Ollama Cloud
                    </div>
                    <div class="sp-online"></div>
                </div>

                <div class="sp-ai-model">
                    Connected • {get_ollama_model()}
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
                    <div class="sp-offline"></div>
                </div>

                <div class="sp-ai-model">
                    Not configured
                </div>
            </div>
            """
        )

    sidebar_df = create_dataframe()

    if not sidebar_df.empty:
        active_food = sidebar_df[
            sidebar_df[
                "Item Status"
            ]
            ==
            "Available"
        ]

        risk_food = active_food[
            (active_food["Days Left"] >= 0)
            &
            (active_food["Days Left"] <= 7)
        ]

        st.html(
            """
            <div class="sp-sidebar-section">
                Pantry Status
            </div>
            """
        )

        s1, s2 = st.columns(2)

        s1.metric(
            "Items",
            len(active_food),
        )

        s2.metric(
            "Risk",
            len(risk_food),
        )

    if not st.session_state[
        "pantry_items"
    ]:
        st.divider()

        if st.button(
            "🧪 Load Demo Pantry",
            use_container_width=True,
        ):
            load_demo_data()

            st.session_state[
                "ai_attempt_signature"
            ] = ""

            st.session_state[
                "flash_message"
            ] = (
                "Demo pantry saved to Supabase."
            )

            st.rerun()

    st.html(
        """
        <div class="sp-sidebar-footer">
            SmartPantry Intelligence System
            <br>
            Supabase persistent storage
        </div>
        """
    )


# ============================================================
# FLASH + AUTOMATIC AI
# ============================================================

page = st.session_state[
    "active_page"
]

if st.session_state[
    "flash_message"
]:
    st.toast(
        st.session_state[
            "flash_message"
        ]
    )

    st.session_state[
        "flash_message"
    ] = ""

automatic_ai_update()


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":
    page_header(
        "Pantry Command Centre",
        "Overview",
        (
            "See what needs attention, "
            "what value is at risk, and "
            "how SmartPantry is responding."
        ),
    )

    df = create_dataframe()

    if df.empty:
        st.info(
            "Your pantry database is empty. "
            "Add your first item or load the demo pantry."
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

        attention = (
            available[
                (available["Days Left"] >= 0)
                &
                (available["Days Left"] <= 7)
            ]
            .sort_values(
                "Days Left"
            )
        )

        health, health_label = (
            pantry_health_score(df)
        )

        risk_value = attention[
            "Cost (RM)"
        ].sum()

        saved_value = consumed[
            "Cost (RM)"
        ].sum()

        pantry_value = available[
            "Cost (RM)"
        ].sum()

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
                f"## {health}/100 — {health_label}"
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
                    f"RM {risk_value:.2f}",
                )

                st.caption(
                    f"{len(attention)} item(s) "
                    f"expire within seven days."
                )

        st.divider()

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        with c1:
            metric_card(
                "🥫",
                len(available),
                "Available Items",
            )

        with c2:
            metric_card(
                "🚨",
                len(attention),
                "Need Attention",
            )

        with c3:
            metric_card(
                "💼",
                f"RM {pantry_value:.2f}",
                "Pantry Value",
            )

        with c4:
            metric_card(
                "💚",
                f"RM {saved_value:.2f}",
                "Value Saved",
            )

        st.divider()

        st.markdown(
            "### 🚨 Priority Food"
        )

        if attention.empty:
            st.success(
                "No food currently needs urgent attention."
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
                    a, b, c = st.columns(
                        [3, 2, 1]
                    )

                    with a:
                        st.markdown(
                            f"#### {row['Food']}"
                        )

                        status_badge(
                            row[
                                "Expiry Status"
                            ]
                        )

                    with b:
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

                    with c:
                        st.metric(
                            "Value",
                            f"RM "
                            f"{row['Cost (RM)']:.2f}",
                        )

        st.divider()

        st.html(
            """
            <div class="sp-ai-panel">
                <div class="sp-ai-title">
                    🤖 Autonomous Meal Intelligence
                </div>

                <div class="sp-ai-description">
                    SmartPantry uses persisted pantry data
                    from Supabase and can automatically
                    rebuild the AI meal strategy when
                    inventory conditions change.
                </div>
            </div>
            """
        )

        plan = st.session_state[
            "ai_meal_plan"
        ]

        if plan:
            st.markdown(
                "### "
                +
                plan.get(
                    "situation_title",
                    "Current AI Plan",
                )
            )

            st.write(
                "**Situation:** "
                +
                plan.get(
                    "situation_level",
                    "Moderate",
                )
            )

            st.write(
                plan.get(
                    "situation_summary",
                    "",
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

        elif st.session_state[
            "ai_plan_error"
        ]:
            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )

        st.divider()

        st.markdown(
            "### 🕘 Recent Activity"
        )

        if not st.session_state[
            "activity_log"
        ]:
            st.caption(
                "No activity yet."
            )

        else:
            for event in st.session_state[
                "activity_log"
            ][:6]:
                st.write(
                    f"**"
                    f"{format_db_time(event.get('event_time'))}"
                    f"**"
                )

                st.caption(
                    str(
                        event.get(
                            "message",
                            "",
                        )
                    )
                )


# ============================================================
# FOOD TRACKER
# ============================================================

elif page == "Food Tracker":
    page_header(
        "Lifecycle Management",
        "Food Tracker",
        (
            "Monitor every pantry item "
            "through its lifecycle."
        ),
    )

    df = create_dataframe()

    if df.empty:
        st.info(
            "No food items are stored in Supabase yet."
        )

    else:
        f1, f2, f3 = st.columns(3)

        search = f1.text_input(
            "🔍 Search food"
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
                ),
            )
        )

        status_filter = (
            f3.selectbox(
                "Lifecycle Status",
                [
                    "All",
                    "Available",
                    "Consumed",
                    "Wasted",
                ],
            )
        )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered[
                    "Food"
                ]
                .str.contains(
                    search,
                    case=False,
                    na=False,
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

        if status_filter != "All":
            filtered = filtered[
                filtered[
                    "Item Status"
                ]
                ==
                status_filter
            ]

        filtered = filtered.sort_values(
            "Days Left"
        )

        for _, row in filtered.iterrows():
            source_item = next(
                item
                for item in st.session_state[
                    "pantry_items"
                ]
                if item["id"] == row["ID"]
            )

            with st.container(
                border=True
            ):
                main_col, qty_col = (
                    st.columns(
                        [4, 1]
                    )
                )

                with main_col:
                    st.markdown(
                        f"### {row['Food']}"
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
                        f"{row['Category']} • "
                        f"{row['Storage']} • "
                        f"RM {row['Cost (RM)']:.2f}"
                    )

                with qty_col:
                    st.metric(
                        "Quantity",
                        f"{row['Quantity']} "
                        f"{row['Unit']}",
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

                    st.caption(
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
                        key=(
                            "consume_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True,
                    ):
                        db_update_item_status(
                            row["ID"],
                            "Consumed",
                        )

                        db_add_activity(
                            f"✅ {row['Food']} was consumed."
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()

                    if b2.button(
                        "🗑️ Wasted",
                        key=(
                            "waste_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True,
                    ):
                        db_update_item_status(
                            row["ID"],
                            "Wasted",
                        )

                        db_add_activity(
                            f"🗑️ {row['Food']} "
                            f"was recorded as wasted."
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()

                    if b3.button(
                        "❌ Remove",
                        key=(
                            "remove_"
                            +
                            row["ID"]
                        ),
                        use_container_width=True,
                    ):
                        db_delete_item(
                            row["ID"]
                        )

                        db_add_activity(
                            f"❌ {row['Food']} "
                            f"was removed."
                        )

                        st.session_state[
                            "ai_attempt_signature"
                        ] = ""

                        st.rerun()


# ============================================================
# ADD ITEM
# ============================================================

elif page == "Add Item":
    page_header(
        "Inventory Entry",
        "Add Food",
        (
            "Add a food item and save it "
            "directly to Supabase."
        ),
    )

    with st.container(
        border=True
    ):
        left, right = st.columns(2)

        with left:
            food_name = st.text_input(
                "Food Name *",
                placeholder=(
                    "Example: Fresh Milk"
                ),
                key="add_food_name",
            )

            category = st.selectbox(
                "Category",
                CATEGORIES,
                key="add_category",
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1,
                key="add_quantity",
            )

            unit = st.selectbox(
                "Unit",
                UNITS,
                key="add_unit",
            )

        with right:
            purchase_date = st.date_input(
                "Purchase Date",
                value=date.today(),
                key="add_purchase",
            )

            expiry_date = st.date_input(
                "Expiry Date",
                value=(
                    date.today()
                    +
                    timedelta(days=7)
                ),
                key="add_expiry",
            )

            cost_key = (
                "add_cost_component_"
                +
                str(
                    st.session_state[
                        "cost_component_nonce"
                    ]
                )
            )

            cost = tng_money_input(
                key=cost_key
            )

            storage = st.selectbox(
                "Storage",
                STORAGE_LOCATIONS,
                key="add_storage",
            )

        st.caption(
            f"Current entered cost: "
            f"**RM {cost:,.2f}**"
        )

        if st.button(
            "➕ Add to SmartPantry",
            type="primary",
            use_container_width=True,
        ):
            if not food_name.strip():
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
                    "before purchase date."
                )

            elif cost <= 0:
                st.error(
                    "Total cost must be "
                    "greater than RM 0.00."
                )

            else:
                item = {
                    "item_name": food_name.strip(),
                    "category": category,
                    "quantity": int(quantity),
                    "unit": unit,
                    "purchase_date": str(
                        purchase_date
                    ),
                    "expiry_date": str(
                        expiry_date
                    ),
                    "cost": round(
                        float(cost),
                        2,
                    ),
                    "storage": storage,
                    "item_status": "Available",
                    "status_date": None,
                }

                db_insert_pantry_item(
                    item
                )

                db_add_activity(
                    f"➕ {food_name.strip()} "
                    f"was added."
                )

                st.session_state[
                    "ai_attempt_signature"
                ] = ""

                st.session_state[
                    "flash_message"
                ] = (
                    f"{food_name.strip()} "
                    f"saved to Supabase."
                )

                clear_add_item_inputs()

                st.session_state[
                    "active_page"
                ] = "Food Tracker"

                st.rerun()


# ============================================================
# EXPIRY TIMELINE
# ============================================================

elif page == "Expiry Timeline":
    page_header(
        "Time-Based Tracking",
        "Expiry Timeline",
        (
            "See foods organised "
            "by expiry urgency."
        ),
    )

    df = create_dataframe()

    if df.empty:
        st.info(
            "No tracked food."
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
                ],
            ),
            (
                "🔴 Today",
                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    0
                ],
            ),
            (
                "🟠 Tomorrow",
                available[
                    available[
                        "Days Left"
                    ]
                    ==
                    1
                ],
            ),
            (
                "🟡 Next 7 Days",
                available[
                    (available["Days Left"] >= 2)
                    &
                    (available["Days Left"] <= 7)
                ],
            ),
            (
                "🟢 Later",
                available[
                    available[
                        "Days Left"
                    ]
                    >
                    7
                ],
            ),
        ]

        for title, group in groups:
            st.markdown(
                f"### {title}"
            )

            if group.empty:
                st.caption(
                    "No items."
                )

            else:
                for _, row in group.iterrows():
                    with st.container(
                        border=True
                    ):
                        c1, c2, c3 = (
                            st.columns(
                                [3, 2, 1]
                            )
                        )

                        c1.markdown(
                            f"**{row['Food']}**"
                        )

                        c1.caption(
                            f"{row['Category']} • "
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

elif page == "AI Meal Planner":
    page_header(
        "Ollama Cloud",
        "Autonomous Meal Planner",
        (
            "The AI uses persistent Supabase "
            "inventory to control the current "
            "meal strategy."
        ),
    )

    st.html(
        """
        <div class="sp-ai-panel">
            <div class="sp-ai-title">
                ✨ AI-Controlled Meal Strategy
            </div>

            <div class="sp-ai-description">
                Meal selection automatically adapts
                to the pantry stored in Supabase,
                expiry risk and planner preferences.
            </div>
        </div>
        """
    )

    with st.expander(
        "⚙️ Planner Preferences"
    ):
        preference = st.text_input(
            "Meal Preference",
            value=st.session_state[
                "planner_preference"
            ],
            key="planner_pref_widget",
        )

        servings = st.number_input(
            "Servings",
            min_value=1,
            max_value=8,
            value=st.session_state[
                "planner_servings"
            ],
            key="planner_servings_widget",
        )

        time_options = [
            "15 minutes",
            "30 minutes",
            "45 minutes",
            "60 minutes",
        ]

        current_time = (
            st.session_state[
                "planner_time"
            ]
        )

        selected_time = st.selectbox(
            "Maximum Preparation Time",
            time_options,
            index=(
                time_options.index(
                    current_time
                )
                if current_time
                in time_options
                else 1
            ),
            key="planner_time_widget",
        )

        if st.button(
            "Save & Recalculate",
            type="primary",
            use_container_width=True,
            key="save_planner_settings",
        ):
            saved = db_save_settings(
                meal_preference=(
                    preference.strip()
                    or
                    "Practical everyday meals"
                ),
                servings=int(servings),
                max_prep_time=selected_time,
                auto_ai_planner=st.session_state[
                    "auto_ai_planner"
                ],
            )

            st.session_state[
                "planner_preference"
            ] = saved[
                "meal_preference"
            ]

            st.session_state[
                "planner_servings"
            ] = int(
                saved[
                    "servings"
                ]
            )

            st.session_state[
                "planner_time"
            ] = saved[
                "max_prep_time"
            ]

            st.session_state[
                "ai_attempt_signature"
            ] = ""

            db_add_activity(
                "⚙️ AI planner preferences "
                "were updated."
            )

            st.rerun()

    pantry = ai_pantry_context()

    if not pantry:
        st.warning(
            "No usable non-expired "
            "food is available."
        )

    else:
        r1, r2 = st.columns(
            [1, 2]
        )

        with r1:
            if st.button(
                "🔄 Re-plan Now",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(
                    "Ollama Cloud is "
                    "analysing the pantry..."
                ):
                    generate_ai_plan(
                        "The user requested "
                        "a fresh plan.",
                        force=True,
                    )

                st.rerun()

        with r2:
            if st.session_state[
                "ai_last_updated"
            ]:
                last_updated = (
                    st.session_state[
                        "ai_last_updated"
                    ]
                )

                st.info(
                    "Last AI adaptation: "
                    +
                    last_updated.strftime(
                        "%d %b %Y • %H:%M UTC"
                    )
                )
            else:
                st.info(
                    f"{len(pantry)} usable "
                    f"item(s) available "
                    f"for planning."
                )

        if st.session_state[
            "ai_plan_error"
        ]:
            st.warning(
                st.session_state[
                    "ai_plan_error"
                ]
            )

            if st.session_state[
                "ai_plan_raw"
            ]:
                with st.expander(
                    "Technical AI response"
                ):
                    st.code(
                        st.session_state[
                            "ai_plan_raw"
                        ]
                    )

        plan = st.session_state[
            "ai_meal_plan"
        ]

        if plan:
            st.divider()

            st.metric(
                "Situation",
                plan.get(
                    "situation_level",
                    "Moderate",
                ),
            )

            st.markdown(
                "### "
                +
                plan.get(
                    "situation_title",
                    "Current Plan",
                )
            )

            st.write(
                plan.get(
                    "situation_summary",
                    "",
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

            meals = plan.get(
                "meals",
                [],
            )

            st.markdown(
                f"### 🍽️ "
                f"{len(meals)} "
                f"AI-Selected Meal(s)"
            )

            for number, meal in enumerate(
                meals,
                start=1,
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
                            f"### {number}. "
                            f"{meal.get('meal_name', 'Meal')}"
                        )

                    with priority_col:
                        st.caption(
                            "PRIORITY"
                        )

                        st.write(
                            "**"
                            +
                            meal.get(
                                "priority",
                                "Flexible",
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
                            "",
                        )
                    )

                    i1, i2 = (
                        st.columns(2)
                    )

                    with i1:
                        st.markdown(
                            "#### 🥕 Pantry Items"
                        )

                        pantry_items = (
                            meal.get(
                                "pantry_ingredients",
                                [],
                            )
                        )

                        if pantry_items:
                            for ingredient in pantry_items:
                                st.write(
                                    "✓ "
                                    +
                                    str(
                                        ingredient
                                    )
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
                                [],
                            )
                        )

                        if missing:
                            for ingredient in missing:
                                st.write(
                                    "• "
                                    +
                                    str(
                                        ingredient
                                    )
                                )
                        else:
                            st.success(
                                "Nothing extra needed."
                            )

                    preparation = (
                        meal.get(
                            "preparation",
                            [],
                        )
                    )

                    if preparation:
                        with st.expander(
                            "👨‍🍳 Preparation"
                        ):
                            for index, step in enumerate(
                                preparation,
                                start=1,
                            ):
                                st.write(
                                    f"{index}. {step}"
                                )

                    note = meal.get(
                        "food_safety_note",
                        "",
                    )

                    if note:
                        st.caption(
                            "Food safety: "
                            +
                            note
                        )

            st.success(
                "✅ **Next Action:** "
                +
                plan.get(
                    "next_action",
                    "Review priority food.",
                )
            )


# ============================================================
# INSIGHTS
# ============================================================

elif page == "Insights":
    page_header(
        "Performance Analytics",
        "Insights",
        (
            "Track food saved, waste, "
            "pantry performance and backups."
        ),
    )

    df = create_dataframe()

    if df.empty:
        st.info(
            "Add pantry data first."
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
            len(consumed)
            +
            len(wasted)
        )

        avoidance = (
            len(consumed)
            /
            completed
            *
            100
            if completed
            else 0
        )

        saved_value = consumed[
            "Cost (RM)"
        ].sum()

        waste_cost = wasted[
            "Cost (RM)"
        ].sum()

        x1, x2, x3, x4 = (
            st.columns(4)
        )

        with x1:
            metric_card(
                "🌱",
                len(consumed),
                "Food Saved",
            )

        with x2:
            metric_card(
                "💚",
                f"RM {saved_value:.2f}",
                "Value Saved",
            )

        with x3:
            metric_card(
                "🗑️",
                f"RM {waste_cost:.2f}",
                "Waste Cost",
            )

        with x4:
            metric_card(
                "📈",
                f"{avoidance:.1f}%",
                "Waste Avoidance",
            )

        st.divider()

        if completed:
            outcome_df = pd.DataFrame({
                "Outcome": [
                    "Consumed",
                    "Wasted",
                ],
                "Items": [
                    len(consumed),
                    len(wasted),
                ],
            })

            fig = px.pie(
                outcome_df,
                names="Outcome",
                values="Items",
                hole=.5,
                title=(
                    "Food Lifecycle Outcomes"
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                theme="streamlit",
            )

        if not available.empty:
            category_df = (
                available
                .groupby(
                    "Category"
                )
                .size()
                .reset_index(
                    name="Items"
                )
            )

            fig2 = px.bar(
                category_df,
                x="Category",
                y="Items",
                title=(
                    "Available Pantry by Category"
                ),
            )

            st.plotly_chart(
                fig2,
                use_container_width=True,
                theme="streamlit",
            )

        st.divider()

        st.markdown(
            "### 💾 Pantry Backup"
        )

        backup_df = pd.DataFrame(
            st.session_state[
                "pantry_items"
            ]
        )

        export_columns = [
            "id",
            "item_name",
            "category",
            "quantity",
            "unit",
            "purchase_date",
            "expiry_date",
            "cost",
            "storage",
            "item_status",
            "status_date",
        ]

        for column in export_columns:
            if column not in backup_df.columns:
                backup_df[column] = ""

        csv = (
            backup_df[
                export_columns
            ]
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )

        st.download_button(
            "⬇️ Download Backup",
            data=csv,
            file_name=(
                "smartpantry_backup.csv"
            ),
            mime="text/csv",
        )

        uploaded = st.file_uploader(
            "Restore Backup",
            type=["csv"],
        )

        if uploaded is not None:
            try:
                restored = pd.read_csv(
                    uploaded
                )

                required = {
                    "item_name",
                    "category",
                    "quantity",
                    "unit",
                    "purchase_date",
                    "expiry_date",
                    "cost",
                    "storage",
                    "item_status",
                }

                if not required.issubset(
                    set(
                        restored.columns
                    )
                ):
                    st.error(
                        "This is not a valid "
                        "SmartPantry backup."
                    )

                elif st.button(
                    "♻️ Restore Pantry",
                    type="primary",
                ):
                    records = (
                        restored
                        .fillna("")
                        .to_dict(
                            orient="records"
                        )
                    )

                    db_replace_pantry(
                        records
                    )

                    db_add_activity(
                        "♻️ Pantry backup restored."
                    )

                    st.session_state[
                        "ai_plan_signature"
                    ] = ""

                    st.session_state[
                        "ai_attempt_signature"
                    ] = ""

                    st.session_state[
                        "flash_message"
                    ] = (
                        "Pantry backup restored."
                    )

                    st.rerun()

            except Exception as error:
                st.error(
                    "Unable to restore "
                    f"backup: {error}"
                )
