import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# ==========================================================
# CONFIG
# ==========================================================
st.set_page_config(page_title="Waribei – CM1 / CM2 / Break-even", layout="wide")

# ----------------------------------------------------------
# DEFAULTS / PRESETS
# ----------------------------------------------------------
DEFAULT_DATE = date(2026, 6, 1)
HISTORY_DATES = [date(2025, 6, 1), date(2025, 12, 1), date(2026, 6, 1)]

PRESETS_BY_DATE = {
    date(2025, 6, 1): {
        "name": "Historique – Jun 2025",
        "revenu_pct": 3.73,
        "cout_paiement_pct": 1.75,
        "cout_liquidite_10j_pct": 0.21,
        "expected_loss_pct": 1.43,
        "cost_of_service_pct": 0.65,
        "loan_book_k": 140.0,
        "cycles_per_month": 2.9,
        "sales_marketing_opex_monthly": 2240.0,
        "it_product_opex_monthly": 3630.0,
        "ga_opex_monthly": 5820.0,
    },
    date(2025, 12, 1): {
        "name": "Historique – Dec 2025",
        "revenu_pct": 3.76,
        "cout_paiement_pct": 1.80,
        "cout_liquidite_10j_pct": 0.36,
        "expected_loss_pct": 1.00,
        "cost_of_service_pct": 0.55,
        "loan_book_k": 155.0,
        "cycles_per_month": 2.9,
        "sales_marketing_opex_monthly": 2526.0,
        "it_product_opex_monthly": 4000.0,
        "ga_opex_monthly": 6500.0,
    },
    date(2026, 6, 1): {
        "name": "Base – Jun 2026",
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.20,
        "cout_liquidite_10j_pct": 0.40,
        "expected_loss_pct": 1.00,
        "cost_of_service_pct": 0.45,
        "loan_book_k": 320.0,
        "cycles_per_month": 2.9,
        "sales_marketing_opex_monthly": 3500.0,
        "it_product_opex_monthly": 4200.0,
        "ga_opex_monthly": 7000.0,
    },
}

SCENARIOS_PRESETS = {
    "Custom": None,
    "Base scénario — Aujourd’hui": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.60,
        "cout_liquidite_10j_pct": 0.40,
        "expected_loss_pct": 1.00,
        "cost_of_service_pct": 0.52,
        "loan_book_k": 225.0,
        "cycles_per_month": 2.9,
        "sales_marketing_opex_monthly": 3600.0,
        "it_product_opex_monthly": 4100.0,
        "ga_opex_monthly": 6900.0,
        "scenario_name_autofill": "Base scénario — Aujourd’hui",
    },
    "Scénario 1 — Optimisation légère": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.20,
        "cout_liquidite_10j_pct": 0.40,
        "expected_loss_pct": 0.90,
        "cost_of_service_pct": 0.45,
        "loan_book_k": 320.0,
        "cycles_per_month": 2.9,
        "sales_marketing_opex_monthly": 3600.0,
        "it_product_opex_monthly": 4100.0,
        "ga_opex_monthly": 6900.0,
        "scenario_name_autofill": "Scénario 1 — Optimisation légère",
    },
    "Scénario 2 — Open Banking": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 0.50,
        "cout_liquidite_10j_pct": 0.40,
        "expected_loss_pct": 0.62,
        "cost_of_service_pct": 0.40,
        "loan_book_k": 320.0,
        "cycles_per_month": 3.0,
        "sales_marketing_opex_monthly": 3400.0,
        "it_product_opex_monthly": 4100.0,
        "ga_opex_monthly": 6900.0,
        "scenario_name_autofill": "Scénario 2 — Open Banking",
    },
    "Scénario 3 — Scale disciplinée": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.00,
        "cout_liquidite_10j_pct": 0.40,
        "expected_loss_pct": 0.80,
        "cost_of_service_pct": 0.40,
        "loan_book_k": 500.0,
        "cycles_per_month": 3.0,
        "sales_marketing_opex_monthly": 4500.0,
        "it_product_opex_monthly": 4500.0,
        "ga_opex_monthly": 7400.0,
        "scenario_name_autofill": "Scénario 3 — Scale disciplinée",
    },
}

# ----------------------------------------------------------
# STYLE
# ----------------------------------------------------------
st.markdown(
    """
    <style>
    .metric-card {
        padding: 14px 16px;
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 16px;
        background: white;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        min-height: 105px;
    }
    .metric-label {
        font-size: 13px;
        color: rgba(0,0,0,0.65);
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        line-height: 1.05;
        color: #064C72;
    }
    .metric-sub {
        margin-top: 8px;
        font-size: 12px;
        color: rgba(0,0,0,0.58);
    }
    .section-note {
        font-size: 13px;
        color: rgba(0,0,0,0.68);
        margin-top: -4px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def euro(x):
    return f"€{x:,.0f}".replace(",", " ")

def euro1(x):
    return f"€{x:,.1f}".replace(",", " ")

def pct(x):
    return f"{x:.2f}%"

def safe_div(a, b):
    return a / b if b else 0.0

def metric_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def init_state():
    if "scenario_date" not in st.session_state:
        st.session_state["scenario_date"] = DEFAULT_DATE

    if "saved_scenarios" not in st.session_state:
        st.session_state["saved_scenarios"] = [
            {"date": date(2025, 6, 1), "name": "Historique – Jun 2025"},
            {"date": date(2025, 12, 1), "name": "Historique – Dec 2025"},
            {"date": date(2026, 6, 1), "name": "Base – Jun 2026"},
        ]

def apply_preset_for_date(d):
    preset = PRESETS_BY_DATE.get(d)
    if preset:
        for k, v in preset.items():
            st.session_state[f"in_{k}"] = v

def apply_scenario_preset(name):
    cfg = SCENARIOS_PRESETS.get(name)
    if cfg:
        for k, v in cfg.items():
            st.session_state[f"in_{k}"] = v

def compute_model(
    revenu_pct,
    cout_paiement_pct,
    cout_liquidite_10j_pct,
    expected_loss_pct,
    cost_of_service_pct,
    loan_book_k,
    cycles_per_month,
    sales_marketing_opex_monthly,
    it_product_opex_monthly,
    ga_opex_monthly,
    sales_marketing_variable_ratio,
    it_product_variable_ratio,
    ga_variable_ratio,
):
    # Volume
    loan_book_eur = loan_book_k * 1000
    monthly_tpv_eur = loan_book_eur * cycles_per_month

    # Revenue & direct costs
    monthly_revenue_eur = monthly_tpv_eur * revenu_pct / 100
    monthly_payment_cost_eur = monthly_tpv_eur * cout_paiement_pct / 100
    monthly_liquidity_cost_eur = monthly_tpv_eur * cout_liquidite_10j_pct / 100

    # CM1
    cm1_eur = monthly_revenue_eur - monthly_payment_cost_eur - monthly_liquidity_cost_eur
    cm1_pct = safe_div(cm1_eur, monthly_tpv_eur) * 100

    # Variable operating load
    monthly_cost_of_service_eur = monthly_tpv_eur * cost_of_service_pct / 100
    monthly_expected_loss_eur = monthly_tpv_eur * expected_loss_pct / 100

    sales_marketing_variable = sales_marketing_opex_monthly * sales_marketing_variable_ratio
    sales_marketing_fixed = sales_marketing_opex_monthly * (1 - sales_marketing_variable_ratio)

    it_product_variable = it_product_opex_monthly * it_product_variable_ratio
    it_product_fixed = it_product_opex_monthly * (1 - it_product_variable_ratio)

    ga_variable = ga_opex_monthly * ga_variable_ratio
    ga_fixed = ga_opex_monthly * (1 - ga_variable_ratio)

    variable_opex_eur = sales_marketing_variable + it_product_variable + ga_variable
    fixed_opex_eur = sales_marketing_fixed + it_product_fixed + ga_fixed

    # CM2
    cm2_eur = (
        cm1_eur
        - monthly_cost_of_service_eur
        - monthly_expected_loss_eur
        - variable_opex_eur
    )
    cm2_pct = safe_div(cm2_eur, monthly_tpv_eur) * 100

    # Break-even contribution
    break_even_contribution_eur = cm2_eur - fixed_opex_eur
    opex_coverage_pct = safe_div(cm2_eur, fixed_opex_eur) * 100
    net_operating_margin_pct = safe_div(break_even_contribution_eur, monthly_tpv_eur) * 100

    return {
        "loan_book_eur": loan_book_eur,
        "monthly_tpv_eur": monthly_tpv_eur,
        "monthly_revenue_eur": monthly_revenue_eur,
        "monthly_payment_cost_eur": monthly_payment_cost_eur,
        "monthly_liquidity_cost_eur": monthly_liquidity_cost_eur,
        "cm1_eur": cm1_eur,
        "cm1_pct": cm1_pct,
        "monthly_cost_of_service_eur": monthly_cost_of_service_eur,
        "monthly_expected_loss_eur": monthly_expected_loss_eur,
        "sales_marketing_variable": sales_marketing_variable,
        "sales_marketing_fixed": sales_marketing_fixed,
        "it_product_variable": it_product_variable,
        "it_product_fixed": it_product_fixed,
        "ga_variable": ga_variable,
        "ga_fixed": ga_fixed,
        "variable_opex_eur": variable_opex_eur,
        "fixed_opex_eur": fixed_opex_eur,
        "cm2_eur": cm2_eur,
        "cm2_pct": cm2_pct,
        "break_even_contribution_eur": break_even_contribution_eur,
        "opex_coverage_pct": opex_coverage_pct,
        "net_operating_margin_pct": net_operating_margin_pct,
    }

def make_waterfall_df(m):
    rows = [
        ("Revenue", m["monthly_revenue_eur"]),
        ("Payment fees", -m["monthly_payment_cost_eur"]),
        ("Liquidity cost", -m["monthly_liquidity_cost_eur"]),
        ("CM1", m["cm1_eur"]),
        ("Cost of service", -m["monthly_cost_of_service_eur"]),
        ("Expected losses", -m["monthly_expected_loss_eur"]),
        ("Variable OPEX", -m["variable_opex_eur"]),
        ("CM2", m["cm2_eur"]),
        ("Fixed OPEX", -m["fixed_opex_eur"]),
        ("Break-even contribution", m["break_even_contribution_eur"]),
    ]

    df = pd.DataFrame(rows, columns=["step", "value"])

    starts, ends, kinds = [], [], []
    running = 0.0
    total_steps = {"CM1", "CM2", "Break-even contribution"}

    for _, row in df.iterrows():
        step = row["step"]
        val = row["value"]

        if step in total_steps:
            starts.append(0.0)
            ends.append(val)
            kinds.append("total")
        else:
            starts.append(running)
            running += val
            ends.append(running)
            kinds.append("positive" if val >= 0 else "negative")

    df["start"] = starts
    df["end"] = ends
    df["kind"] = kinds
    return df

def make_break_even_curve(base_inputs):
    rows = []
    for loan_book_k in range(100, 901, 25):
        m = compute_model(
            revenu_pct=base_inputs["revenu_pct"],
            cout_paiement_pct=base_inputs["cout_paiement_pct"],
            cout_liquidite_10j_pct=base_inputs["cout_liquidite_10j_pct"],
            expected_loss_pct=base_inputs["expected_loss_pct"],
            cost_of_service_pct=base_inputs["cost_of_service_pct"],
            loan_book_k=loan_book_k,
            cycles_per_month=base_inputs["cycles_per_month"],
            sales_marketing_opex_monthly=base_inputs["sales_marketing_opex_monthly"],
            it_product_opex_monthly=base_inputs["it_product_opex_monthly"],
            ga_opex_monthly=base_inputs["ga_opex_monthly"],
            sales_marketing_variable_ratio=base_inputs["sales_marketing_variable_ratio"],
            it_product_variable_ratio=base_inputs["it_product_variable_ratio"],
            ga_variable_ratio=base_inputs["ga_variable_ratio"],
        )
        rows.append(
            {
                "loan_book_k": loan_book_k,
                "tpv_eur": m["monthly_tpv_eur"],
                "cm2_eur": m["cm2_eur"],
                "fixed_opex_eur": m["fixed_opex_eur"],
                "break_even_contribution_eur": m["break_even_contribution_eur"],
            }
        )
    return pd.DataFrame(rows)

# ----------------------------------------------------------
# INIT
# ----------------------------------------------------------
init_state()
apply_preset_for_date(st.session_state["scenario_date"])

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.title("Waribei – CM1 / CM2 / Break-even Dashboard")
st.caption(
    "Lecture recommandée : CM1 = moteur transactionnel, CM2 = croissance réellement contributive, Break-even contribution = CM2 après structure fixe."
)

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.header("Scénarios")

    quick = st.selectbox("Preset rapide", list(SCENARIOS_PRESETS.keys()))
    if quick != "Custom":
        apply_scenario_preset(quick)

    dcols = st.columns([0.7, 0.3])
    with dcols[0]:
        picked = st.date_input("Date", value=st.session_state["scenario_date"])
        st.session_state["scenario_date"] = picked
    with dcols[1]:
        if st.button("Today"):
            st.session_state["scenario_date"] = DEFAULT_DATE
            apply_preset_for_date(DEFAULT_DATE)

    st.markdown("---")
    st.subheader("Inputs business")

    revenu_pct = st.slider("Revenue % TPV", 0.0, 8.0, float(st.session_state.get("in_revenu_pct", 3.80)), 0.01)
    cout_paiement_pct = st.slider("Payment cost % TPV", 0.0, 4.0, float(st.session_state.get("in_cout_paiement_pct", 1.20)), 0.01)
    cout_liquidite_10j_pct = st.slider("Liquidity cost % TPV", 0.0, 3.0, float(st.session_state.get("in_cout_liquidite_10j_pct", 0.40)), 0.01)
    expected_loss_pct = st.slider("Expected credit loss % TPV", 0.0, 5.0, float(st.session_state.get("in_expected_loss_pct", 1.00)), 0.01)
    cost_of_service_pct = st.slider("Cost of service % TPV", 0.0, 3.0, float(st.session_state.get("in_cost_of_service_pct", 0.45)), 0.01)

    loan_book_k = st.slider("Loan book (€k)", 50.0, 1000.0, float(st.session_state.get("in_loan_book_k", 320.0)), 5.0)
    cycles_per_month = st.slider("Cycles / month", 1.0, 5.0, float(st.session_state.get("in_cycles_per_month", 2.9)), 0.1)

    st.markdown("---")
    st.subheader("OPEX mensuels (€)")

    sales_marketing_opex_monthly = st.number_input(
        "Sales & Marketing OPEX",
        min_value=0.0,
        value=float(st.session_state.get("in_sales_marketing_opex_monthly", 3500.0)),
        step=100.0,
    )
    it_product_opex_monthly = st.number_input(
        "IT & Product OPEX",
        min_value=0.0,
        value=float(st.session_state.get("in_it_product_opex_monthly", 4200.0)),
        step=100.0,
    )
    ga_opex_monthly = st.number_input(
        "G&A OPEX",
        min_value=0.0,
        value=float(st.session_state.get("in_ga_opex_monthly", 7000.0)),
        step=100.0,
    )

    st.markdown("---")
    st.subheader("Ratios de variabilisation")

    sales_marketing_variable_ratio = st.slider("Part variable Sales & Marketing", 0.0, 1.0, 0.70, 0.05)
    it_product_variable_ratio = st.slider("Part variable IT & Product", 0.0, 1.0, 0.10, 0.05)
    ga_variable_ratio = st.slider("Part variable G&A", 0.0, 1.0, 0.05, 0.05)

    st.markdown("---")
    scenario_name = st.text_input("Label du scénario", value=SCENARIOS_PRESETS.get(quick, {}).get("scenario_name_autofill", "Custom scenario") if SCENARIOS_PRESETS.get(quick) else "Custom scenario")

# ----------------------------------------------------------
# MODEL
# ----------------------------------------------------------
base_inputs = {
    "revenu_pct": revenu_pct,
    "cout_paiement_pct": cout_paiement_pct,
    "cout_liquidite_10j_pct": cout_liquidite_10j_pct,
    "expected_loss_pct": expected_loss_pct,
    "cost_of_service_pct": cost_of_service_pct,
    "loan_book_k": loan_book_k,
    "cycles_per_month": cycles_per_month,
    "sales_marketing_opex_monthly": sales_marketing_opex_monthly,
    "it_product_opex_monthly": it_product_opex_monthly,
    "ga_opex_monthly": ga_opex_monthly,
    "sales_marketing_variable_ratio": sales_marketing_variable_ratio,
    "it_product_variable_ratio": it_product_variable_ratio,
    "ga_variable_ratio": ga_variable_ratio,
}

m = compute_model(**base_inputs)

# ----------------------------------------------------------
# TOP KPIs
# ----------------------------------------------------------
st.markdown("## Vue synthétique")
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    metric_card("CM1 %", pct(m["cm1_pct"]), "Revenue – payment – liquidité")
with k2:
    metric_card("CM1 € / mois", euro(m["cm1_eur"]), f"sur {euro(m['monthly_tpv_eur'])} de TPV")
with k3:
    metric_card("CM2 %", pct(m["cm2_pct"]), "après service, risque et OPEX variables")
with k4:
    metric_card("CM2 € / mois", euro(m["cm2_eur"]), "contribution économique réelle")
with k5:
    metric_card("OPEX coverage", pct(m["opex_coverage_pct"]), "CM2 / OPEX fixes")
with k6:
    metric_card("Break-even contribution", euro(m["break_even_contribution_eur"]), "CM2 – OPEX fixes")

st.markdown("## Lecture business")
st.markdown(
    """
    <div class="section-note">
    CM1 te dit si le moteur transactionnel est sain. CM2 te dit si ta croissance marginale crée de la valeur.
    Break-even contribution te dit si la structure actuelle peut être absorbée.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
# DETAIL TABLES
# ----------------------------------------------------------
c1, c2 = st.columns([0.52, 0.48])

with c1:
    st.markdown("### Unit economics (% du TPV)")
    unit_df = pd.DataFrame(
        [
            ("Revenue", revenu_pct),
            ("Payment fees", -cout_paiement_pct),
            ("Liquidity cost", -cout_liquidite_10j_pct),
            ("CM1", m["cm1_pct"]),
            ("Cost of service", -cost_of_service_pct),
            ("Expected losses", -expected_loss_pct),
            ("Variable OPEX", -safe_div(m["variable_opex_eur"], m["monthly_tpv_eur"]) * 100),
            ("CM2", m["cm2_pct"]),
            ("Fixed OPEX", -safe_div(m["fixed_opex_eur"], m["monthly_tpv_eur"]) * 100),
            ("Break-even contribution", m["net_operating_margin_pct"]),
        ],
        columns=["Line item", "% TPV"],
    )
    st.dataframe(unit_df.style.format({"% TPV": "{:.2f}%"}), use_container_width=True)

with c2:
    st.markdown("### Lecture mensuelle (€)")
    monthly_df = pd.DataFrame(
        [
            ("Loan book", m["loan_book_eur"]),
            ("TPV mensuel", m["monthly_tpv_eur"]),
            ("Revenue", m["monthly_revenue_eur"]),
            ("Payment fees", m["monthly_payment_cost_eur"]),
            ("Liquidity cost", m["monthly_liquidity_cost_eur"]),
            ("CM1", m["cm1_eur"]),
            ("Cost of service", m["monthly_cost_of_service_eur"]),
            ("Expected losses", m["monthly_expected_loss_eur"]),
            ("Variable OPEX", m["variable_opex_eur"]),
            ("CM2", m["cm2_eur"]),
            ("Fixed OPEX", m["fixed_opex_eur"]),
            ("Break-even contribution", m["break_even_contribution_eur"]),
        ],
        columns=["Line item", "€ / month"],
    )
    st.dataframe(monthly_df.style.format({"€ / month": "€{:,.0f}"}), use_container_width=True)

# ----------------------------------------------------------
# RECLASSIFICATION VIEW
# ----------------------------------------------------------
st.markdown("## Reclassification des coûts")
r1, r2, r3 = st.columns(3)

with r1:
    st.markdown("### Variable pur")
    st.dataframe(
        pd.DataFrame(
            [
                ("Cost of service", m["monthly_cost_of_service_eur"]),
                ("Expected losses", m["monthly_expected_loss_eur"]),
                ("S&M variable", m["sales_marketing_variable"]),
                ("IT/Product variable", m["it_product_variable"]),
                ("G&A variable", m["ga_variable"]),
            ],
            columns=["Item", "€/mois"],
        ).style.format({"€/mois": "€{:,.0f}"}),
        use_container_width=True,
    )

with r2:
    st.markdown("### Fixe pur")
    st.dataframe(
        pd.DataFrame(
            [
                ("S&M fixe", m["sales_marketing_fixed"]),
                ("IT/Product fixe", m["it_product_fixed"]),
                ("G&A fixe", m["ga_fixed"]),
            ],
            columns=["Item", "€/mois"],
        ).style.format({"€/mois": "€{:,.0f}"}),
        use_container_width=True,
    )

with r3:
    st.markdown("### Totaux")
    reclass_totals = pd.DataFrame(
        [
            ("Variable OPEX total", m["variable_opex_eur"]),
            ("Fixed OPEX total", m["fixed_opex_eur"]),
            ("CM2", m["cm2_eur"]),
            ("Break-even contribution", m["break_even_contribution_eur"]),
        ],
        columns=["Item", "€/mois"],
    )
    st.dataframe(reclass_totals.style.format({"€/mois": "€{:,.0f}"}), use_container_width=True)

# ----------------------------------------------------------
# WATERFALL
# ----------------------------------------------------------
st.markdown("## Waterfall économique")
wf_df = make_waterfall_df(m)

color_scale = alt.Scale(
    domain=["positive", "negative", "total"],
    range=["#1B5A43", "#F83131", "#064C72"],
)

waterfall_chart = (
    alt.Chart(wf_df)
    .mark_bar()
    .encode(
        x=alt.X("step:N", sort=list(wf_df["step"]), title=None),
        y=alt.Y("start:Q", title="€"),
        y2="end:Q",
        color=alt.Color("kind:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("step:N", title="Step"),
            alt.Tooltip("value:Q", title="Value", format=",.0f"),
        ],
    )
)

waterfall_labels = (
    alt.Chart(wf_df)
    .mark_text(dy=-6, color="#333", fontSize=11)
    .encode(
        x=alt.X("step:N", sort=list(wf_df["step"])),
        y="end:Q",
        text=alt.Text("value:Q", format=",.0f"),
    )
)

st.altair_chart((waterfall_chart + waterfall_labels).properties(height=360), use_container_width=True)

# ----------------------------------------------------------
# BREAK-EVEN CURVE
# ----------------------------------------------------------
st.markdown("## Courbe de break-even")
curve_df = make_break_even_curve(base_inputs)

cm2_line = (
    alt.Chart(curve_df)
    .mark_line(point=False)
    .encode(
        x=alt.X("loan_book_k:Q", title="Loan book (€k)"),
        y=alt.Y("cm2_eur:Q", title="€ / month"),
        tooltip=[
            alt.Tooltip("loan_book_k:Q", title="Loan book (€k)", format=".0f"),
            alt.Tooltip("cm2_eur:Q", title="CM2", format=",.0f"),
        ],
    )
)

fixed_line = (
    alt.Chart(curve_df)
    .mark_line(strokeDash=[4, 4])
    .encode(
        x="loan_book_k:Q",
        y="fixed_opex_eur:Q",
        tooltip=[alt.Tooltip("fixed_opex_eur:Q", title="Fixed OPEX", format=",.0f")],
    )
)

be_line = (
    alt.Chart(curve_df)
    .mark_line(color="#F59E0B")
    .encode(
        x="loan_book_k:Q",
        y="break_even_contribution_eur:Q",
        tooltip=[alt.Tooltip("break_even_contribution_eur:Q", title="Break-even contribution", format=",.0f")],
    )
)

zero_rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="gray").encode(y="y:Q")

st.altair_chart((cm2_line + fixed_line + be_line + zero_rule).properties(height=340), use_container_width=True)

# ----------------------------------------------------------
# SCENARIO SAVE / HISTORY
# ----------------------------------------------------------
st.markdown("## Historique de scénarios")

save_col1, save_col2 = st.columns([0.25, 0.75])
with save_col1:
    if st.button("SAVE current scenario"):
        d = st.session_state["scenario_date"]
        record = {
            "date": d,
            "name": scenario_name,
            "cm1_pct": m["cm1_pct"],
            "cm2_pct": m["cm2_pct"],
            "break_even_contribution_eur": m["break_even_contribution_eur"],
            "loan_book_k": loan_book_k,
        }

        replaced = False
        for i, s in enumerate(st.session_state["saved_scenarios"]):
            if s.get("date") == d:
                st.session_state["saved_scenarios"][i] = record
                replaced = True
                break
        if not replaced:
            st.session_state["saved_scenarios"].append(record)

        st.success(f"Scenario saved for {d}")

hist_df = pd.DataFrame(st.session_state["saved_scenarios"])
if not hist_df.empty:
    if "cm1_pct" not in hist_df.columns:
        hist_df["cm1_pct"] = None
    if "cm2_pct" not in hist_df.columns:
        hist_df["cm2_pct"] = None
    if "break_even_contribution_eur" not in hist_df.columns:
        hist_df["break_even_contribution_eur"] = None
    if "loan_book_k" not in hist_df.columns:
        hist_df["loan_book_k"] = None

    hist_df = hist_df.sort_values("date").drop_duplicates(subset=["date"], keep="last")

    hist_long = hist_df.melt(
        id_vars=["date", "name"],
        value_vars=["cm1_pct", "cm2_pct"],
        var_name="metric",
        value_name="value",
    )

    line = (
        alt.Chart(hist_long.dropna())
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="% TPV"),
            color=alt.Color("metric:N", title=None),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("name:N", title="Scenario"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=".2f"),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(line, use_container_width=True)

    st.dataframe(hist_df, use_container_width=True)

# ----------------------------------------------------------
# MANAGEMENT COMMENT
# ----------------------------------------------------------
st.markdown("## Ce que ce dashboard doit te faire voir")
comment_df = pd.DataFrame(
    [
        {
            "Question": "Le moteur transactionnel est-il bon ?",
            "Metric": "CM1",
            "Lecture": "Si CM1 monte, ton pricing / paiement / liquidité s’améliorent."
        },
        {
            "Question": "La croissance marginale crée-t-elle de la valeur ?",
            "Metric": "CM2",
            "Lecture": "Si CM2 reste faible malgré CM1 fort, tu as un problème de coût de service, risque ou machine humaine."
        },
        {
            "Question": "La structure actuelle est-elle absorbable ?",
            "Metric": "Break-even contribution",
            "Lecture": "Si la courbe passe au-dessus de zéro, ton modèle couvre enfin sa structure fixe."
        },
    ]
)
st.dataframe(comment_df, use_container_width=True)
