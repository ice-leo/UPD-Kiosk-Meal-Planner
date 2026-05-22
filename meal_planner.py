# =============================================================================
#  UP Diliman Kiosk Weekly Meal Planner  —  Streamlit App
#  Math 180.1 Project  (v2 — improved)
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

    /* Force main content text to dark — scoped to the main block container only,
       so Streamlit's top toolbar (Deploy bar) is NOT affected and keeps its own
       theme-aware colors in dark/system mode. */
    [data-testid="stMainBlockContainer"],
    [data-testid="stMainBlockContainer"] p,
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3,
    [data-testid="stMainBlockContainer"] h4,
    [data-testid="stMainBlockContainer"] h5,
    [data-testid="stMainBlockContainer"] h6,
    [data-testid="stMainBlockContainer"] span,
    [data-testid="stMainBlockContainer"] div,
    [data-testid="stMainBlockContainer"] label,
    [data-testid="stMainBlockContainer"] li {
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

    /* Fix: sidebar input fields — light text on dark sidebar background makes
       typed values invisible in Streamlit's light mode. Force white bg + dark text
       on all interactive inputs so they're readable regardless of theme. */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="base-input"] input,
    [data-testid="stSidebar"] [data-testid="stNumberInputField"],
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        background-color: #fff !important;
        color: #1a1a1a !important;
        border-color: rgba(255,255,255,0.4) !important;
    }
    /* Also fix the number-input container wrapper */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="base-input"] {
        background-color: #fff !important;
    }
            /* Fix: sidebar number-input stepper buttons (+/−) — force visible bg+icon */
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"],
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"] {
        background-color: #7b1113 !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"]:hover,
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"]:hover {
        background-color: #a01517 !important;
    }
    /* Also covers the SVG icons inside the buttons */
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] svg,
    [data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    /* Selectbox / multiselect dropdowns */
    [data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="tag"],
    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
        background-color: transparent !important;
        color: #1a1a1a !important;
    }

    /* Tab styling to match sidebar */
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #7b1113 !important;
        font-weight: 600;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #7b1113 !important;
    }

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
    .relaxation-box {
        background: #fff3e0;
        border-left: 5px solid #f57c00;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 12px;
        color: #e65100 !important;
    }
    /* FIX 2: Themed dataframe — style the Streamlit dataframe container */
    [data-testid="stDataFrame"] {
        background: #fff8f5 !important;
        border-radius: 8px;
        border: 1px solid #f0d8d8;
    }
    [data-testid="stDataFrame"] table { color: #3a1a1a !important; }
    [data-testid="stDataFrame"] thead tr th {
        background: #7b1113 !important;
        color: white !important;
    }
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background: #fdf0f0 !important;
    }
    /* Profile card style */
    .profile-card {
        background: white;
        border: 2px solid #e8d5d5;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        cursor: pointer;
    }
    .profile-card.active {
        border-color: #7b1113;
        background: #fff8f5;
    }
    .rdv-hint {
        font-size: 0.75rem;
        color: #888 !important;
        font-style: italic;
    }
    /* Fix: expander — same look regardless of state or theme */
    [data-testid="stExpander"] details summary {
        background-color: #7b1113 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] details[open] summary {
        background-color: #7b1113 !important;
        border-radius: 8px 8px 0 0 !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] details[open] summary span,
    [data-testid="stExpander"] details[open] summary p {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════

DATASET_FILE = "Math 180.1 Dataset.xlsx"
EXPECTED_COLS = [
    "location", "menu_item", "menu_type", "carbs",
    "item_1", "item_2", "item_3", "drink",
    "sugar_g", "protein_g", "fat_g", "sodium_mg", "calories_kcal", "price",
]
ALL_LOCATIONS = ["imath", "sub_che", "gyudfood", "cal", "stat", "arki", "palma_psych", "plaridel"]
ALL_DAYS      = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Preset profiles — (name, emoji, description, weekly_budget, min_cals, min_protein, max_sodium, max_sugar, max_fat, cal_targets)
PROFILES = {
    "Light Eater": {
        "emoji": "🥗",
        "desc": "Smaller portions, lower calorie target. Great for sedentary days.",
        "weekly_budget": 500,
        "min_cals": 5600,       # ~800 kcal/day × 7
        "min_protein": 35,      # ~5g/day
        "max_sodium": 9800,     # ~1400 mg/day
        "max_sugar": 420,       # ~60g/day
        "max_fat": 280,         # ~40g/day
        "cal_targets": [300, 400, 200, 250],
    },
    "Active Student": {
        "emoji": "🏃",
        "desc": "Balanced macros for a student on the go with regular physical activity.",
        "weekly_budget": 750,
        "min_cals": 10500,      # ~1500 kcal/day
        "min_protein": 70,      # ~10g/day
        "max_sodium": 14000,    # ~2000 mg/day
        "max_sugar": 630,       # ~90g/day
        "max_fat": 420,         # ~60g/day
        "cal_targets": [400, 600, 300, 350],
    },
    "Bulking": {
        "emoji": "💪",
        "desc": "High calories and protein for muscle gain. Larger meals, generous budget.",
        "weekly_budget": 1200,
        "min_cals": 17500,      # ~2500 kcal/day
        "min_protein": 140,     # ~20g/day
        "max_sodium": 19600,    # ~2800 mg/day
        "max_sugar": 700,       # ~100g/day
        "max_fat": 630,         # ~90g/day
        "cal_targets": [600, 900, 400, 600],
    },
}

# Recommended daily values for tooltips
RDV = {
    "min_cals":    {"label": "Min Total Calories", "rdv": "~1,800–2,200 kcal/day (12,600–15,400/wk)", "unit": "kcal"},
    "min_protein": {"label": "Min Protein",        "rdv": "~50–60 g/day (350–420/wk)",                 "unit": "g"},
    "max_sodium":  {"label": "Max Sodium",          "rdv": "≤ 2,300 mg/day (16,100/wk)",                "unit": "mg"},
    "max_sugar":   {"label": "Max Sugar",           "rdv": "≤ 50 g/day (350/wk)",                       "unit": "g"},
    "max_fat":     {"label": "Max Fat",             "rdv": "≤ 65 g/day (455/wk)",                       "unit": "g"},
}

# Activity level multipliers (Mifflin–St Jeor PAL)
ACTIVITY_LEVELS = {
    "Sedentary (little/no exercise)":          1.2,
    "Lightly active (1–3 days/wk exercise)":   1.375,
    "Moderately active (3–5 days/wk exercise)":1.55,
    "Very active (6–7 days/wk exercise)":      1.725,
    "Extra active (physical job + exercise)":  1.9,
}

# ═════════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(DATASET_FILE)
    if not path.exists():
        return None
    df = pd.read_excel(path, header=0)

    if "location" not in df.columns:
        n = min(len(EXPECTED_COLS), len(df.columns))
        df.columns = list(EXPECTED_COLS[:n]) + list(df.columns[n:])

    present = [c for c in EXPECTED_COLS if c in df.columns]
    df = df[present].copy()

    for c in EXPECTED_COLS:
        if c not in df.columns:
            df[c] = 0 if c in ("sugar_g","protein_g","fat_g","sodium_mg","calories_kcal","price") else "none"

    str_cols = ["location","menu_item","menu_type","carbs","item_1","item_2","item_3","drink"]
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip().str.lower().replace("nan", "none")

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
    Solves the MILP using PuLP (preferred) or scipy LP relaxation fallback.
    Returns feasibility dict including what constraints were relaxed.
    """
    M = n_days * meals_per_day

    F  = df.index[df.menu_type == "a_la_carte"].tolist()
    D  = df.index[df.menu_type == "drink"].tolist()
    C  = df.index[df.menu_type == "combo"].tolist()
    Me = df.index[df.menu_type == "meal"].tolist()

    nF, nD, nC, nMe = len(F), len(D), len(C), len(Me)
    nVars = nF + nD + nC + nMe + nC + nMe   # x, d, y, m, z, w

    ix  = list(range(0, nF))
    id_ = list(range(nF, nF+nD))
    iy  = list(range(nF+nD, nF+nD+nC))
    im  = list(range(nF+nD+nC, nF+nD+nC+nMe))
    iz  = list(range(nF+nD+nC+nMe, nF+nD+nC+nMe+nC))
    iw  = list(range(nF+nD+nC+nMe+nC, nVars))

    def col(name, idx):
        return df.loc[idx, name].values.astype(float)

    # Objective: maximise calories
    c_obj = np.zeros(nVars)
    c_obj[ix]  = col("calories_kcal", F)
    c_obj[id_] = col("calories_kcal", D)
    c_obj[iy]  = col("calories_kcal", C)
    c_obj[im]  = col("calories_kcal", Me)
    c_neg = -c_obj

    def build_constraints(
        cur_min_cals, cur_min_protein, cur_max_sodium, cur_weekly_budget
    ):
        A_ub_rows, b_ub_rows = [], []

        def add_ineq(row_vals, rhs):
            A_ub_rows.append(row_vals)
            b_ub_rows.append(rhs)

        # Budget
        r = np.zeros(nVars)
        r[ix]=col("price",F); r[id_]=col("price",D); r[iy]=col("price",C); r[im]=col("price",Me)
        add_ineq(r, cur_weekly_budget)

        # Sugar
        r = np.zeros(nVars)
        r[ix]=col("sugar_g",F); r[id_]=col("sugar_g",D); r[iy]=col("sugar_g",C); r[im]=col("sugar_g",Me)
        add_ineq(r, max_sugar)

        # Fat
        r = np.zeros(nVars)
        r[ix]=col("fat_g",F); r[id_]=col("fat_g",D); r[iy]=col("fat_g",C); r[im]=col("fat_g",Me)
        add_ineq(r, max_fat)

        # Sodium ≤ max
        r = np.zeros(nVars)
        r[ix]=col("sodium_mg",F); r[id_]=col("sodium_mg",D); r[iy]=col("sodium_mg",C); r[im]=col("sodium_mg",Me)
        add_ineq(r, cur_max_sodium)

        # Protein ≥ min → -protein ≤ -min
        r = np.zeros(nVars)
        r[ix]=-col("protein_g",F); r[id_]=-col("protein_g",D); r[iy]=-col("protein_g",C); r[im]=-col("protein_g",Me)
        add_ineq(r, -cur_min_protein)

        # Total calories ≥ min → -cals ≤ -min
        r = np.zeros(nVars)
        r[ix]=-col("calories_kcal",F); r[id_]=-col("calories_kcal",D); r[iy]=-col("calories_kcal",C); r[im]=-col("calories_kcal",Me)
        add_ineq(r, -cur_min_cals)

        # Duplicate limits
        for fi in ix:
            r = np.zeros(nVars); r[fi] = 1; add_ineq(r, max_duplicates)
        for di in id_:
            r = np.zeros(nVars); r[di] = 1; add_ineq(r, max_duplicates)
        for yi in iy:
            r = np.zeros(nVars); r[yi] = 1; add_ineq(r, max_duplicates)
        for mi in im:
            r = np.zeros(nVars); r[mi] = 1; add_ineq(r, max_duplicates)

        # Component exclusion — combos and meals have components; a_la_carte and drinks do not
        bigM = M
        food_name_map = {df.loc[f_idx, "menu_item"]: i for i, f_idx in enumerate(F)}
        meal_name_map = {df.loc[m_idx, "menu_item"]: i for i, m_idx in enumerate(Me)}

        # Combos: prevent selecting a combo and its components simultaneously (via z binary)
        for k, c_idx in enumerate(C):
            components = []
            for cc in ["carbs", "item_1", "item_2", "item_3", "drink"]:
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

        # Meals: prevent selecting a meal and its components simultaneously (via w binary)
        for k, m_idx in enumerate(Me):
            components = []
            for cc in ["carbs", "item_1", "item_2", "item_3", "drink"]:
                val = df.loc[m_idx, cc]
                if val and val != "none":
                    components.append(val)
            for comp in components:
                if comp in food_name_map:
                    r = np.zeros(nVars)
                    r[ix[food_name_map[comp]]] = 1
                    r[iw[k]] = bigM
                    add_ineq(r, bigM)
                elif comp in meal_name_map and meal_name_map[comp] != k:
                    r = np.zeros(nVars)
                    r[im[meal_name_map[comp]]] = 1
                    r[iw[k]] = bigM
                    add_ineq(r, bigM)
            # Linking: m_k ≤ bigM * w_k
            r = np.zeros(nVars)
            r[im[k]] = 1; r[iw[k]] = -bigM
            add_ineq(r, 0)

        A_ub = np.array(A_ub_rows) if A_ub_rows else np.empty((0, nVars))
        b_ub = np.array(b_ub_rows) if b_ub_rows else np.array([])

        # Equality: meal count
        A_eq_rows, b_eq_rows = [], []
        r = np.zeros(nVars)
        r[ix] = 1; r[iy] = 1; r[im] = 1
        A_eq_rows.append(r); b_eq_rows.append(M)

        # Equality: exact drinks
        r = np.zeros(nVars)
        r[id_] = 1
        A_eq_rows.append(r); b_eq_rows.append(num_drinks)

        A_eq = np.array(A_eq_rows)
        b_eq = np.array(b_eq_rows)

        return A_ub, b_ub, A_eq, b_eq

    def try_solve(cur_min_cals, cur_min_protein, cur_max_sodium, cur_weekly_budget):
        A_ub, b_ub, A_eq, b_eq = build_constraints(
            cur_min_cals, cur_min_protein, cur_max_sodium, cur_weekly_budget
        )
        bounds = [(0, None)] * nVars
        for zi in iz:
            bounds[zi] = (0, 1)
        for wi in iw:
            bounds[wi] = (0, 1)
        if num_drinks == 0:
            for di in id_:
                bounds[di] = (0, 0)

        try:
            import pulp
            prob = pulp.LpProblem("MealPlanner", pulp.LpMaximize)
            x_vars = [pulp.LpVariable(f"x_{i}", lowBound=0, cat="Integer") for i in range(nF)]
            d_vars = [pulp.LpVariable(f"d_{i}", lowBound=0, upBound=(0 if num_drinks == 0 else None), cat="Integer") for i in range(nD)]
            y_vars = [pulp.LpVariable(f"y_{i}", lowBound=0, cat="Integer") for i in range(nC)]
            m_vars = [pulp.LpVariable(f"m_{i}", lowBound=0, cat="Integer") for i in range(nMe)]
            z_vars = [pulp.LpVariable(f"z_{i}", lowBound=0, upBound=1, cat="Binary") for i in range(nC)]
            w_vars = [pulp.LpVariable(f"w_{i}", lowBound=0, upBound=1, cat="Binary") for i in range(nMe)]
            all_vars = x_vars + d_vars + y_vars + m_vars + z_vars + w_vars
            prob += pulp.lpDot(c_obj.tolist(), all_vars)
            for row, rhs in zip(A_ub.tolist(), b_ub.tolist()):
                prob += pulp.lpDot(row, all_vars) <= rhs
            for row, rhs in zip(A_eq.tolist(), b_eq.tolist()):
                prob += pulp.lpDot(row, all_vars) == rhs
            prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60))
            if pulp.LpStatus[prob.status] not in ("Optimal", "Feasible"):
                return None, pulp.LpStatus[prob.status]
            sol = np.array([v.varValue or 0 for v in all_vars])
        except ImportError:
            res = linprog(c_neg, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method="highs", options={"time_limit": 60})
            if res.status != 0:
                reasons = {1: "Iteration limit", 2: "Infeasible", 3: "Unbounded", 4: "Numerical error"}
                return None, reasons.get(res.status, f"Status {res.status}")
            sol = np.round(res.x)

        return np.clip(np.round(sol).astype(int), 0, None), "Optimal"

    # ── FIX 4: Auto-relaxation loop ──────────────────────────────────────────
    relaxations_applied = []
    cur_min_cals    = min_calories_total
    cur_min_protein = min_protein
    cur_max_sodium  = max_sodium
    cur_weekly_budget = weekly_budget

    sol, status = try_solve(cur_min_cals, cur_min_protein, cur_max_sodium, cur_weekly_budget)

    if sol is None:
        # For each constraint, try 10→90%. If no pct solves it, permanently lock
        # in the 90% relaxation before moving to the next constraint.
        constraints = [
            "Min Calories",
            "Min Protein",
            "Max Sodium",
            "Budget",
        ]
        for step_name in constraints:
            if sol is not None:
                break
            last_pct = 0
            for pct in [0.10, 0.30, 0.50, 0.70, 0.90]:
                # Build trial using CURRENT (already relaxed) values
                if step_name == "Min Calories":
                    trial_cals, trial_prot, trial_sod, trial_budget = (cur_min_cals * (1 - pct), cur_min_protein, cur_max_sodium, cur_weekly_budget)
                elif step_name == "Min Protein":
                    trial_cals, trial_prot, trial_sod, trial_budget = (cur_min_cals, cur_min_protein * (1 - pct), cur_max_sodium, cur_weekly_budget)
                elif step_name == "Max Sodium":
                    trial_cals, trial_prot, trial_sod, trial_budget = (cur_min_cals, cur_min_protein, cur_max_sodium * (1 + pct), cur_weekly_budget)
                elif step_name == "Budget":
                    trial_cals, trial_prot, trial_sod, trial_budget = (cur_min_cals, cur_min_protein, cur_max_sodium, cur_weekly_budget * (1 + pct))
                last_pct = pct
                trial_sol, trial_status = try_solve(trial_cals, trial_prot, trial_sod, trial_budget)
                if trial_sol is not None:
                    sol = trial_sol
                    status = trial_status
                    cur_min_cals      = trial_cals
                    cur_min_protein   = trial_prot
                    cur_max_sodium    = trial_sod
                    cur_weekly_budget = trial_budget
                    relaxations_applied.append(f"{step_name} relaxed by {int(last_pct*100)}%")
                    break
            else:
                # All pcts failed — permanently apply 90% relaxation before next constraint
                if step_name == "Min Calories":
                    cur_min_cals      = cur_min_cals * (1 - 0.90)
                elif step_name == "Min Protein":
                    cur_min_protein   = cur_min_protein * (1 - 0.90)
                elif step_name == "Max Sodium":
                    cur_max_sodium    = cur_max_sodium * (1 + 0.90)
                elif step_name == "Budget":
                    cur_weekly_budget = cur_weekly_budget * (1 + 0.90)
                relaxations_applied.append(f"{step_name} relaxed by 90% (max, carried forward)")

    if sol is None:
        return {"feasible": False, "reason": status}

    sel_food  = sol[ix]
    sel_drink = sol[id_]
    sel_combo = sol[iy]
    sel_meal  = sol[im]

    quantities  = np.concatenate([sel_food, sel_drink, sel_combo, sel_meal])
    indices_all = F + D + C + Me
    types_all   = (["a_la_carte"] * nF + ["drink"] * nD + ["combo"] * nC + ["meal"] * nMe)

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
        "feasible":            True,
        "result_df":           result_df,
        "total_calories":      wtd("calories_kcal"),
        "total_cost":          wtd("price"),
        "total_sugar":         wtd("sugar_g"),
        "total_protein":       wtd("protein_g"),
        "total_fat":           wtd("fat_g"),
        "total_sodium":        wtd("sodium_mg"),
        "M":                   M,
        "nF": nF, "nD": nD, "nC": nC, "nMe": nMe,
        "sel_food":            sel_food,
        "sel_drink":           sel_drink,
        "sel_combo":           sel_combo,
        "sel_meal":            sel_meal,
        "relaxations_applied": relaxations_applied,
        "relaxed_min_cals":    cur_min_cals,
        "relaxed_min_protein": cur_min_protein,
        "relaxed_max_sodium":  cur_max_sodium,
        "relaxed_budget":      cur_weekly_budget,
    }


# ═════════════════════════════════════════════════════════════════════════════
#  SCHEDULE BUILDER  (FIX 3: drinks placed only at slots that have food, 
#                     and drink location matches meal locations for that day)
# ═════════════════════════════════════════════════════════════════════════════

def build_schedule(result_df: pd.DataFrame, n_days: int, meals_per_day: int,
                   meal_labels: list, num_drinks: int, selected_days: list) -> list:
    """
    Returns list of dicts per day, each with 'slots' and optionally 'drink'.
    FIX 3: drinks are only placed on days that have at least one meal assigned,
    and preferably drinks from the same location as the meals on that day.
    """
    if result_df.empty or n_days == 0:
        return []

    food_df  = result_df[result_df["type"] != "drink"].copy()
    drink_df = result_df[result_df["type"] == "drink"].copy()

    food_pool  = food_df.loc[food_df.index.repeat(food_df["quantity"])].reset_index(drop=True)
    drink_pool = drink_df.loc[drink_df.index.repeat(drink_df["quantity"])].reset_index(drop=True)

    food_pool = food_pool.sort_values("calories_kcal", ascending=False).reset_index(drop=True)

    if meals_per_day >= 2:
        priority_slots = [1, 0] + list(range(2, meals_per_day))
    else:
        priority_slots = [0]

    slot_order = []
    for s in priority_slots:
        if s < meals_per_day:
            for d in range(n_days):
                slot_order.append((d, s))

    schedule = [[None] * meals_per_day for _ in range(n_days)]
    for k, (d, s) in enumerate(slot_order):
        if k < len(food_pool):
            schedule[d][s] = food_pool.iloc[k].to_dict()

    # FIX 3: assign drinks to days that have at least one meal, 
    # and try to match drink location with meal locations on that day
    days_with_food = [d for d in range(n_days) if any(schedule[d])]
    
    # Build a list of available drinks with their locations
    drink_list = []
    for i in range(len(drink_pool)):
        drink_list.append(drink_pool.iloc[i].to_dict())
    
    # For each day with food, collect the locations of meals on that day
    day_locations = {}
    for d in days_with_food:
        locs = set()
        for s in range(meals_per_day):
            item = schedule[d][s]
            if item is not None:
                locs.add(item.get("location", ""))
        day_locations[d] = locs
    
    # Assign drinks, preferring same-location matches
    assigned_drinks = set()
    day_drinks = {}
    n_drinks_assigned = 0
    max_drinks_possible = min(num_drinks, len(drink_list), len(days_with_food))
    
    # First pass: try to match drinks to days with same location
    remaining_drinks = list(range(len(drink_list)))
    for d in days_with_food:
        if n_drinks_assigned >= max_drinks_possible:
            break
        day_locs = day_locations.get(d, set())
        best_drink_idx = None
        for di in remaining_drinks:
            if di in assigned_drinks:
                continue
            drink_loc = drink_list[di].get("location", "")
            if drink_loc in day_locs:
                best_drink_idx = di
                break
        if best_drink_idx is not None:
            day_drinks[d] = drink_list[best_drink_idx]
            assigned_drinks.add(best_drink_idx)
            n_drinks_assigned += 1
    
    # Second pass: assign remaining drinks to days without drinks yet
    for d in days_with_food:
        if n_drinks_assigned >= max_drinks_possible:
            break
        if d not in day_drinks:
            for di in remaining_drinks:
                if di not in assigned_drinks:
                    day_drinks[d] = drink_list[di]
                    assigned_drinks.add(di)
                    n_drinks_assigned += 1
                    break

    days = []
    for d in range(n_days):
        day_name = selected_days[d]
        day_info = {
            "name":  day_name,
            "slots": [{"label": meal_labels[s], "item": schedule[d][s]}
                      for s in range(meals_per_day)],
            "drink": day_drinks.get(d),
        }
        days.append(day_info)
    return days


# ═════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def fmt_name(name: str) -> str:
    return name.replace("_", " ").title() if name else ""

def badge_html(tp: str) -> str:
    cls   = {"a_la_carte": "badge-alacarte", "combo": "badge-combo",
             "meal": "badge-meal",          "drink": "badge-drink"}.get(tp, "badge-alacarte")
    label = {"a_la_carte": "A La Carte",    "combo": "Combo",
             "meal": "Meal",                "drink": "Drink"}.get(tp, tp)
    return f'<span class="badge {cls}">{label}</span>'

def cal_note(item_cal: float, target_cal: float) -> str:
    diff = item_cal - target_cal
    if diff > 150:
        return '<span class="note-high">↑ High calorie — save room for later!</span>'
    elif diff < -150:
        return '<span class="note-low">↓ Light meal — consider a snack later.</span>'
    return '<span class="note-good">✓ Good fit for this slot.</span>'

def nutrient_bar(label: str, value: float, limit: float, unit: str,
                 is_min: bool = False):
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

def rdv_label(key: str) -> str:
    """Return an input label with an inline RDV hint."""
    info = RDV.get(key, {})
    return f"{info.get('label', key)} ({info.get('unit', '')})"

def rdv_help(key: str) -> str:
    info = RDV.get(key, {})
    return f"📋 Recommended Daily Value: {info.get('rdv', 'N/A')}"


# ═════════════════════════════════════════════════════════════════════════════
#  TDEE CALCULATOR
# ═════════════════════════════════════════════════════════════════════════════

def compute_tdee(weight_kg: float, height_cm: float, age: int, sex: str, activity: str) -> float:
    """Mifflin–St Jeor TDEE in kcal/day."""
    if sex == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return bmr * ACTIVITY_LEVELS.get(activity, 1.55)


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

    loc_options = sorted(df_all["location"].unique().tolist())
    default_labels = ["Breakfast", "Lunch", "Merienda", "Dinner"]

    # ═══════════════════════════════════════════════════════════════════════════
    #  SIDEBAR — Two-tab settings
    # ═══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("## ⚙️ Planner Settings")
        st.markdown("---")

        settings_tab, smart_tab = st.tabs(["🔢 Manual", "🧠 Smart"])

        # ── MANUAL TAB ────────────────────────────────────────────────────────
        with settings_tab:
            st.markdown("### 📅 Schedule")
            selected_days_m = []
            for day in ALL_DAYS:
                if st.checkbox(day, value=day in ["Monday","Tuesday","Wednesday","Thursday","Friday"], key=f"day_m_{day}"):
                    selected_days_m.append(day)
            selected_days_m = sorted(selected_days_m, key=lambda x: ALL_DAYS.index(x))
            n_days_m = len(selected_days_m)

            meals_per_day_m = st.slider("Meals per day", 1, 4, 3, key="mpd_m")

            st.markdown("### 🏷️ Meal Slot Names")
            meal_labels_m = []
            for i in range(meals_per_day_m):
                lbl = st.text_input(
                    f"Slot {i+1} name",
                    value=default_labels[i] if i < len(default_labels) else f"Meal {i+1}",
                    key=f"label_m_{i}",
                )
                meal_labels_m.append(lbl)

            st.markdown("### 🎯 Calorie Targets per Slot (kcal)")
            default_targets = [400, 600, 350, 300]
            cal_targets_m = []
            for i in range(meals_per_day_m):
                t = st.number_input(
                    f"{meal_labels_m[i]} target (kcal)",
                    min_value=50, max_value=2000,
                    value=default_targets[i] if i < len(default_targets) else 400,
                    step=50, key=f"cal_target_m_{i}",
                )
                cal_targets_m.append(t)

            st.markdown("### 💰 Budget & Drinks")
            weekly_budget_m = st.number_input("Budget (PHP)", 50, 5000, 750, step=50, key="budget_m")
            max_drinks_m = max(1, n_days_m * meals_per_day_m)
            num_drinks_m = st.slider("Drinks per week", 0, max_drinks_m, min(3, max_drinks_m), key="drinks_m")

            st.markdown("### 🥗 Nutrient Constraints (total)")
            max_sugar_m   = st.number_input(rdv_label("max_sugar"),   50, 5000,  700,   step=50,  key="sugar_m",   help=rdv_help("max_sugar"))
            max_fat_m     = st.number_input(rdv_label("max_fat"),     50, 2000,  400,   step=50,  key="fat_m",     help=rdv_help("max_fat"))
            max_sodium_m  = st.number_input(rdv_label("max_sodium"),  500, 50000, 12000, step=500, key="sodium_m",  help=rdv_help("max_sodium"))
            min_protein_m = st.number_input(rdv_label("min_protein"), 5, 500,   20,    step=5,   key="protein_m", help=rdv_help("min_protein"))
            min_cals_m    = st.number_input(rdv_label("min_cals"),    500, 30000, 7000,  step=500, key="cals_m",    help=rdv_help("min_cals"))

            st.markdown("### 🔁 Duplicate Limit")
            max_items_m = max(1, n_days_m * meals_per_day_m)
            max_dup_m = st.slider(
                "Max times same item can appear",
                1, max(2, max_items_m), 
                min(2, max(2, max_items_m)),
                help="1 = unique items only; higher = allow repeats",
                key="dup_m",
            )
            if max_dup_m > max_items_m:
                max_dup_m = max_items_m

            st.markdown("### 📍 Allowed Kiosks")
            selected_locs_m = []
            for loc in loc_options:
                if st.checkbox(loc.replace("_"," ").title(), value=True, key=f"loc_m_{loc}"):
                    selected_locs_m.append(loc)

            st.markdown("---")
            run_btn_m = st.button("🚀 Run Meal Planner", type="primary", use_container_width=True, key="run_m")

        # ── SMART TAB (FIX 1: auto-updating nutrient targets, no editable section) ─
                # ── SMART TAB (FIX: Calculator always reactive, profile overrides when selected) ─
        with smart_tab:
            st.markdown("### 📅 Schedule")
            selected_days_s = []
            for day in ALL_DAYS:
                if st.checkbox(day, value=day in ["Monday","Tuesday","Wednesday","Thursday","Friday"], key=f"day_s_{day}"):
                    selected_days_s.append(day)
            selected_days_s = sorted(selected_days_s, key=lambda x: ALL_DAYS.index(x))
            n_days_s = len(selected_days_s)

            meals_per_day_s = st.slider("Meals per day", 1, 4, 3, key="mpd_s")

            st.markdown("### 🏷️ Meal Slot Names")
            meal_labels_s = []
            for i in range(meals_per_day_s):
                lbl = st.text_input(
                    f"Slot {i+1} name",
                    value=default_labels[i] if i < len(default_labels) else f"Meal {i+1}",
                    key=f"label_s_{i}",
                )
                meal_labels_s.append(lbl)

            st.markdown("### 💰 Budget & Drinks")
            weekly_budget_s_base = st.number_input("Budget (PHP)", 50, 5000, 750, step=50, key="budget_s")
            max_drinks_s = max(1, n_days_s * meals_per_day_s)
            num_drinks_s = st.slider("Total number of drinks", 0, max_drinks_s, min(3, max_drinks_s), key="drinks_s")

            st.markdown("### 🔁 Duplicate Limit")
            max_items_s = max(1, n_days_s * meals_per_day_s)
            max_dup_s = st.slider(
                "Max times same item can appear",
                1, max(2, max_items_s), 
                min(2, max(2, max_items_s)),
                help="1 = unique items only; higher = allow repeats",
                key="dup_s",
            )
            if max_dup_s > max_items_s:
                max_dup_s = max_items_s

            st.markdown("### 📍 Allowed Kiosks")
            selected_locs_s = []
            for loc in loc_options:
                if st.checkbox(loc.replace("_"," ").title(), value=True, key=f"loc_s_{loc}"):
                    selected_locs_s.append(loc)


            st.markdown("---")
            st.markdown("### 🏋️ Personalised Calculator")
            
            st.caption("Fill in to auto-calculate your total nutrient targets.")

            col_wh1, col_wh2 = st.columns(2)
            with col_wh1:
                weight_kg = st.number_input("Weight (kg)", 30.0, 200.0, 60.0, step=0.5, key="weight_smart")
                age       = st.number_input("Age", 10, 80, 20, key="age_smart")
            with col_wh2:
                height_cm = st.number_input("Height (cm)", 100.0, 250.0, 165.0, step=0.5, key="height_smart")
                sex       = st.radio("Sex", ["Male", "Female"], key="sex_smart")

            activity = st.selectbox("Activity level", list(ACTIVITY_LEVELS.keys()), index=2, key="activity_smart")

            # ── ALWAYS COMPUTE BOTH ──────────────────────────────────────────
            # FIX: Compute calculator values ALWAYS (so inputs are reactive)
            try:
                tdee_day  = compute_tdee(weight_kg, height_cm, age, sex, activity)
            except Exception:
                tdee_day = 2000.0
                
            n_campus = max(n_days_s, 1)
            tdee_week = tdee_day * n_campus
            
            calc_min_cals    = max(500, round(tdee_week * 0.85 / 500) * 500)
            calc_min_protein = max(5, round(weight_kg * 0.8 * n_campus / 5) * 5)
            calc_max_sodium  = max(500, round(2300 * n_campus / 500) * 500)
            calc_max_sugar   = max(50, round(50 * n_campus / 50) * 50)
            calc_max_fat     = max(50, round(65 * n_campus / 50) * 50)
            calc_budget      = weekly_budget_s_base
            calc_cal_targets = [400, 600, 350, 300]
            
            # Show TDEE info
            st.info(f"📊 Estimated TDEE: **{tdee_day:.0f} kcal/day**  |  Weekly target: **{tdee_week:.0f} kcal**")
            
            # ── DETERMINE FINAL VALUES ───────────────────────────────────────
                        # ── COMPUTE NUTRIENT TARGETS (reactive) ───────────────────────────
            # Personalised calculator
            try:
                tdee_day  = compute_tdee(weight_kg, height_cm, age, sex, activity)
            except Exception:
                tdee_day = 2000.0
                
            n_campus = max(n_days_s, 1)
            tdee_week = tdee_day * n_campus
            
            min_cals_s    = max(500, round(tdee_week * 0.85 / 500) * 500)
            min_protein_s = max(5, round(weight_kg * 0.8 * n_campus / 5) * 5)
            max_sodium_s  = max(500, round(2300 * n_campus / 500) * 500)
            max_sugar_s   = max(50, round(50 * n_campus / 50) * 50)
            max_fat_s     = max(50, round(65 * n_campus / 50) * 50)
            weekly_budget_s = weekly_budget_s_base
            def_cal_targets = [400, 600, 350, 300]
            
            st.markdown("---")
            st.markdown("### 📊 Auto-Calculated Targets")
            st.caption("🔄 These values update automatically when you change your details.")
            
            # Display auto-calculated targets (read-only, reactive)
                        # Display auto-calculated targets (read-only, reactive) with smaller font
            st.markdown("""
            <style>
                /* Smaller font for metric values in auto-calculated targets */
                [data-testid="stMetricValue"] {
                    font-size: 1.2rem !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            col_target1, col_target2 = st.columns(2)
            with col_target1:
                st.metric("Min Calories", f"{min_cals_s:,} kcal")
                st.metric("Min Protein", f"{min_protein_s:,} g")
                st.metric("Max Sodium", f"{max_sodium_s:,} mg")
            with col_target2:
                st.metric("Max Sugar", f"{max_sugar_s:,} g")
                st.metric("Max Fat", f"{max_fat_s:,} g")
                st.metric("Budget", f"PHP {weekly_budget_s:,}")
            
    

            st.markdown("### 🎯 Calorie Targets per Slot (kcal)")
            cal_targets_s = []
            for i in range(meals_per_day_s):
                t = st.number_input(
                    f"{meal_labels_s[i]} target (kcal)",
                    min_value=50, max_value=2000,
                    value=def_cal_targets[i] if i < len(def_cal_targets) else 400,
                    step=50, key=f"cal_target_s_{i}",
                )
                cal_targets_s.append(t)

            # Store all computed values in session state for use when running
            st.session_state["smart_min_cals"]    = min_cals_s
            st.session_state["smart_min_protein"] = min_protein_s
            st.session_state["smart_max_sodium"]  = max_sodium_s
            st.session_state["smart_max_sugar"]   = max_sugar_s
            st.session_state["smart_max_fat"]     = max_fat_s
            st.session_state["smart_budget"]      = weekly_budget_s
            st.session_state["smart_cal_targets"] = cal_targets_s

            st.markdown("---")
            run_btn_s = st.button("🚀 Run Meal Planner", type="primary", use_container_width=True, key="run_s")

    # ── Determine which tab triggered the run ─────────────────────────────────
        # ── Determine which tab triggered the run ─────────────────────────────────
    using_smart = run_btn_s
    run_btn     = run_btn_m or run_btn_s

    if using_smart:
        selected_days  = selected_days_s
        n_days         = n_days_s
        meals_per_day  = meals_per_day_s
        meal_labels    = meal_labels_s
        cal_targets    = st.session_state.get("smart_cal_targets", [400, 600, 350, 300])
        weekly_budget  = st.session_state.get("smart_budget", 750)
        num_drinks     = num_drinks_s
        # FIX 1: Use auto-calculated values from session state (reactive)
        max_sugar      = st.session_state.get("smart_max_sugar", 700)
        max_fat        = st.session_state.get("smart_max_fat", 400)
        max_sodium     = st.session_state.get("smart_max_sodium", 12000)
        min_protein    = st.session_state.get("smart_min_protein", 20)
        min_cals       = st.session_state.get("smart_min_cals", 7000)
        max_dup        = max_dup_s
        selected_locs  = selected_locs_s
    else:
        selected_days  = selected_days_m
        n_days         = n_days_m
        meals_per_day  = meals_per_day_m
        meal_labels    = meal_labels_m
        cal_targets    = cal_targets_m
        weekly_budget  = weekly_budget_m
        num_drinks     = num_drinks_m
        max_sugar      = max_sugar_m
        max_fat        = max_fat_m
        max_sodium     = max_sodium_m
        min_protein    = min_protein_m
        min_cals       = min_cals_m
        max_dup        = max_dup_m
        selected_locs  = selected_locs_m

    # ── Dataset Preview (always visible) ─────────────────────────────────────
    with st.expander("📋 Browse Full Dataset", expanded=False):
        filter_loc  = st.multiselect("Filter by location", options=loc_options, default=loc_options, key="browse_loc")
        filter_type = st.multiselect("Filter by type",
                                     options=["a_la_carte","drink","combo","meal"],
                                     default=["a_la_carte","drink","combo","meal"], key="browse_type")
        preview_df = df_all[
            df_all["location"].isin(filter_loc) & df_all["menu_type"].isin(filter_type)
        ].copy()
        preview_df["menu_item"] = preview_df["menu_item"].apply(fmt_name)
        # FIX 2: Themed dataframe styling (no black colors)
        styled = (
            preview_df[["location","menu_item","menu_type","calories_kcal",
                         "price","protein_g","fat_g","sugar_g","sodium_mg"]]
            .style
            .format({
                "calories_kcal": "{:.0f}",
                "price": "₱{:.2f}",
                "protein_g": "{:.1f}",
                "fat_g": "{:.1f}",
                "sugar_g": "{:.1f}",
                "sodium_mg": "{:.0f}",
            })
            .set_table_styles([
                {"selector": "thead th",
                 "props": [("background-color", "#7b1113"), ("color", "white"),
                           ("font-weight", "bold")]},
                {"selector": "tbody tr:nth-child(even)",
                 "props": [("background-color", "#fdf0f0")]},
                {"selector": "tbody tr:nth-child(odd)",
                 "props": [("background-color", "#fff8f5")]},
                {"selector": "tbody td",
                 "props": [("color", "#3a1a1a")]},
            ])
        )
        st.dataframe(styled, use_container_width=True, height=300)
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
        st.error("Please select at least one day on campus.")
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
  <p style="margin:0;font-size:0.9rem;color:#c62828 !important;"><strong>Auto-relaxation was attempted (10%, 30%, 50%, 70%, 90%) but could not find a feasible solution.</strong></p>
  <p style="margin:6px 0 0 0;font-size:0.9rem;color:#c62828 !important;">Try these additional fixes:</p>
  <ul style="margin:6px 0 0 0;font-size:0.9rem;color:#c62828 !important;">
    <li>Increase <strong>max duplicates</strong></li>
    <li>Raise nutrient limits (sugar / fat)</li>
    <li>Add more <strong>kiosk locations</strong></li>
    <li>Reduce <strong>number of days</strong> or <strong>meals per day</strong></li>
  </ul>
</div>""", unsafe_allow_html=True)
        return

    result_df = result["result_df"]

    # ── Show relaxation notice if any were applied ────────────────────────────
    if result.get("relaxations_applied"):
        relaxation_list = "<br>".join(f"• {r}" for r in result["relaxations_applied"])
        st.markdown(f"""<div class="relaxation-box">
  <strong>⚠️ Auto-Relaxation Applied</strong><br>
  The original constraints were infeasible. The solver automatically relaxed the following:<br>
  {relaxation_list}<br>
  <small>Final effective values — Min Calories: {result['relaxed_min_cals']:,.0f} kcal &nbsp;|&nbsp;
  Min Protein: {result['relaxed_min_protein']:,.0f} g &nbsp;|&nbsp;
  Max Sodium: {result['relaxed_max_sodium']:,.0f} mg &nbsp;|&nbsp;
  Budget: ₱{result['relaxed_budget']:,.2f}</small>
</div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    #  TAB LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    tab3, tab1, tab2, tab4 = st.tabs(["🗓️ Weekly Schedule", "📊 Summary", "📋 Selected Items", "💡 Tips & Charts"])

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 1 — WEEKLY SCHEDULE
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-header">📊 Optimisation Results</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="section-header">✅ Constraint Verification</div>', unsafe_allow_html=True)
        checks = [
            ("Meal slots filled",  sum(result["sel_food"])+sum(result["sel_combo"])+sum(result["sel_meal"]) == M,
             f"{sum(result['sel_food'])+sum(result['sel_combo'])+sum(result['sel_meal'])} / {M}"),
            ("Drinks",             sum(result["sel_drink"]) == num_drinks,
             f"{sum(result['sel_drink'])} / {num_drinks}"),
            ("Within budget",      result["total_cost"] <= weekly_budget,
             f"PHP {result['total_cost']:.2f} / {weekly_budget:.2f}"),
            ("Sugar ≤ limit",      result["total_sugar"] <= max_sugar,
             f"{result['total_sugar']:.1f} / {max_sugar} g"),
            ("Fat ≤ limit",        result["total_fat"] <= max_fat,
             f"{result['total_fat']:.1f} / {max_fat} g"),
            ("Sodium ≤ limit",     result["total_sodium"] <= max_sodium,
             f"{result['total_sodium']:.1f} / {max_sodium} mg"),
            ("Protein ≥ minimum",  result["total_protein"] >= min_protein,
             f"{result['total_protein']:.1f} / {min_protein} g"),
            ("Calories ≥ minimum", result["total_calories"] >= min_cals,
             f"{result['total_calories']:.0f} / {min_cals} kcal"),
        ]
        cc1, cc2 = st.columns(2)
        for i, (label, ok, detail) in enumerate(checks):
            col = cc1 if i % 2 == 0 else cc2
            with col:
                icon  = "✅" if ok else "❌"
                color = "#2e7d32" if ok else "#c62828"
                st.markdown(f"""<div style="display:flex;align-items:center;padding:6px 0;border-bottom:1px solid #f0ece8;font-size:0.9rem">
  <span style="font-size:1.1rem;margin-right:8px">{icon}</span>
  <span style="flex:1;color:#1a1a1a">{label}</span>
  <span style="color:{color};font-weight:600">{detail}</span>
</div>""", unsafe_allow_html=True)

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
    #  TAB 2 — SELECTED ITEMS (FIX 2: themed dataframe)
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

            styled_df = (
                display_df.style
                .format({
                    "Price (PHP)": "₱{:.2f}", "Total Cost": "₱{:.2f}",
                    "Calories": "{:.0f}",      "Total Cal": "{:.0f}",
                    "Protein (g)": "{:.1f}",   "Fat (g)": "{:.1f}",
                    "Sugar (g)": "{:.1f}",     "Sodium (mg)": "{:.0f}",
                })
                .bar(subset=["Total Cal"], color="#e57373")
                .set_table_styles([
                    {"selector": "thead th",
                     "props": [("background-color", "#7b1113"), ("color", "white"), ("font-weight", "bold")]},
                    {"selector": "tbody tr:nth-child(even)",
                     "props": [("background-color", "#fdf0f0")]},
                    {"selector": "tbody tr:nth-child(odd)",
                     "props": [("background-color", "#fff8f5")]},
                    {"selector": "tbody td",
                     "props": [("color", "#3a1a1a")]},
                ])
            )
            st.dataframe(styled_df, use_container_width=True, height=400)

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
    #  TAB 3 — WEEKLY SCHEDULE (FIX 3: drinks within meal locations)
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">🗓️ Weekly Eating Schedule</div>', unsafe_allow_html=True)

        schedule = build_schedule(
            result_df, n_days, meals_per_day,
            meal_labels, num_drinks, selected_days,
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

                # Collect locations of meals on this day
                day_meal_locations = set()
                for slot in day_info["slots"]:
                    item = slot["item"]
                    if item is not None:
                        day_meal_locations.add(item.get("location", ""))

                for slot in day_info["slots"]:
                    item  = slot["item"]
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

                # FIX 3: drink only appears if there's food in this day's slots,
                # and is placed within the meal locations context
                drink_html = ""
                day_has_food = any(s["item"] is not None for s in day_info["slots"])
                if day_info["drink"] and day_has_food:
                    dk = day_info["drink"]
                    dk_name  = fmt_name(dk["menu_item"])
                    dk_loc   = dk["location"]
                    dk_cal   = float(dk["calories_kcal"])
                    dk_price = float(dk["price"])
                    
                    # Show if drink location matches any meal location on this day
                    location_match_note = ""
                    if dk_loc in day_meal_locations:
                        location_match_note = " ✅ Same kiosk as meals"
                    
                    drink_html = f"""<div class="slot-row">
<div class="slot-label">🧃 Drink</div>
<div class="slot-item">
<div class="item-name">{dk_name}</div>
<div class="item-meta">
  {badge_html("drink")}
  📍 {dk_loc.replace("_"," ").title()} &nbsp;
  🔥 {dk_cal:.0f} kcal &nbsp;
  💰 PHP {dk_price:.0f}{location_match_note}
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

            st.markdown(f"""
<div style="background:linear-gradient(90deg,#7b1113,#c0392b); color:white; border-radius:10px; padding:18px 24px; margin-top:10px; font-family: sans-serif;">
  <div style="font-size:1.1rem; font-weight:800; margin-bottom:10px; color:white;">📊 Weekly Schedule Summary</div>
  <div style="display:flex; gap:40px; flex-wrap:wrap">
    <div>
      <div style="font-size:0.8rem; color:white;">Total Calories</div>
      <div style="font-size:1.4rem; font-weight:700; color:white;">{week_cal:,.0f} kcal</div>
    </div>
    <div>
      <div style="font-size:0.8rem; color:white;">Total Spend</div>
      <div style="font-size:1.4rem; font-weight:700; color:white;">PHP {week_cost:,.2f}</div>
    </div>
    <div>
      <div style="font-size:0.8rem; color:white;">Avg Daily Calories</div>
      <div style="font-size:1.4rem; font-weight:700; color:white;">{week_cal/n_days:,.0f} kcal</div>
    </div>
    <div>
      <div style="font-size:0.8rem; color:white;">Avg Daily Spend</div>
      <div style="font-size:1.4rem; font-weight:700; color:white;">PHP {week_cost/n_days:,.2f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════════════════════
    #  TAB 4 — TIPS & CHARTS (FIX 2: themed colors, black legends/ticks)
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

        if not result_df.empty:
            st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)

            chart1, chart2 = st.columns(2)
            with chart1:
                type_cal = result_df.groupby("type")["total_cal"].sum().reset_index()
                type_cal["type_label"] = type_cal["type"].map({
                    "a_la_carte": "A La Carte", "drink": "Drink",
                    "combo": "Combo", "meal": "Meal"
                })
                # FIX 2: Maroon-themed pie chart with black legend font
                fig_pie = px.pie(
                    type_cal, values="total_cal", names="type_label",
                    title="Calories by Food Type",
                    color_discrete_sequence=["#7b1113","#c0392b","#e57373","#ffcdd2"],
                )
                fig_pie.update_layout(
                    margin=dict(t=40,b=0,l=0,r=0),
                    paper_bgcolor="#fff8f5",
                    plot_bgcolor="#fff8f5",
                    font=dict(color="#3a1a1a"),
                    title=dict(font=dict(color="#7b1113")),
                    legend=dict(
                        font=dict(
                            color="black",  # Black legend text
                            size=12,
                        ),
                    ),
                )
                # Make the percentage and label text inside slices black
                fig_pie.update_traces(
                    textfont=dict(color="black"),
                    textposition="inside",
                    textinfo="percent+label",
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with chart2:
                loc_spend = result_df.groupby("location")["total_cost"].sum().reset_index()
                loc_spend["location"] = loc_spend["location"].str.replace("_"," ").str.title()
                loc_spend = loc_spend.sort_values("total_cost", ascending=True)
                # FIX 2: Maroon-themed bar chart with black ticks and numbers
                fig_bar = px.bar(
                    loc_spend, x="total_cost", y="location",
                    orientation="h", title="Total Spend by Kiosk (PHP)",
                    color="total_cost",
                    color_continuous_scale=["#ffcdd2","#7b1113"],
                    labels={"total_cost": "PHP", "location": "Kiosk"},
                )
                fig_bar.update_layout(
                    margin=dict(t=40,b=0,l=0,r=0), 
                    showlegend=False,
                    coloraxis_showscale=False,
                    paper_bgcolor="#fff8f5",
                    plot_bgcolor="#fff8f5",
                    font=dict(color="#3a1a1a"),
                    title=dict(font=dict(color="#7b1113")),
                    xaxis=dict(
                        tickfont=dict(color="black", size=11),  # Black x-axis ticks
                        title_font=dict(color="black", size=12),  # Black x-axis title
                        gridcolor="#f0d8d8",
                        linecolor="#e8d5d5",
                    ),
                    yaxis=dict(
                        tickfont=dict(color="black", size=11),  # Black y-axis ticks
                        title_font=dict(color="black", size=12),  # Black y-axis title
                        gridcolor="#f0d8d8",
                        linecolor="#e8d5d5",
                    ),
                )
                # Make the value labels on bars black
                fig_bar.update_traces(
                    textfont=dict(color="black"),
                    texttemplate="%{x:.0f}",
                    textposition="outside",
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("#### 🕸️ Nutrient Usage (% of limit)")
            nutrients = {
                "Sugar":    (result["total_sugar"],    max_sugar),
                "Fat":      (result["total_fat"],      max_fat),
                "Sodium":   (result["total_sodium"],   max_sodium),
                "Protein":  (result["total_protein"],  min_protein),
                "Calories": (result["total_calories"], min_cals),
            }
            cats   = list(nutrients.keys())
            values = [min(v/l*100, 150) for v, l in nutrients.values()]
            values += [values[0]]
            cats   += [cats[0]]

            # FIX 2: Maroon-themed radar chart with black text
            fig_radar = go.Figure(go.Scatterpolar(
                r=values, theta=cats,
                fill="toself", fillcolor="rgba(123,17,19,0.15)",
                line=dict(color="#7b1113", width=2),
                name="Nutrient Usage",
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0,150],
                        ticksuffix="%", 
                        tickfont=dict(size=9, color="black"),  # Black radial ticks
                        gridcolor="#f0d8d8",
                        linecolor="#e8d5d5",
                    ),
                    angularaxis=dict(
                        tickfont=dict(color="black"),  # Black category labels
                        gridcolor="#f0d8d8",
                        linecolor="#e8d5d5",
                    ),
                    bgcolor="#fff8f5",
                ),
                showlegend=False, 
                margin=dict(t=20,b=20,l=40,r=40),
                height=380,
                paper_bgcolor="#fff8f5",
                font=dict(color="#3a1a1a"),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            st.markdown("#### 🏆 Top 10 Items by Total Calories")
            top10 = result_df.nlargest(10, "total_cal")[
                ["menu_item","location","type","total_cal","total_cost"]
            ].copy()
            top10["menu_item"] = top10["menu_item"].apply(fmt_name)
            top10["location"]  = top10["location"].str.replace("_"," ").str.title()
            top10.columns = ["Item","Kiosk","Type","Total Cal (kcal)","Total Cost (PHP)"]

            # FIX 2: themed top-10 table
            styled_top10 = (
                top10.style
                .format({"Total Cal (kcal)": "{:.0f}", "Total Cost (PHP)": "₱{:.2f}"})
                .set_table_styles([
                    {"selector": "thead th",
                     "props": [("background-color", "#7b1113"), ("color", "white"), ("font-weight", "bold")]},
                    {"selector": "tbody tr:nth-child(even)",
                     "props": [("background-color", "#fdf0f0")]},
                    {"selector": "tbody tr:nth-child(odd)",
                     "props": [("background-color", "#fff8f5")]},
                    {"selector": "tbody td",
                     "props": [("color", "#3a1a1a")]},
                ])
            )
            st.dataframe(styled_top10, use_container_width=True, hide_index=True)
    


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()