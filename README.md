# 🍱 UPD Kiosk Weekly Meal Planner

A **Streamlit web app** that uses **Mixed Integer Linear Programming (MILP)** to generate an optimized weekly meal plan from UP Diliman campus kiosks — maximizing calories within your budget and nutrient constraints.

> **Math 180.1 Project** — By: Chua, Gerundiano, Gutierrez, Mariano (*Data Driven Students - DDS*)

---

## Live Demo

You can access our deployed Streamlit application [here](https://upd-kiosk-meal-planner-myuifkxrjoqcb9z4quahtq.streamlit.app/).



---

## Features

- **MILP Optimization** via [PuLP](https://coin-or.github.io/pulp/) (with scipy HiGHS fallback) to find the best weekly meal plan
- **Customizable constraints**: budget, nutrient limits, meals per day, kiosk locations, and more
- **Weekly schedule view** with per-slot calorie targets and notes
- **Visual analytics**: calorie breakdown by food type, spend by kiosk, and a nutrient radar chart
- **Dataset browser** to explore all available items before running the planner

---

## Project Structure

```
.
├── meal_planner.py          # Main Streamlit application
├── Math 180.1 Dataset.xlsx  # Menu dataset (kiosk items + nutrition info)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Setup & Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run meal_planner.py
```

Make sure `Math 180.1 Dataset.xlsx` is in the **same folder** as `meal_planner.py`.

---

## How It Works

The app formulates a **MILP problem** where:

- **Decision variables** represent how many times each menu item (a la carte, combo, meal, or drink) appears in the weekly plan
- **Objective**: Maximize total weekly calories
- **Constraints**: weekly budget, max sugar/fat/sodium, min protein, min total calories, exact drink count, and duplicate limits

The solver uses **PuLP with CBC** (or scipy HiGHS as fallback) to find an integer-feasible solution.

---

## Weekly Scheduler

After the MILP determines what items to select and how many times, the scheduler assigns them across days and meal slots.

- **Expand quantities**: Each item is duplicated based on how many times it appears, forming a pool of servings.
- **Prioritize calories**: Items are sorted by calories (highest first) so heavier meals are placed earlier.
- **Slot-first assignment**: Meal slots are filled by priority (e.g., lunch → breakfast → others) across all days before moving to the next slot. This spreads calories more evenly throughout the week.
- **Even drink spacing**: Drinks are distributed across days as evenly as possible to avoid clustering.

---


## Dataset Columns

The dataset (`Math 180.1 Dataset.xlsx`) contains the following columns:

| Column         | Description                                      |
|----------------|--------------------------------------------------|
| `location`     | Kiosk name (e.g., `imath`, `sub_che`, `cal`)     |
| `menu_item`    | Item name                                        |
| `menu_type`    | Type: `a_la_carte`, `combo`, `meal`, or `drink`  |
| `carbs`        | Carb component (for combo and meal items)        |
| `item_1–3`     | Additional components (for combo and meal items) |
| `drink`        | Drink included (for combo and meal items)        |
| `sugar_g`      | Sugar content (grams)                            |
| `protein_g`    | Protein content (grams)                          |
| `fat_g`        | Fat content (grams)                              |
| `sodium_mg`    | Sodium content (milligrams)                      |
| `calories_kcal`| Caloric value (kcal)                             |
| `price`        | Price in Philippine Peso (PHP)                   |

> ⚠️ **Note for users**: You currently need to know or estimate the nutrient values for your constraints (sugar, fat, sodium, protein, calories). The sidebar defaults are good starting points for a typical college student's weekly intake.

---

## Known Limitations & Suggested Improvements

### 1. ❌ Infeasible Solutions
-
Auto-relaxation has been implemented. When no feasible solution exists, it automatically relaxes constraints (10%, 20%, 30%) until a solution is found. However, there are still cases when infeasible solutions would still occur.
---

## Dependencies

See `requirements.txt`. Key packages:

- `streamlit` — web app framework
- `pulp` — MILP solver
- `scipy` — LP fallback solver (HiGHS)
- `pandas` / `openpyxl` — data loading
- `plotly` / `matplotlib` — interactive charts

---

## License

This project was created for academic purposes (Math 180.1, UP Diliman). Feel free to fork and adapt.
