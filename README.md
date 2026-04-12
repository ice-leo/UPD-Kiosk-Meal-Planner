# 🍱 UPD Kiosk Weekly Meal Planner

A **Streamlit web app** that uses **Mixed Integer Linear Programming (MILP)** to generate an optimized weekly meal plan from UP Diliman campus kiosks — maximizing calories within your budget and nutrient constraints.

> **Math 180.1 Project** — By: Chua, Gerundiano, Gutierrez, Mariano (*Data Driven Students - DDS*)

---

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]([https://your-app-name.streamlit.app](https://upd-kiosk-meal-planner-myuifkxrjoqcb9z4quahtq.streamlit.app/))

> 🔗 Replace the link above with your actual Streamlit Cloud URL after deployment.

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

### 1. 🧃 Drinks Placement in the Schedule
Currently, the LP Model may suggest drinks whose location is separate from the meal. A planned improvement is to include a constraint such that the location of the drinks must be identical to at least one of the location of the meals.

### 2. 📏 Nutrient Constraints Require Prior Knowledge
The app requires users to manually input weekly targets for sugar, fat, sodium, protein, and calories. Most students won't know these values off the top of their heads. A future improvement would be to:
- Add **preset profiles** (e.g., "Light eater", "Active student", "Bulking") that auto-fill reasonable defaults
- Display **recommended daily values (RDV)** as tooltips or hints next to each input
- Allow users to input their **weight, height, and activity level** to auto-calculate personalized targets

### 3. ❌ Infeasible Solutions
The solver can return **no feasible solution** when constraints are too tight — for example, if the budget is low but calorie minimums are high, or if the duplicate limit is 1 but there aren't enough unique items to fill the week. The app currently displays a list of manual fixes. A future version could:
- **Auto-relax constraints** iteratively until a feasible solution is found (e.g., loosen budget by 10%, then 20%, etc.)
- **Suggest the minimum budget** needed to satisfy the current nutrient goals
- **Highlight which constraint is causing the infeasibility** instead of listing all possible fixes
- Use sensitivity analysis to show **how close each constraint is to the feasibility boundary**

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
