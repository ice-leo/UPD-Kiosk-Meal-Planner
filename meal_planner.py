# =============================================================================
#  UP Diliman Kiosk Weekly Meal Planner  —  Streamlit App
#  Math 180.1 Project
#
#  Run with:  streamlit run meal_planner.py
#  Dataset :  Math 180.1 Dataset.xlsx  (must be in the same folder)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UPD Kiosk Meal Planner",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f8f5f0; }

    /* Force all main text to be dark, overriding System/Dark mode */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp span, .stApp div, .stApp label, .stApp li {
        color: #1a1a1a;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #7b1113 0%, #4a0a0b 100%);
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { 
        color: #fff !important; 
    }
    [data-testid="stSidebar"] .stSlider > div > div { background: rgba(255,255,255,0.3); }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #7b1113, #c0392b);
        color: white !important;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 18px 0 10px 0;
        letter-spacing: 0.5px;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #7b1113;
        margin-bottom: 10px;
    }
    .metric-card h3 { margin: 0; font-size: 0.85rem; color: #666 !important; text-transform: uppercase; }
    .metric-card p  { margin: 4px 0 0 0; font-size: 1.6rem; font-weight: 800; color: #2d2d2d !important; }

    /* Day card */
    .day-card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        border-top: 4px solid #7b1113;
    }
    .day-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #7b1113 !important;
        margin-bottom: 12px;
    }
    .slot-row {
        display: flex;
        align-items: flex-start;
        padding: 9px 0;
        border-bottom: 1px solid #f0ece8;
    }
    .slot-label {
        width: 110px;
        font-weight: 700;
        color: #555 !important;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .slot-item { flex: 1; }
    .item-name {
        font-weight: 700;
        font-size: 1rem;
        color: #1a1a1a !important;
        text-transform: capitalize;
    }
    .item-meta {
        font-size: 0.8rem;
        color: #888 !important;
        margin-top: 2px;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-alacarte  { background: #fff3e0; color: #e65100 !important; }
    .badge-combo     { background: #e8f5e9; color: #1b5e20 !important; }
    .badge-meal      { background: #e3f2fd; color: #0d47a1 !important; }
    .badge-drink     { background: #fce4ec; color: #880e4f !important; }
    .note-good  { color: #2e7d32 !important; font-size: 0.8rem; }
    .note-high  { color: #e65100 !important; font-size: 0.8rem; }
    .note-low   { color: #1565c0 !important; font-size: 0.8rem; }
    .day-total {
        margin-top: 10px;
        padding-top: 8px;
        font-size: 0.85rem;
        color: #555 !important;
        display: flex;
        gap: 20px;
    }
    .tip-box {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        border-radius: 6px;
        padding: 10px 16px;
        margin: 6px 0;
        font-size: 0.9rem;
        color: #4a4a1a !important;
    }
    .infeasible-box {
        background: #ffebee;
        border-left: 5px solid #c62828;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 20px;
        color: #c62828 !important;
    }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ═════════════════════════════════════════════════════════════════════════════

DATASET_FILE = "Math 180.1 Dataset.xlsx"
EXPECTED_COLS = [
    "location", "menu_item", "menu_type", "carbs",
    "item_1", "item_2", "item_3", "drink",
    "sugar_g", "protein_g", "fat_g", "sodium_mg", "calories_kcal", "price",
]
ALL_LOCATIONS = ["imath", "sub_che", "gyudfood", "cal", "stat", "arki", "palma_psych", "plaridel"]
ALL_DAYS      = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(DATASET_FILE)
    if not path.exists():
        return None
    df = pd.read_excel(path, header=0)

    # Rename columns to expected names if needed
    if "location" not in df.columns:
        n = min(len(EXPECTED_COLS), len(df.columns))
        df.columns = list(EXPECTED_COLS[:n]) + list(df.columns[n:])

    # Keep only the 14 expected columns (drop stray unnamed columns)
    present = [c for c in EXPECTED_COLS if c in df.columns]
    df = df[present].copy()

    # Add any missing expected columns as default values
    for c in EXPECTED_COLS:
        if c not in df.columns:
            df[c] = 0 if c in ("sugar_g","protein_g","fat_g","sodium_mg","calories_kcal","price") else "none"

    # Clean string columns
    str_cols = ["location","menu_item","menu_type","carbs","item_1","item_2","item_3","drink"]
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip().str.lower().replace("nan", "none")

    # Clean numeric columns
    num_cols = ["sugar_g","protein_g","fat_g","sodium_mg","calories_kcal","price"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df


# ═════════════════════════════════════════════════════════════════════════════
#  MILP SOLVER
# ═════════════════════════════════════════════════════════════════════════════

def solve_milp(
    df: pd.DataFrame,
    weekly_budget: float,
    n_days: int,
    meals_per_day: int,
    max_sugar: float,
    max_fat: float,
    max_sodium: float,
    min_protein: float,
    min_calories_total: float,
    num_drinks: int,
    max_duplicates: int,
) -> dict:
    """
    Solves the MILP using scipy linprog (LP relaxation with rounding).
    For true integer results we use PuLP which supports MILP natively.
    Falls back gracefully if PuLP is unavailable.
    """
    M = n_days * meals_per_day

    F  = df.index[df.menu_type == "a_la_carte"].tolist()
    D  = df.index[df.menu_type == "drink"].tolist()
    C  = df.index[df.menu_type == "combo"].tolist()
    Me = df.index[df.menu_type == "meal"].tolist()

    nF, nD, nC, nMe = len(F), len(D), len(C), len(Me)
    nVars = nF + nD + nC + nMe + nC   # x, d, y, m, z

    # Index slices (0-based)
    ix = list(range(0, nF))
    id_ = list(range(nF, nF+nD))
    iy = list(range(nF+nD, nF+nD+nC))
    im = list(range(nF+nD+nC, nF+nD+nC+nMe))
    iz = list(range(nF+nD+nC+nMe, nVars))

    # ── Helper: get column values for index subsets ──────────────────────────
    def col(name, idx):
        return df.loc[idx, name].values.astype(float)

    # ── Objective: maximise calories ─────────────────────────────────────────
    c_obj = np.zeros(nVars)
    c_obj[ix]  = col("calories_kcal", F)
    c_obj[id_] = col("calories_kcal", D)
    c_obj[iy]  = col("calories_kcal", C)
    c_obj[im]  = col("calories_kcal", Me)
    # Negate for minimisation (linprog minimises)
    c_neg = -c_obj

    # ── Build inequality constraints Ax ≤ b ──────────────────────────────────
    A_ub_rows, b_ub_rows = [], []

    def add_ineq(row_vals, rhs):
        A_ub_rows.append(row_vals)
        b_ub_rows.append(rhs)

    # 2) Budget
    r = np.zeros(nVars)
    r[ix]=col("price",F); r[id_]=col("price",D); r[iy]=col("price",C); r[im]=col("price",Me)
    add_ineq(r, weekly_budget)

    # 3a) Sugar
    r = np.zeros(nVars)
    r[ix]=col("sugar_g",F); r[id_]=col("sugar_g",D); r[iy]=col("sugar_g",C); r[im]=col("sugar_g",Me)
    add_ineq(r, max_sugar)

    # 3b) Fat
    r = np.zeros(nVars)
    r[ix]=col("fat_g",F); r[id_]=col("fat_g",D); r[iy]=col("fat_g",C); r[im]=col("fat_g",Me)
    add_ineq(r, max_fat)

    # 3c) Sodium
    r = np.zeros(nVars)
    r[ix]=col("sodium_mg",F); r[id_]=col("sodium_mg",D); r[iy]=col("sodium_mg",C); r[im]=col("sodium_mg",Me)
    add_ineq(r, max_sodium)

    # 3d) Protein ≥ min  → -protein ≤ -min
    r = np.zeros(nVars)
    r[ix]=-col("protein_g",F); r[id_]=-col("protein_g",D); r[iy]=-col("protein_g",C); r[im]=-col("protein_g",Me)
    add_ineq(r, -min_protein)

    # 3e) Total calories ≥ min_calories  → -calories ≤ -min
    r = np.zeros(nVars)
    r[ix]=-col("calories_kcal",F); r[id_]=-col("calories_kcal",D); r[iy]=-col("calories_kcal",C); r[im]=-col("calories_kcal",Me)
    add_ineq(r, -min_calories_total)

    # 5) Duplicate limits
    for i, fi in enumerate(ix):
        r = np.zeros(nVars); r[fi] = 1; add_ineq(r, max_duplicates)
    for i, di in enumerate(id_):
        r = np.zeros(nVars); r[di] = 1; add_ineq(r, max_duplicates)
    for i, yi in enumerate(iy):
        r = np.zeros(nVars); r[yi] = 1; add_ineq(r, max_duplicates)
    for i, mi in enumerate(im):
        r = np.zeros(nVars); r[mi] = 1; add_ineq(r, max_duplicates)

    # 6) Combo-component exclusion (Big-M)
    bigM = M
    food_name_map  = {df.loc[f_idx,"menu_item"]: i for i, f_idx in enumerate(F)}
    meal_name_map  = {df.loc[m_idx,"menu_item"]: i for i, m_idx in enumerate(Me)}
    comp_cols = ["carbs","item_1","item_2","item_3","drink"]

    for k, c_idx in enumerate(C):
        components = []
        for cc in comp_cols:
            val = df.loc[c_idx, cc]
            if val and val != "none":
                components.append(val)
        for comp in components:
            if comp in food_name_map:
                r = np.zeros(nVars)
                r[ix[food_name_map[comp]]] = 1
                r[iz[k]] = bigM
                add_ineq(r, bigM)
            elif comp in meal_name_map:
                r = np.zeros(nVars)
                r[im[meal_name_map[comp]]] = 1
                r[iz[k]] = bigM
                add_ineq(r, bigM)
        # Linking: y_k ≤ bigM * z_k
        r = np.zeros(nVars)
        r[iy[k]] = 1; r[iz[k]] = -bigM
        add_ineq(r, 0)

    A_ub = np.array(A_ub_rows) if A_ub_rows else np.empty((0, nVars))
    b_ub = np.array(b_ub_rows) if b_ub_rows else np.array([])

    # ── Equality constraints ──────────────────────────────────────────────────
    A_eq_rows, b_eq_rows = [], []

    # 1) Meal count
    r = np.zeros(nVars)
    r[ix] = 1; r[iy] = 1; r[im] = 1
    A_eq_rows.append(r); b_eq_rows.append(M)

    # 4) Exact drinks
    r = np.zeros(nVars)
    r[id_] = 1
    A_eq_rows.append(r); b_eq_rows.append(num_drinks)

    A_eq = np.array(A_eq_rows)
    b_eq = np.array(b_eq_rows)

    # ── Bounds ────────────────────────────────────────────────────────────────
    bounds = [(0, None)] * nVars
    for zi in iz:
        bounds[zi] = (0, 1)   # z binary
    if num_drinks == 0:
        for di in id_:
            bounds[di] = (0, 0)

    # ── Try PuLP for true integer solution ───────────────────────────────────
    try:
        import pulp

        prob = pulp.LpProblem("MealPlanner", pulp.LpMaximize)

        # Variables
        x_vars = [pulp.LpVariable(f"x_{i}", lowBound=0, cat="Integer") for i in range(nF)]
        d_vars = [pulp.LpVariable(f"d_{i}", lowBound=0, upBound=(0 if num_drinks==0 else None), cat="Integer") for i in range(nD)]
        y_vars = [pulp.LpVariable(f"y_{i}", lowBound=0, cat="Integer") for i in range(nC)]
        m_vars = [pulp.LpVariable(f"m_{i}", lowBound=0, cat="Integer") for i in range(nMe)]
        z_vars = [pulp.LpVariable(f"z_{i}", lowBound=0, upBound=1, cat="Binary") for i in range(nC)]

        all_vars = x_vars + d_vars + y_vars + m_vars + z_vars

        # Objective
        prob += pulp.lpDot(c_obj.tolist(), all_vars)

        # Inequality constraints
        for row, rhs in zip(A_ub_rows, b_ub_rows):
            prob += pulp.lpDot(row.tolist(), all_vars) <= rhs

        # Equality constraints
        for row, rhs in zip(A_eq_rows, b_eq_rows):
            prob += pulp.lpDot(row.tolist(), all_vars) == rhs

        prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60))

        if pulp.LpStatus[prob.status] not in ("Optimal", "Feasible"):
            return {"feasible": False, "reason": pulp.LpStatus[prob.status]}

        sol = np.array([v.varValue or 0 for v in all_vars])

    except ImportError:
        # Fallback: LP relaxation via scipy, then round
        res = linprog(
            c_neg,
            A_ub=A_ub, b_ub=b_ub,
            A_eq=A_eq, b_eq=b_eq,
            bounds=bounds,
            method="highs",
            options={"time_limit": 60},
        )
        if res.status != 0:
            reasons = {1:"Iteration limit", 2:"Infeasible", 3:"Unbounded", 4:"Numerical error"}
            return {"feasible": False, "reason": reasons.get(res.status, f"Status {res.status}")}
        sol = np.round(res.x)

    sol = np.round(sol).astype(int)
    sol = np.clip(sol, 0, None)

    # ── Extract results ───────────────────────────────────────────────────────
    sel_food  = sol[ix]
    sel_drink = sol[id_]
    sel_combo = sol[iy]
    sel_meal  = sol[im]

    quantities  = np.concatenate([sel_food, sel_drink, sel_combo, sel_meal])
    indices_all = F + D + C + Me
    types_all   = (["a_la_carte"]*nF + ["drink"]*nD + ["combo"]*nC + ["meal"]*nMe)

    rows = []
    for q, idx, tp in zip(quantities, indices_all, types_all):
        if q > 0:
            row = df.loc[idx].to_dict()
            row["quantity"] = int(q)
            row["type"]     = tp
            rows.append(row)

    result_df = pd.DataFrame(rows) if rows else pd.DataFrame()
    if not result_df.empty:
        result_df["total_cost"] = result_df["quantity"] * result_df["price"]
        result_df["total_cal"]  = result_df["quantity"] * result_df["calories_kcal"]

    def wtd(col_name):
        return float(np.dot(quantities, [df.loc[i, col_name] for i in indices_all]))

    return {
        "feasible":       True,
        "result_df":      result_df,
        "total_calories": wtd("calories_kcal"),
        "total_cost":     wtd("price"),
        "total_sugar":    wtd("sugar_g"),
        "total_protein":  wtd("protein_g"),
        "total_fat":      wtd("fat_g"),
        "total_sodium":   wtd("sodium_mg"),
        "M":              M,
        "nF": nF, "nD": nD, "nC": nC, "nMe": nMe,
        "sel_food": sel_food, "sel_drink": sel_drink,
        "sel_combo": sel_combo, "sel_meal": sel_meal,
    }


# ═════════════════════════════════════════════════════════════════════════════
#  SCHEDULE BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def build_schedule(result_df: pd.DataFrame, n_days: int, meals_per_day: int,
                   meal_labels: list, num_drinks: int, selected_days: list) -> list:
    """Returns list of dicts per day, each with 'slots' and optionally 'drink'."""
    if result_df.empty or n_days == 0:
        return []

    food_df  = result_df[result_df["type"] != "drink"].copy()
    drink_df = result_df[result_df["type"] == "drink"].copy()

    # Expand by quantity
    food_pool  = food_df.loc[food_df.index.repeat(food_df["quantity"])].reset_index(drop=True)
    drink_pool = drink_df.loc[drink_df.index.repeat(drink_df["quantity"])].reset_index(drop=True)

    # Sort food by calories descending (high-cal → midday slot)
    food_pool = food_pool.sort_values("calories_kcal", ascending=False).reset_index(drop=True)

    # Build slot-visit order: slot-2 (lunch) first across all days, then slot-1, then slot-3+
    if meals_per_day >= 2:
        priority_slots = [1, 0] + list(range(2, meals_per_day))  # 0-indexed; slot 1 = lunch
    else:
        priority_slots = [0]

    slot_order = []
    for s in priority_slots:
        if s < meals_per_day:
            for d in range(n_days):
                slot_order.append((d, s))

    # Assign food items to slots
    schedule = [[None] * meals_per_day for _ in range(n_days)]
    for k, (d, s) in enumerate(slot_order):
        if k < len(food_pool):
            schedule[d][s] = food_pool.iloc[k].to_dict()

    # Assign drinks across days
    n_drinks = min(num_drinks, len(drink_pool))
    spacing = max(1, n_days // max(n_drinks, 1))
    day_drinks = {}
    for k in range(n_drinks):
        d = min(k * spacing, n_days - 1)
        day_drinks[d] = drink_pool.iloc[k].to_dict()

    # Build day-level list based on explicitly selected days
    days = []
    for d in range(n_days):
        day_name = selected_days[d]
        day_info = {
            "name":   day_name,
            "slots":  [{"label": meal_labels[s], "item": schedule[d][s]}
                       for s in range(meals_per_day)],
            "drink":  day_drinks.get(d),
        }
        days.append(day_info)
    return days


# ═════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def fmt_name(name: str) -> str:
    return name.replace("_", " ").title() if name else ""

def badge_html(tp: str) -> str:
    cls = {"a_la_carte":"badge-alacarte","combo":"badge-combo",
           "meal":"badge-meal","drink":"badge-drink"}.get(tp, "badge-alacarte")
    label = {"a_la_carte":"A La Carte","combo":"Combo",
             "meal":"Meal","drink":"Drink"}.get(tp, tp)
    return f'<span class="badge {cls}">{label}</span>'

def cal_note(item_cal: float, target_cal: float) -> str:
    diff = item_cal - target_cal
    if diff > 150:
        return '<span class="note-high">↑ High calorie — save room for later!</span>'
    elif diff < -150:
        return '<span class="note-low">↓ Light meal — consider a snack later.</span>'
    return '<span class="note-good">✓ Good fit for this slot.</span>'

def nutrient_bar(label: str, value: float, limit: float, unit: str,
                 is_min: bool = False, color: str = "#7b1113"):
    pct = min(value / limit * 100, 100) if limit > 0 else 0
    status = "✓" if (value >= limit if is_min else value <= limit) else "✗"
    bar_color = "#2e7d32" if status == "✓" else "#c62828"
    st.markdown(f"""<div style="margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;font-size:0.85rem;font-weight:600;color:#1a1a1a;">
    <span>{label}</span>
    <span style="color:{bar_color}">{status} {value:,.1f} / {limit:,} {unit}</span>
  </div>
  <div style="background:#e0e0e0;border-radius:4px;height:8px;margin-top:3px">
    <div style="background:{bar_color};width:{pct:.1f}%;height:8px;border-radius:4px;transition:width 0.3s"></div>
  </div>
</div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

def main():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""<div style="text-align:center;padding:20px 0 8px 0">
  <h1 style="color:#7b1113;font-size:2.2rem;margin:0">🍱 UPD Kiosk Meal Planner</h1>
  <p style="color:#1a1a1a;font-size:1rem;margin:6px 0 0 0">
    Math 180.1 — Mixed Integer Linear Programming Project<br>
    <em>By: Chua, Gerundiano, Gutierrez, Mariano - Data Driven Students (DDS)</em>
  </p>
</div>
<hr style="border:none;border-top:2px solid #7b1113;margin:10px 0 20px 0">""", unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    df_all = load_data()
    if df_all is None:
        st.error(f"❌ **Dataset not found.** Make sure `{DATASET_FILE}` is in the same folder as this script.")
        st.info("Put the file here: `" + str(Path(DATASET_FILE).resolve()) + "`")
        st.stop()

    # ── Sidebar: User Inputs ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Planner Settings")
        st.markdown("---")

        st.markdown("### 📅 Schedule")
        
        # New feature: specific multiselect days instead of continuous N days
        selected_days = st.multiselect(
            "Select days on campus",
            ALL_DAYS,
            default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        
        # Sort the days chronologically to make sure the schedule makes sense
        selected_days = sorted(selected_days, key=lambda x: ALL_DAYS.index(x))
        n_days = len(selected_days)
        
        meals_per_day = st.slider("Meals per day", 1, 4, 3)

        st.markdown("### 🏷️ Meal Slot Names")
        default_labels = ["Breakfast", "Lunch", "Merienda", "Dinner"]
        meal_labels = []
        for i in range(meals_per_day):
            label = st.text_input(
                f"Slot {i+1} name",
                value=default_labels[i] if i < len(default_labels) else f"Meal {i+1}",
                key=f"label_{i}",
            )
            meal_labels.append(label)

        st.markdown("### 🎯 Calorie Targets per Slot (kcal)")
        default_targets = [400, 600, 350, 300]
        cal_targets = []
        for i in range(meals_per_day):
            t = st.number_input(
                f"{meal_labels[i]} target (kcal)",
                min_value=50, max_value=2000,
                value=default_targets[i] if i < len(default_targets) else 400,
                step=50, key=f"cal_target_{i}",
            )
            cal_targets.append(t)

        st.markdown("### 💰 Budget & Drinks")
        weekly_budget = st.number_input("Weekly budget (PHP)", 50, 5000, 750, step=50)
        
        # Max drinks automatically matches total meals to prevent slider errors
        max_drinks = max(1, n_days * meals_per_day)
        num_drinks = st.slider("Drinks per week", 0, max_drinks, min(3, max_drinks))

        st.markdown("### 🥗 Nutrient Constraints (weekly)")
        max_sugar   = st.number_input("Max sugar (g)",   0, 5000, 700,   step=50)
        max_fat     = st.number_input("Max fat (g)",     0, 2000, 400,   step=50)
        max_sodium  = st.number_input("Max sodium (mg)", 0, 50000, 12000, step=500)
        min_protein = st.number_input("Min protein (g)", 0, 500,   20,    step=5)
        min_cals    = st.number_input("Min total calories (kcal)", 0, 30000, 7000, step=500)

        st.markdown("### 🔁 Duplicate Limit")
        
        # Max dupes automatically matches total meals
        max_items = max(1, n_days * meals_per_day)
        max_dup = st.slider(
            "Max times same item can appear",
            1, max_items, min(2, max_items),
            help="1 = unique items only; higher = allow repeats"
        )

        st.markdown("### 📍 Allowed Kiosks")
        loc_options = sorted(df_all["location"].unique().tolist())
        selected_locs = st.multiselect(
            "Select kiosks",
            options=loc_options,
            default=loc_options,
        )

        st.markdown("---")
        run_btn = st.button("🚀 Run Meal Planner", type="primary", use_container_width=True)

    # ── Dataset Preview (always visible) ─────────────────────────────────────
    with st.expander("📋 Browse Full Dataset", expanded=False):
        filter_loc  = st.multiselect("Filter by location", options=loc_options, default=loc_options, key="browse_loc")
        filter_type = st.multiselect("Filter by type", options=["a_la_carte","drink","combo","meal"],
                                     default=["a_la_carte","drink","combo","meal"], key="browse_type")
        preview_df = df_all[df_all["location"].isin(filter_loc) & df_all["menu_type"].isin(filter_type)].copy()
        preview_df["menu_item"] = preview_df["menu_item"].apply(fmt_name)
        st.dataframe(preview_df[["location","menu_item","menu_type","calories_kcal",
                                  "price","protein_g","fat_g","sugar_g","sodium_mg"]],
                     use_container_width=True, height=300)
        st.caption(f"Showing {len(preview_df)} items")

    # ── Guards ───────────────────────────────────────────────────────────────
    if not run_btn:
        st.markdown("""<div style="text-align:center;padding:60px 20px;color:#1a1a1a;">
  <div style="font-size:4rem">🍱</div>
  <p style="font-size:1.1rem">Configure your settings in the sidebar, then click <strong>Run Meal Planner</strong>.</p>
</div>""", unsafe_allow_html=True)
        return

    if not selected_locs:
        st.error("Please select at least one kiosk location.")
        return
        
    if n_days == 0:
        st.error("Please select at least one day on campus in the schedule settings.")
        return

    # ── Filter dataset ────────────────────────────────────────────────────────
    df = df_all[df_all["location"].isin(selected_locs)].reset_index(drop=True)
    if df.empty:
        st.error("No items found for selected locations.")
        return

    M = n_days * meals_per_day

    # ── Run solver ────────────────────────────────────────────────────────────
    with st.spinner("🔍 Solving the MILP... this may take a few seconds."):
        result = solve_milp(
            df=df,
            weekly_budget=weekly_budget,
            n_days=n_days,
            meals_per_day=meals_per_day,
            max_sugar=max_sugar,
            max_fat=max_fat,
            max_sodium=max_sodium,
            min_protein=min_protein,
            min_calories_total=min_cals,
            num_drinks=num_drinks,
            max_duplicates=max_dup,
        )

    # ── Infeasibility handling ────────────────────────────────────────────────
    if not result["feasible"]:
        st.markdown(f"""<div class="infeasible-box">
  <h3 style="color:#c62828 !important;margin:0 0 8px 0">❌ No feasible solution found</h3>
  <p style="margin:0;color:#c62828 !important;">Solver status: <strong>{result.get('reason','Unknown')}</strong></p>
  <hr style="border-color:#ffcdd2;margin:10px 0">
  <p style="margin:0;font-size:0.9rem;color:#c62828 !important;"><strong>Try these fixes:</strong></p>
  <ul style="margin:6px 0 0 0;font-size:0.9rem;color:#c62828 !important;">
    <li>Increase the <strong>weekly budget</strong></li>
    <li>Increase <strong>max duplicates</strong> (currently {max_dup})</li>
    <li>Raise the <strong>nutrient limits</strong> (sugar / fat / sodium)</li>
    <li>Lower <strong>min protein</strong> or <strong>min calories</strong></li>
    <li>Add more <strong>kiosk locations</strong></li>
    <li>Reduce <strong>number of days</strong> or <strong>meals per day</strong></li>
  </ul>
</div>""", unsafe_allow_html=True)
        return

    result_df = result["result_df"]

    # ─────────────────────────────────────────────────────────────────────────
    #  TAB LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📋 Selected Items", "🗓️ Weekly Schedule", "💡 Tips & Charts"])

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 1 — SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-header">📊 Optimisation Results</div>', unsafe_allow_html=True)

        # Top metric cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
  <h3>Total Calories</h3>
  <p>{result['total_calories']:,.0f} kcal</p>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
  <h3>Total Cost</h3>
  <p>PHP {result['total_cost']:,.2f}</p>
</div>""", unsafe_allow_html=True)
        with c3:
            budget_left = weekly_budget - result["total_cost"]
            st.markdown(f"""<div class="metric-card">
  <h3>Budget Remaining</h3>
  <p>PHP {budget_left:,.2f}</p>
</div>""", unsafe_allow_html=True)
        with c4:
            avg_daily = result["total_calories"] / n_days if n_days else 0
            st.markdown(f"""<div class="metric-card">
  <h3>Avg Daily Calories</h3>
  <p>{avg_daily:,.0f} kcal</p>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">🥦 Nutrient Totals vs Limits</div>', unsafe_allow_html=True)

        col_n1, col_n2 = st.columns(2)
        with col_n1:
            nutrient_bar("Sugar",   result["total_sugar"],   max_sugar,   "g")
            nutrient_bar("Fat",     result["total_fat"],     max_fat,     "g")
        with col_n2:
            nutrient_bar("Sodium",  result["total_sodium"],  max_sodium,  "mg")
            nutrient_bar("Protein", result["total_protein"], min_protein, "g", is_min=True)

        # Verification checklist
        st.markdown('<div class="section-header">✅ Constraint Verification</div>', unsafe_allow_html=True)

        checks = [
            ("Meal slots filled",    sum(result["sel_food"])+sum(result["sel_combo"])+sum(result["sel_meal"]) == M,
             f"{sum(result['sel_food'])+sum(result['sel_combo'])+sum(result['sel_meal'])} / {M}"),
            ("Drinks",               sum(result["sel_drink"]) == num_drinks,
             f"{sum(result['sel_drink'])} / {num_drinks}"),
            ("Within budget",        result["total_cost"] <= weekly_budget,
             f"PHP {result['total_cost']:.2f} / {weekly_budget:.2f}"),
            ("Sugar ≤ limit",        result["total_sugar"] <= max_sugar,
             f"{result['total_sugar']:.1f} / {max_sugar} g"),
            ("Fat ≤ limit",          result["total_fat"] <= max_fat,
             f"{result['total_fat']:.1f} / {max_fat} g"),
            ("Sodium ≤ limit",       result["total_sodium"] <= max_sodium,
             f"{result['total_sodium']:.1f} / {max_sodium} mg"),
            ("Protein ≥ minimum",    result["total_protein"] >= min_protein,
             f"{result['total_protein']:.1f} / {min_protein} g"),
            ("Calories ≥ minimum",   result["total_calories"] >= min_cals,
             f"{result['total_calories']:.0f} / {min_cals} kcal"),
        ]

        cc1, cc2 = st.columns(2)
        for i, (label, ok, detail) in enumerate(checks):
            col = cc1 if i % 2 == 0 else cc2
            with col:
                icon = "✅" if ok else "❌"
                color = "#2e7d32" if ok else "#c62828"
                st.markdown(f"""<div style="display:flex;align-items:center;padding:6px 0;border-bottom:1px solid #f0ece8;font-size:0.9rem">
  <span style="font-size:1.1rem;margin-right:8px">{icon}</span>
  <span style="flex:1;color:#1a1a1a">{label}</span>
  <span style="color:{color};font-weight:600">{detail}</span>
</div>""", unsafe_allow_html=True)

        # Variety stats
        st.markdown('<div class="section-header">🔢 Item Variety</div>', unsafe_allow_html=True)
        v1, v2, v3, v4 = st.columns(4)
        for col_el, cat, sel in [
            (v1, "A La Carte", result["sel_food"]),
            (v2, "Drinks",     result["sel_drink"]),
            (v3, "Combos",     result["sel_combo"]),
            (v4, "Meals",      result["sel_meal"]),
        ]:
            with col_el:
                st.metric(cat, f"{int(sum(sel > 0))} unique", f"{int(sum(sel))} total")

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 2 — SELECTED ITEMS TABLE
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-header">📋 Optimal Item Selection</div>', unsafe_allow_html=True)

        if result_df.empty:
            st.info("No items selected.")
        else:
            display_df = result_df[[
                "location","menu_item","type","quantity",
                "price","calories_kcal","protein_g","fat_g","sugar_g","sodium_mg",
                "total_cost","total_cal"
            ]].copy()
            display_df["menu_item"] = display_df["menu_item"].apply(fmt_name)
            display_df.columns = [
                "Location","Item","Type","Qty",
                "Price (PHP)","Calories","Protein (g)","Fat (g)","Sugar (g)","Sodium (mg)",
                "Total Cost","Total Cal"
            ]

            st.dataframe(
                display_df.style
                    .format({"Price (PHP)": "₱{:.2f}", "Total Cost": "₱{:.2f}",
                             "Calories": "{:.0f}", "Total Cal": "{:.0f}",
                             "Protein (g)": "{:.1f}", "Fat (g)": "{:.1f}",
                             "Sugar (g)": "{:.1f}", "Sodium (mg)": "{:.0f}"})
                    .bar(subset=["Total Cal"], color="#e57373"),
                use_container_width=True,
                height=400,
            )

            # Totals row
            totals = display_df[["Total Cost","Total Cal","Protein (g)","Fat (g)","Sugar (g)","Sodium (mg)"]].sum()
            st.markdown(f"""<div style="background:#fff3f3;border-radius:8px;padding:12px 18px;display:flex;gap:30px;flex-wrap:wrap;font-size:0.9rem;margin-top:8px;color:#1a1a1a;">
  <span>💰 <strong>Total: ₱{totals['Total Cost']:.2f}</strong></span>
  <span>🔥 <strong>{totals['Total Cal']:.0f} kcal</strong></span>
  <span>💪 Protein: <strong>{totals['Protein (g)']:.1f}g</strong></span>
  <span>🧈 Fat: <strong>{totals['Fat (g)']:.1f}g</strong></span>
  <span>🍬 Sugar: <strong>{totals['Sugar (g)']:.1f}g</strong></span>
  <span>🧂 Sodium: <strong>{totals['Sodium (mg)']:.0f}mg</strong></span>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 3 — WEEKLY SCHEDULE
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">🗓️ Weekly Eating Schedule</div>', unsafe_allow_html=True)

        schedule = build_schedule(
            result_df, n_days, meals_per_day,
            meal_labels, num_drinks, selected_days
        )

        if not schedule:
            st.info("No schedule to display.")
        else:
            week_cal  = 0.0
            week_cost = 0.0

            for day_info in schedule:
                day_cal  = 0.0
                day_cost = 0.0

                slots_html = ""
                for slot in day_info["slots"]:
                    item = slot["item"]
                    label = slot["label"]
                    target_cal = cal_targets[meal_labels.index(label)] if label in meal_labels else 400

                    if item is None:
                        slots_html += f"""<div class="slot-row">
<div class="slot-label">{label}</div>
<div class="slot-item" style="color:#bbb;font-style:italic">No item assigned</div>
</div>"""
                    else:
                        name    = fmt_name(item["menu_item"])
                        tp      = item["type"]
                        loc     = item["location"]
                        cal_v   = float(item["calories_kcal"])
                        price_v = float(item["price"])
                        prot_v  = float(item["protein_g"])
                        note    = cal_note(cal_v, target_cal)

                        slots_html += f"""<div class="slot-row">
<div class="slot-label">{label}</div>
<div class="slot-item">
<div class="item-name">{name}</div>
<div class="item-meta">
  {badge_html(tp)}
  📍 {loc.replace("_"," ").title()} &nbsp;
  🔥 {cal_v:.0f} kcal &nbsp;
  💰 PHP {price_v:.0f} &nbsp;
  💪 {prot_v:.1f}g protein
</div>
<div style="margin-top:3px">{note}</div>
</div>
</div>"""
                        day_cal  += cal_v
                        day_cost += price_v

                # Drink for this day
                drink_html = ""
                if day_info["drink"]:
                    dk = day_info["drink"]
                    dk_name  = fmt_name(dk["menu_item"])
                    dk_loc   = dk["location"]
                    dk_cal   = float(dk["calories_kcal"])
                    dk_price = float(dk["price"])
                    drink_html = f"""<div class="slot-row">
<div class="slot-label">🧃 Drink</div>
<div class="slot-item">
<div class="item-name">{dk_name}</div>
<div class="item-meta">
  {badge_html("drink")}
  📍 {dk_loc.replace("_"," ").title()} &nbsp;
  🔥 {dk_cal:.0f} kcal &nbsp;
  💰 PHP {dk_price:.0f}
</div>
</div>
</div>"""
                    day_cal  += dk_cal
                    day_cost += dk_price

                week_cal  += day_cal
                week_cost += day_cost

                st.markdown(f"""<div class="day-card">
  <div class="day-title">📅 {day_info['name']}</div>
  {slots_html}
  {drink_html}
  <div class="day-total">
    <span>🔥 <strong>{day_cal:.0f} kcal</strong> today</span>
    <span>💰 <strong>PHP {day_cost:.2f}</strong> today</span>
  </div>
</div>""", unsafe_allow_html=True)

            # Weekly summary bar
            st.markdown(f"""<div style="background:linear-gradient(90deg,#7b1113,#c0392b);color:white;border-radius:10px;padding:18px 24px;margin-top:10px">
  <div style="font-size:1.1rem;font-weight:800;margin-bottom:10px">📊 Weekly Schedule Summary</div>
  <div style="display:flex;gap:40px;flex-wrap:wrap">
    <div><div style="font-size:0.8rem;opacity:0.8">Total Calories</div>
         <div style="font-size:1.4rem;font-weight:700">{week_cal:,.0f} kcal</div></div>
    <div><div style="font-size:0.8rem;opacity:0.8">Total Spend</div>
         <div style="font-size:1.4rem;font-weight:700">PHP {week_cost:,.2f}</div></div>
    <div><div style="font-size:0.8rem;opacity:0.8">Avg Daily Calories</div>
         <div style="font-size:1.4rem;font-weight:700">{week_cal/n_days:,.0f} kcal</div></div>
    <div><div style="font-size:0.8rem;opacity:0.8">Avg Daily Spend</div>
         <div style="font-size:1.4rem;font-weight:700">PHP {week_cost/n_days:,.2f}</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 4 — TIPS & CHARTS
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-header">💡 Student Tips</div>', unsafe_allow_html=True)

        tips = []
        if result["total_sodium"] > 0.8 * max_sodium:
            tips.append(f"⚠️ Sodium is {result['total_sodium']/max_sodium*100:.0f}% of your weekly limit — drink extra water!")
        if result["total_protein"] < 1.5 * min_protein:
            tips.append("💪 Protein is on the low side. Consider adding eggs or tofu as sides.")
        if result["total_cost"] < 0.85 * weekly_budget:
            tips.append(f"💰 Budget surplus of PHP {weekly_budget - result['total_cost']:.2f} — treat yourself to merienda!")
        if result["total_calories"] / n_days < 1500:
            tips.append("🍚 Daily average is below 1500 kcal — consider adding rice or noodles.")
        tips += [
            "📍 All items are from UP Diliman kiosks — no off-campus trips needed.",
            "🧃 Stay hydrated! Aim for at least 8 glasses of water per day.",
            "⏰ Try to eat at regular times to keep your energy steady during class.",
            "🥦 Balance your week — alternate between heavier and lighter meals.",
        ]

        for tip in tips:
            st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)

        # ── Charts ────────────────────────────────────────────────────────────
        if not result_df.empty:
            st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)

            chart1, chart2 = st.columns(2)

            with chart1:
                # Calorie distribution by food type
                type_cal = result_df.groupby("type")["total_cal"].sum().reset_index()
                type_cal["type_label"] = type_cal["type"].map({
                    "a_la_carte": "A La Carte", "drink": "Drink",
                    "combo": "Combo", "meal": "Meal"
                })
                fig_pie = px.pie(
                    type_cal, values="total_cal", names="type_label",
                    title="Calories by Food Type",
                    color_discrete_sequence=["#7b1113","#c0392b","#e57373","#ffcdd2"],
                )
                fig_pie.update_layout(margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig_pie, use_container_width=True)

            with chart2:
                # Spend by kiosk
                loc_spend = result_df.groupby("location")["total_cost"].sum().reset_index()
                loc_spend["location"] = loc_spend["location"].str.replace("_"," ").str.title()
                loc_spend = loc_spend.sort_values("total_cost", ascending=True)
                fig_bar = px.bar(
                    loc_spend, x="total_cost", y="location",
                    orientation="h", title="Total Spend by Kiosk (PHP)",
                    color="total_cost",
                    color_continuous_scale=["#ffcdd2","#7b1113"],
                    labels={"total_cost": "PHP", "location": "Kiosk"},
                )
                fig_bar.update_layout(margin=dict(t=40,b=0,l=0,r=0), showlegend=False,
                                       coloraxis_showscale=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            # Nutrient radar
            st.markdown("#### 🕸️ Nutrient Usage (% of limit)")
            nutrients = {
                "Sugar":   (result["total_sugar"],   max_sugar),
                "Fat":     (result["total_fat"],     max_fat),
                "Sodium":  (result["total_sodium"],  max_sodium),
                "Protein": (result["total_protein"], min_protein),
                "Calories":(result["total_calories"],min_cals),
            }
            cats   = list(nutrients.keys())
            values = [min(v/l*100, 150) for v, l in nutrients.values()]
            values += [values[0]]
            cats   += [cats[0]]

            fig_radar = go.Figure(go.Scatterpolar(
                r=values, theta=cats,
                fill="toself", fillcolor="rgba(123,17,19,0.15)",
                line=dict(color="#7b1113", width=2),
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,150],
                                           ticksuffix="%", tickfont=dict(size=9))),
                showlegend=False, margin=dict(t=20,b=20,l=40,r=40),
                height=380,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Top 10 items by calories
            st.markdown("#### 🏆 Top 10 Items by Total Calories")
            top10 = result_df.nlargest(10, "total_cal")[["menu_item","location","type","total_cal","total_cost"]].copy()
            top10["menu_item"] = top10["menu_item"].apply(fmt_name)
            top10["location"]  = top10["location"].str.replace("_"," ").str.title()
            top10.columns = ["Item","Kiosk","Type","Total Cal (kcal)","Total Cost (PHP)"]
            st.dataframe(top10.style.format({"Total Cal (kcal)":"{:.0f}","Total Cost (PHP)":"₱{:.2f}"}),
                         use_container_width=True, hide_index=True)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()