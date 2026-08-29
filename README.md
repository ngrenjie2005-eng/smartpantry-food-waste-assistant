# 🥕 SmartPantry

## AI-Powered Food Lifecycle Tracking and Autonomous Meal Planning System

SmartPantry is an experimental web-based pantry management system that combines food tracking, expiry monitoring, cloud database storage, data analytics, and artificial intelligence.

The project was designed out of an interest in exploring how AI can be combined with everyday household activities in a practical way.

Instead of only recording food items, SmartPantry attempts to understand the current pantry situation and react when circumstances change.

For example:

```text
Food added
    ↓
Expiry risk calculated
    ↓
Priority foods identified
    ↓
AI evaluates current pantry
    ↓
Meal strategy generated
    ↓
Food consumed / wasted
    ↓
Pantry situation changes
    ↓
AI automatically re-evaluates
```

The system currently combines:

- **Streamlit** for the web interface
- **Supabase PostgreSQL** for persistent cloud storage
- **Ollama Cloud** for AI meal planning
- **Pandas** for data processing
- **Plotly** for visual analytics
- **JavaScript** for custom interactive components

---

# 🌱 Why SmartPantry?

Household food can easily be forgotten inside refrigerators, freezers, and kitchen cabinets.

Even when people know what ingredients they have, they may still be unsure about:

- Which food should be used first
- Which food is approaching expiry
- How much food value may be wasted
- What meals can be prepared using current ingredients
- Which ingredients are missing
- Whether a meal plan should change after pantry conditions change

SmartPantry explores the idea of combining traditional pantry tracking with an adaptive AI assistant.

The goal is not only to display inventory, but also to make the stored data useful for decisions.

---

# ✨ Current Features

## 🏠 Pantry Overview

The Overview page acts as the main SmartPantry command centre.

It displays information such as:

- Pantry Health Score
- Available food items
- Food requiring attention
- Pantry value
- Value at risk
- Value saved
- Priority food
- Latest AI strategy
- Recent pantry activity

The dashboard automatically updates according to the latest database information.

---

# 🌿 Pantry Health Score

SmartPantry calculates a simple Pantry Health Score from **0 to 100**.

The score considers factors such as:

- Urgent food
- Expired food
- Recorded food waste

Example interpretation:

| Score | Status |
|---|---|
| 90–100 | Excellent |
| 75–89 | Good |
| 50–74 | Needs Attention |
| Below 50 | High Waste Risk |

The score is intended as a quick summary indicator rather than a scientific measurement.

---

# 📍 Food Tracker

The Food Tracker manages the lifecycle of pantry items.

Each food record can contain:

- Food name
- Category
- Quantity
- Unit
- Purchase date
- Expiry date
- Storage location
- Cost
- Expiry status
- Lifecycle status

Users can:

- Search food
- Filter by category
- Filter by lifecycle status
- Mark food as consumed
- Mark food as wasted
- Remove food records

Current lifecycle states are:

```text
Available
Consumed
Wasted
```

---

# 🚦 Expiry Risk Classification

SmartPantry calculates the number of days remaining before each food item expires.

The current classification logic is:

| Days Remaining | Status |
|---|---|
| Already expired | ⚫ Expired |
| 0–2 days | 🔴 Urgent |
| 3–7 days | 🟠 Expiring Soon |
| 8–14 days | 🟡 Use Soon |
| More than 14 days | 🟢 Fresh |

This allows food requiring attention to appear before longer-life food.

---

# ➕ Add Food

Users can manually add pantry items.

Information currently collected includes:

- Food name
- Category
- Quantity
- Unit
- Purchase date
- Expiry date
- Total cost
- Storage location

The system validates several conditions before saving the item.

Examples include:

```text
Food name cannot be empty

Expiry date cannot be earlier than purchase date

Total cost must be greater than RM 0.00
```

After validation, the food is stored directly in the Supabase PostgreSQL database.

---

# 💳 Digital Wallet-Style Cost Input

SmartPantry includes a custom amount entry component inspired by digital wallet interfaces.

Instead of manually entering the decimal point, the last two digits are always treated as cents.

Example:

```text
Type: 1

RM 0.01
```

Continue typing:

```text
Type: 2

RM 0.12
```

Then:

```text
Type: 3

RM 1.23
```

Then:

```text
Type: 4

RM 12.34
```

Backspace performs the reverse operation:

```text
RM 12.34
    ↓
Backspace
    ↓
RM 1.23
```

The component is implemented using:

```text
Streamlit Components v2
HTML
CSS
JavaScript
```

---

# 📅 Expiry Timeline

The Expiry Timeline provides a time-oriented view of pantry inventory.

Food is grouped into:

```text
⚫ Expired

🔴 Today

🟠 Tomorrow

🟡 Next 7 Days

🟢 Later
```

This provides another way to identify which ingredients should receive attention first.

---

# 🤖 Autonomous AI Meal Planner

SmartPantry integrates **Ollama Cloud** as its AI meal planning engine.

The AI receives structured information about the current usable pantry.

Example information includes:

```text
Food name
Category
Quantity
Unit
Storage
Days remaining
Expiry status
Cost
```

The AI can determine:

- Pantry urgency
- Food priorities
- Number of meals
- Meal order
- Pantry ingredients to use
- Missing ingredients
- Preparation steps
- Food safety reminders
- Recommended next action

Depending on the current situation, SmartPantry can request between **1 and 4 meals**.

---

# 🧠 AI Priority Logic

The AI is instructed to prioritise food based on expiry urgency.

```text
Priority 1
0–2 days remaining

Priority 2
3–7 days remaining

Priority 3
8–14 days remaining

Priority 4
Long-life food
```

The intended goal is to make better use of food that may otherwise be wasted.

---

# 🔄 Automatic AI Replanning

One of the experimental features of SmartPantry is automatic AI replanning.

When automatic planning is enabled:

```text
Pantry changes
      ↓
SmartPantry detects a different situation
      ↓
Pantry signature changes
      ↓
Ollama Cloud receives updated pantry information
      ↓
A new meal strategy is generated
      ↓
The new plan is stored in Supabase
```

Possible triggers include:

- New food added
- Food consumed
- Food wasted
- Food removed
- Food becoming more urgent
- Date changes
- Planner preferences changing

This allows the meal planner to react to changes instead of producing only a one-time recommendation.

---

# 🔐 AI Pantry Controls

The AI is instructed not to recommend:

```text
Consumed food
Wasted food
Expired food
```

SmartPantry also performs additional validation on AI-generated pantry ingredients.

The system separates ingredients into:

### Pantry Ingredients

Food that currently exists and is usable in SmartPantry.

### Missing / Optional Ingredients

Food that is not currently available but may be required for a suggested meal.

This helps reduce cases where the AI incorrectly treats a missing ingredient as existing inventory.

---

# ⚙️ AI Planner Preferences

Users can modify several AI planning settings.

Current options include:

- Meal preference
- Number of servings
- Maximum preparation time
- Automatic planning

Example:

```text
Meal Preference:
Quick simple meals

Servings:
2

Maximum Preparation Time:
15 minutes
```

These settings are stored in Supabase and remain available after restarting the application.

---

# 📊 Insights and Analytics

The Insights page provides simple information about food usage and wastage.

Current indicators include:

## Food Saved

Number of food items marked as consumed.

## Value Saved

Total value of food recorded as consumed.

## Waste Cost

Total value of food recorded as wasted.

## Waste Avoidance Rate

Calculated using:

```text
                    Consumed Food
Waste Avoidance = ------------------------- × 100
                  Consumed + Wasted Food
```

Example:

```text
Consumed = 4
Wasted = 1

Waste Avoidance
= 4 / 5 × 100
= 80%
```

---

# 📈 Visual Analytics

Current visualisations include:

- Food lifecycle outcomes
- Available pantry items by category

Charts are created using **Plotly**.

---

# 💾 Persistent Database Storage

SmartPantry uses **Supabase PostgreSQL** for persistent storage.

The database currently stores:

```text
Pantry inventory
Food lifecycle status
Activity history
AI meal plans
Planner preferences
```

This means information does not depend only on the current Streamlit session.

Data can remain available after:

- Refreshing the webpage
- Closing the browser
- Restarting Streamlit
- Redeploying the application

---

# 🗄️ Database Structure

SmartPantry currently uses four main tables.

---

## `pantry_items`

Stores pantry inventory.

Main fields include:

```text
id
workspace_id
item_name
category
quantity
unit
purchase_date
expiry_date
cost
storage
item_status
status_date
created_at
updated_at
```

---

## `activity_log`

Stores important actions performed inside SmartPantry.

Examples include:

```text
Food added
Food consumed
Food wasted
Food removed
Demo pantry loaded
AI plan regenerated
Planner settings changed
Backup restored
```

Main fields include:

```text
id
workspace_id
message
event_time
```

---

## `ai_meal_plans`

Stores AI meal planning history.

Main fields include:

```text
id
workspace_id
pantry_signature
trigger_reason
plan_json
created_at
```

The generated AI meal strategy is stored as JSON.

---

## `planner_settings`

Stores AI planner configuration.

Main fields include:

```text
workspace_id
meal_preference
servings
max_prep_time
auto_ai_planner
updated_at
```

---

# 🔑 Workspace System

The current SmartPantry version uses a simple workspace identifier.

Example:

```text
smartpantry-personal-2026
```

Every related database record contains a:

```text
workspace_id
```

This allows pantry information to be grouped together.

The current implementation does not yet include full user authentication.

---

# 💾 Backup and Restore

SmartPantry supports CSV pantry backup.

Users can download:

```text
smartpantry_backup.csv
```

The backup includes information such as:

```text
Food name
Category
Quantity
Unit
Purchase date
Expiry date
Cost
Storage
Lifecycle status
```

The system also supports restoring pantry information from a compatible backup.

Current restore workflow:

```text
CSV uploaded
      ↓
File validated
      ↓
Current pantry records replaced
      ↓
Backup records inserted into Supabase
      ↓
SmartPantry reloads
```

---

# 🌗 Light and Dark Mode

SmartPantry supports Streamlit Light and Dark appearance modes.

The custom interface uses theme-aware variables for:

- Backgrounds
- Text
- Sidebar
- Cards
- Borders
- Inputs

The green SmartPantry banner remains consistent as part of the application design.

---

# 🎨 Interface Design

The interface uses a dashboard-style layout.

Main navigation currently includes:

```text
🏠 Overview

📍 Food Tracker

➕ Add Item

📅 Expiry Timeline

✨ AI Meal Planner

📊 Insights
```

The sidebar also displays:

- Database connection status
- Ollama Cloud status
- Automatic planning control
- Number of available items
- Number of at-risk items

---

# 🏗️ System Architecture

```text
                       SmartPantry
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
      Streamlit Web UI                Ollama Cloud
             │                             │
             │                     AI Meal Planning
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                    Supabase PostgreSQL
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
     Pantry Items      Activity Log       AI Meal Plans
                                                 │
                                                 ▼
                                         Planner Settings
```

---

# 🔄 Main System Workflow

```text
User adds food
      ↓
Input validation
      ↓
Food stored in Supabase
      ↓
SmartPantry reads updated inventory
      ↓
Expiry risk calculated
      ↓
Priority food identified
      ↓
Pantry signature generated
      ↓
Ollama Cloud receives usable pantry
      ↓
AI generates meal strategy
      ↓
AI plan stored in Supabase
      ↓
Food is consumed / wasted
      ↓
Database lifecycle changes
      ↓
Pantry situation changes
      ↓
AI may automatically re-plan
      ↓
Analytics update
```

---

# 🛠️ Technology Stack

## Application

```text
Python
Streamlit
```

## Interface

```text
HTML
CSS
JavaScript
Streamlit Components v2
```

## Database

```text
Supabase
PostgreSQL
```

## Artificial Intelligence

```text
Ollama Cloud
gpt-oss:120b
```

## Data Processing

```text
Pandas
```

## Data Visualisation

```text
Plotly
```

## API Communication

```text
Requests
REST API
JSON
```

## Deployment

```text
GitHub
Streamlit Community Cloud
```

---

# 📂 Project Structure

```text
smartpantry-food-waste-assistant/
│
├── streamlit_app.py
├── requirements.txt
├── supabase_schema.sql
└── README.md
```

---

# ⚙️ Installation

## 1. Download or Clone the Project

You can download the repository directly from GitHub or clone it using:

```bash
git clone YOUR_REPOSITORY_URL
```

Move into the project directory:

```bash
cd smartpantry-food-waste-assistant
```

---

# 📦 Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

Current dependencies include:

```text
streamlit>=1.60.0
pandas>=2.2.0
plotly>=5.24.0
requests>=2.32.0
supabase>=2.15.0
```

---

# 🗄️ Supabase Setup

## Step 1 — Create a Supabase Project

Create a new Supabase project.

---

## Step 2 — Create the Database

Open:

```text
Supabase
→ SQL Editor
→ New Query
```

Copy the contents of:

```text
supabase_schema.sql
```

Run the SQL script.

The following tables should be created:

```text
pantry_items
activity_log
ai_meal_plans
planner_settings
```

---

# 🔐 Required Configuration

SmartPantry requires several secret values.

For Streamlit Community Cloud:

```text
Manage App
→ Settings
→ Secrets
```

Add:

```toml
SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"

SUPABASE_SECRET_KEY = "YOUR_SUPABASE_SECRET_KEY"

APP_WORKSPACE_ID = "smartpantry-personal-2026"

OLLAMA_API_KEY = "YOUR_OLLAMA_API_KEY"

OLLAMA_MODEL = "gpt-oss:120b"
```

---

# ⚠️ Security

Never upload real secret credentials to a public repository.

Do not commit:

```text
Supabase Secret Key
Ollama API Key
Database Password
```

Keep sensitive credentials inside:

```text
Streamlit Secrets
Environment Variables
```

If running locally, make sure any local secrets file is excluded using `.gitignore`.

---

# 🤖 Ollama Cloud Setup

SmartPantry currently uses Ollama Cloud for the AI meal planning feature.

Required values:

```toml
OLLAMA_API_KEY = "YOUR_OLLAMA_API_KEY"

OLLAMA_MODEL = "gpt-oss:120b"
```

The selected model can be changed without modifying the main application logic.

---

# ▶️ Running the Application

Run:

```bash
streamlit run streamlit_app.py
```

Streamlit will provide a local address that can be opened in a browser.

---

# ☁️ Deployment

The current deployment architecture is:

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
SmartPantry
   ↓
Supabase PostgreSQL
   +
Ollama Cloud
```

Application files can remain inside GitHub while API credentials are stored separately inside Streamlit Secrets.

---

# 🧪 Demo Pantry

If the database is empty, SmartPantry can load a sample pantry.

Current sample foods include:

| Food | Category |
|---|---|
| Fresh Milk | Dairy |
| Chicken Breast | Meat |
| Eggs | Dairy |
| Bread | Bakery |
| Tomatoes | Vegetables |
| Cheese | Dairy |
| Rice | Dry Food |
| Carrots | Vegetables |
| Onions | Vegetables |

The demo pantry is inserted into Supabase.

Because the records are persistent, repeatedly pressing the demo button may create duplicate records.

---

# 🧪 Suggested Testing

A basic system test can include the following.

## Database Persistence

```text
Add food
    ↓
Confirm record in Supabase
    ↓
Refresh SmartPantry
    ↓
Confirm food remains
```

---

## Expiry Classification

Test items with:

```text
Expired date
0 days remaining
1 day remaining
3 days remaining
8 days remaining
20 days remaining
```

Expected results:

```text
Expired    → ⚫ Expired

0–2 days   → 🔴 Urgent

3–7 days   → 🟠 Expiring Soon

8–14 days  → 🟡 Use Soon

15+ days   → 🟢 Fresh
```

---

## Lifecycle Testing

Test:

```text
Available
    ↓
Consumed
```

and:

```text
Available
    ↓
Wasted
```

Confirm both SmartPantry and Supabase reflect the new state.

---

## AI Testing

Generate a meal plan and verify that:

- Available ingredients can be used
- Consumed ingredients are excluded
- Wasted ingredients are excluded
- Expired ingredients are excluded
- Missing ingredients are separated
- Expiring food receives higher priority

---

## Automatic Replanning Test

```text
Generate AI plan
      ↓
Consume important ingredient
      ↓
Pantry signature changes
      ↓
AI generates new strategy
      ↓
New AI plan stored
```

---

## Database Persistence Test

Close the application and reopen it.

The following should remain:

```text
Pantry items
Lifecycle status
Activity history
Planner settings
Latest AI meal plan
```

---

# 🚀 Possible Future Improvements

SmartPantry is still an experimental project and there are many areas that could be explored further.

Possible improvements include:

### User Authentication

Integrate Supabase Authentication so different users have separate pantry data.

### Multiple Household Support

Allow multiple users to share the same household pantry.

### Barcode Scanning

Add food automatically by scanning product barcodes.

### Receipt Recognition

Use OCR or document processing to identify food items from shopping receipts.

### Automatic Shelf-Life Estimation

Estimate typical shelf life using food information databases.

### Smarter Quantity Tracking

Allow partial consumption such as:

```text
Milk

1 L
↓
Used 250 ml
↓
Remaining 750 ml
```

### Quantity-Aware Meal Planning

Allow the AI to consider exact ingredient quantities when planning several meals.

### Notifications

Send reminders when food is approaching expiry.

### Shopping List Generation

Automatically generate shopping lists based on:

- Missing ingredients
- Pantry shortages
- Planned meals
- Frequently used food

### Mobile Optimisation

Improve the interface further for smartphones.

### Better AI Evaluation

Evaluate generated meal plans based on:

- Pantry grounding
- Practicality
- Expiry prioritisation
- Consistency
- Ingredient accuracy
- Waste reduction potential

### Additional AI Models

Compare different Ollama models and allow model selection from the interface.

### Recipe Database Integration

Combine AI suggestions with structured recipe databases.

---

# ⚠️ Development Status

SmartPantry is an **experimental project that is still being developed and improved**.

The current version may contain:

- Incomplete features
- Unexpected behaviour
- Bugs
- UI inconsistencies
- Simplified calculations
- Experimental AI behaviour
- Features that may change in future versions

The system should therefore not be considered a finished or perfect production application.

SmartPantry is mainly an exploration of how several technologies can work together:

```text
Web Application
+
Cloud Database
+
Data Analytics
+
Generative AI
+
Automation
```

Some implementations may also be redesigned as better approaches are discovered.

---

# 🔧 Download, Modify and Experiment

Anyone interested in the idea is welcome to:

```text
Download the project
Fork the repository
Modify the interface
Change the database structure
Use another AI model
Add new functions
Fix existing issues
Experiment with different approaches
```

The project is intended to be flexible rather than treated as a final fixed product.

You can download the repository from GitHub and modify:

```text
streamlit_app.py
```

to change most application behaviour.

You can also modify:

```text
supabase_schema.sql
```

to experiment with different database structures.

The Ollama model can be changed through:

```toml
OLLAMA_MODEL = "YOUR_MODEL"
```

This makes it possible to experiment with different models without redesigning the entire application.

---

# 💡 Project Direction

SmartPantry started from a simple question:

> Can a normal pantry tracker become more useful if it can understand changes and react automatically?

The current system explores that idea through:

```text
Tracking
    +
Database
    +
Expiry Analysis
    +
AI Planning
    +
Automatic Replanning
```

The project may continue changing as new ideas, technologies, or better implementation methods are explored.

---

# 📌 Current Development Status

```text
Core Pantry Tracking         ✅ Implemented

Supabase Integration          ✅ Implemented

Persistent Database Storage   ✅ Implemented

Food Lifecycle Management     ✅ Implemented

Expiry Monitoring             ✅ Implemented

Digital Wallet Cost Input     ✅ Implemented

Ollama Cloud Integration      ✅ Implemented

AI Meal Planner               ✅ Implemented

Automatic AI Replanning       ✅ Implemented

AI Plan Persistence           ✅ Implemented

Planner Settings Storage      ✅ Implemented

Activity History              ✅ Implemented

Analytics                     ✅ Implemented

Backup / Restore              ✅ Implemented

Light / Dark Theme            ✅ Implemented

User Authentication           🔧 Not Implemented

Barcode Scanning              🔧 Not Implemented

Notifications                 🔧 Not Implemented

Mobile-Specific UI            🔧 Future Improvement
```

---

# 📜 Disclaimer

SmartPantry is an experimental software project.

The application may contain incomplete features, bugs, inaccurate outputs, or behaviour that changes during future development.

AI-generated meal suggestions are intended only as general planning ideas.

Expiry dates alone cannot determine whether food is safe to consume.

Users should always consider:

- Storage conditions
- Appearance
- Smell
- Freshness
- Packaging condition
- Normal food safety practices

before deciding whether food is suitable for consumption.

The source code can be downloaded and modified for experimentation, learning, improvement, or further development.
