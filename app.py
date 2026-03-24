import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Waribei – Unit Economics", layout="wide")
DUREE_PERIODE_LIQUIDITE_JOURS = 10

# --------------------------------------------------
# PRESETS (historique + défaut)
# --------------------------------------------------
PRESETS_BY_DATE = {
    date(2025, 6, 1): {
        "name": "Historique – Jun 2025",
        "revenu_pct": 3.73,
        "cout_paiement_pct": 1.75,
        "cout_liquidite_10j_pct": 0.21,
        "defaut_30j_pct": 1.43,
        "loan_book_k": 140.0,
        "cycles_per_month": 2.9,
        "fixed_opex_monthly": 14000.0,
    },
    date(2025, 12, 1): {
        "name": "Historique – Dec 2025",
        "revenu_pct": 3.76,
        "cout_paiement_pct": 1.80,
        "cout_liquidite_10j_pct": 0.36,
        "defaut_30j_pct": 1.00,
        "loan_book_k": 155.0,
        "cycles_per_month": 2.9,
        "fixed_opex_monthly": 14000.0,
    },
    date(2026, 6, 1): {
        "name": "Default – Jun 2026",
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.20,
        "cout_liquidite_10j_pct": 0.40,
        "defaut_30j_pct": 1.00,
        "loan_book_k": 320.0,
        "cycles_per_month": 2.9,
        "fixed_opex_monthly": 14000.0,
    },
}
DEFAULT_DATE = date(2026, 6, 1)
HISTORY_DATES = [date(2025, 6, 1), date(2025, 12, 1), date(2026, 6, 1)]

# --------------------------------------------------
# SCÉNARIOS RAPIDES
# --------------------------------------------------
SCENARIOS_PRESETS = {
    "Custom": None,
    "Base scénario — Aujourd’hui": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.60,
        "cout_liquidite_10j_pct": 0.40,
        "defaut_30j_pct": 1.00,
        "loan_book_k": 225.0,
        "cycles_per_month": 2.9,
        "fixed_opex_monthly": 14000.0,
        "scenario_name_autofill": "Base scénario — Aujourd’hui",
    },
    "Scénario 1 — Optimisation légère": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.20,
        "cout_liquidite_10j_pct": 0.40,
        "defaut_30j_pct": 1.00,
        "loan_book_k": 320.0,
        "cycles_per_month": 2.9,
        "fixed_opex_monthly": 14000.0,
        "scenario_name_autofill": "Scénario 1 — Optimisation légère",
    },
    "Scénario 2 — Open Banking": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 0.50,
        "cout_liquidite_10j_pct": 0.40,
        "defaut_30j_pct": 0.62,
        "loan_book_k": 280.0,
        "cycles_per_month": 3.0,
        "fixed_opex_monthly": 14000.0,
        "scenario_name_autofill": "Scénario 2 — Open Banking",
    },
    "Scénario 3 — Scale disciplinée": {
        "revenu_pct": 3.80,
        "cout_paiement_pct": 1.00,
        "cout_liquidite_10j_pct": 0.40,
        "defaut_30j_pct": 0.80,
        "loan_book_k": 500.0,
        "cycles_per_month": 3.0,
        "fixed_opex_monthly": 14000.0,
        "scenario_name_autofill": "Scénario 3 — Scale disciplinée",
    },
}

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
def init_state():
    if "scenario_date" not in st.session_state:
        st.session_state["scenario_date"] = DEFAULT_DATE

    if "scenarios" not in st.session_state:
        st.session_state["scenarios"] = [
            {
                "date": date(2025, 6, 1),
                "name": "Historique – Jun 2025",
                "cm1_pct": 3.73 - 1.75 - 0.21,
                "cm2_pct": 3.73 - 1.75 - 0.21 - 1.43,
                "contribution_margin_pct": 3.73 - 1.75 - 0.21 - 1.43,
                "break_even_gap_eur": None,
            },
            {
                "date": date(2025, 12, 1),
                "name": "Historique – Dec 2025",
                "cm1_pct": 3.76 - 1.80 - 0.36,
                "cm2_pct": 3.76 - 1.80 - 0.36 - 1.00,
                "contribution_margin_pct": 3.76 - 1.80 - 0.36 - 1.00,
                "break_even_gap_eur": None,
            },
            {
                "date": date(2026, 6, 1),
                "name": "Default – Jun 2026",
                "cm1_pct": 3.80 - 1.20 - 0.40,
                "cm2_pct": 3.80 - 1.20 - 0.40 - 1.00,
                "contribution_margin_pct": 3.80 - 1.20 - 0.40 - 1.00,
                "break_even_gap_eur": None,
            },
        ]

    if "pending_scenario" not in st.session_state:
        st.session_state["pending_scenario"] = None

init_state()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def euro(x):
    return f"{x:,.0f} €".replace(",", " ")

def pct(x):
    return f"{x:.2f}%"

def safe_div(a, b):
    return a / b if b not in [0, None] else 0.0

def apply_preset_for_date(d, force=True):
    preset = PRESETS_BY_DATE.get(d)
    if not preset:
        return

    for key, val in preset.items():
        state_key = key
        if force or state_key not in st.session_state:
            st.session_state[state_key] = val

def apply_scenario_preset(name):
    preset = SCENARIOS_PRESETS.get(name)
    if not preset:
        return
    for key, val in preset.items():
        st.session_state[key] = val

def vbar_widget(label, key, min_value, max_value, step, help_text="", kind="neutral"):
    value = float(st.session_state.get(key, min_value))
    st.metric(label, pct(value))
    st.slider(
        label="",
        min_value=float(min_value),
        max_value=float(max_value),
        value=float(value),
        step=float(step),
        key=key,
        help=help_text,
    )

def knob_simple_visual(label, value, min_value, max_value):
    st.markdown(f"**{label}**")
    st.metric("", f"{value:.1f}")

def make_waterfall_df_cm2(revenue, pay_cost, liq_cost, default_cost, margin):
    steps = ["Revenu", "Coût paiement", "Coût liquidité (10j)", "Défaut 30j", "CM2"]
    values = [revenue, -pay_cost, -liq_cost, -default_cost, margin]

    start, end = [], []
    running = 0.0
    for v in values[:-1]:
        start.append(running)
        running += v
        end.append(running)

    start.append(0.0)
    end.append(margin)

    types = []
    for i, v in enumerate(values):
        if i == len(values) - 1:
            types.append("total")
        elif v >= 0:
            types.append("positive")
        else:
            types.append("negative")

    return pd.DataFrame({"step": steps, "value": values, "start": start, "end": end, "type": types})

def make_waterfall_df_full(revenue, pay_cost, liq_cost, default_cost, cm1, fixed_opex_pct, break_even_pct):
    steps = [
        "Revenu",
        "Coût paiement",
        "Coût liquidité (10j)",
        "CM1",
        "Défaut 30j",
        "CM2",
        "OPEX fixes",
        "Break-even",
    ]
    values = [
        revenue,
        -pay_cost,
        -liq_cost,
        cm1,
        -default_cost,
        cm1 - default_cost,
        -fixed_opex_pct,
        break_even_pct,
    ]

    start, end = [], []
    running = 0.0
    total_steps = {"CM1", "CM2", "Break-even"}

    for step, val in zip(steps, values):
        if step in total_steps:
            start.append(0.0)
            end.append(val)
        else:
            start.append(running)
            running += val
            end.append(running)

    types = []
    for step, val in zip(steps, values):
        if step in total_steps:
            types.append("total")
        elif val >= 0:
            types.append("positive")
        else:
            types.append("negative")

    return pd.DataFrame({"step": steps, "value": values, "start": start, "end": end, "type": types})

# --------------------------------------------------
# STYLES
# --------------------------------------------------
st.markdown(
    """
    <style>
    .wb-card {
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 18px 18px 10px 18px;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------
page = st.sidebar.radio("Navigation", ["Simulateur", "Comment je modélise une courbe ?"])

# ==================================================
# PAGE 2
# ==================================================
if page == "Comment je modélise une courbe ?":
    st.title("Comment fonctionne le simulateur Waribei ?")
    st.markdown(
        """
- Historique : **Jun 2025**, **Dec 2025**, **Jun 2026**
- **CM1** = revenu - coût paiement - coût liquidité
- **CM2** = CM1 - défaut 30j
- **Break-even** = contribution mensuelle - OPEX fixes
- Courbe historique : **CM1** et **CM2**
"""
    )

# ==================================================
# PAGE 1
# ==================================================
else:
    top = st.columns([0.7, 0.3])
    with top[0]:
        st.title("Unit Economics – Waribei")
    with top[1]:
        try:
            st.image("logo_waribei_icon@2x.png", width=100)
        except Exception:
            st.write("Logo Waribei")

    st.markdown("---")

    # --------------------------------------------------
    # APPLY PENDING SCENARIO
    # --------------------------------------------------
    if "pending_scenario" in st.session_state and st.session_state.pending_scenario:
        apply_scenario_preset(st.session_state.pending_scenario)
        st.session_state.pending_scenario = None

    # --------------------------------------------------
    # SIDEBAR CONTROLS
    # --------------------------------------------------
    with st.sidebar:
        st.markdown("### Presets rapides")
        selected_preset = st.selectbox("Scénario rapide", list(SCENARIOS_PRESETS.keys()))
        if selected_preset != "Custom":
            if st.button("Appliquer le preset"):
                apply_scenario_preset(selected_preset)

        st.markdown("---")
        dcols = st.columns([0.72, 0.28])
        with dcols[1]:
            if st.button("Today"):
                st.session_state["scenario_date"] = DEFAULT_DATE
                apply_preset_for_date(DEFAULT_DATE, force=True)
        with dcols[0]:
            picked = st.date_input("Date", value=st.session_state.get("scenario_date", DEFAULT_DATE))
            st.session_state["scenario_date"] = picked
        apply_preset_for_date(st.session_state["scenario_date"], force=False)

        default_label = st.session_state.get("scenario_name_autofill", "Scenario")
        scenario_name = st.text_input("Label du scénario", value=default_label)

    # --------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------
    main_left, main_right = st.columns([0.68, 0.32], gap="large")

    # =========================
    # LEFT
    # =========================
    with main_left:
        # ---- Hypothèses par transaction
        st.markdown('<div class="wb-card">', unsafe_allow_html=True)
        st.subheader("Hypothèses par transaction")

        c1, c2, c3, c4 = st.columns(4, gap="large")
        with c1:
            vbar_widget("Revenus / trx", "revenu_pct", 1.0, 5.0, 0.01, "Take-rate / commission moyenne.")
        with c2:
            vbar_widget("Coût paiement / trx", "cout_paiement_pct", 0.0, 2.5, 0.01, "Coût des rails de paiement.")
        with c3:
            vbar_widget("Coût liquidité (10j)", "cout_liquidite_10j_pct", 0.0, 1.5, 0.01, "Coût de financement sur 10 jours.")
        with c4:
            vbar_widget("Défaut 30j / trx", "defaut_30j_pct", 0.0, 5.0, 0.01, "Perte attendue nette à 30 jours.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        # ---- Variables de volume
        st.markdown('<div class="wb-card">', unsafe_allow_html=True)
        st.subheader("Variables de volume")

        vcol1, vcol2 = st.columns([0.5, 0.5], gap="large")
        with vcol1:
            knob_simple_visual("Loan book moyen (k€)", float(st.session_state.get("loan_book_k", 320.0)), 50.0, 1000.0)
            st.slider(
                label="",
                min_value=50.0,
                max_value=1000.0,
                value=float(st.session_state.get("loan_book_k", 320.0)),
                step=5.0,
                key="loan_book_k",
            )

        with vcol2:
            knob_simple_visual("Cycles / mois", float(st.session_state.get("cycles_per_month", 2.9)), 1.0, 5.0)
            st.slider(
                label="",
                min_value=1.0,
                max_value=5.0,
                value=float(st.session_state.get("cycles_per_month", 2.9)),
                step=0.1,
                key="cycles_per_month",
            )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        # ---- OPEX fixe
        st.markdown('<div class="wb-card">', unsafe_allow_html=True)
        st.subheader("Structure fixe")

        op1, op2 = st.columns([0.45, 0.55], gap="large")
        with op1:
            st.metric("OPEX fixes mensuels", euro(float(st.session_state.get("fixed_opex_monthly", 14000.0))))
        with op2:
            st.slider(
                "OPEX fixes mensuels (€)",
                min_value=0.0,
                max_value=40000.0,
                value=float(st.session_state.get("fixed_opex_monthly", 14000.0)),
                step=500.0,
                key="fixed_opex_monthly",
                help="Coûts fixes à couvrir pour atteindre le break-even.",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # RIGHT
    # =========================
    with main_right:
        revenu_pct = float(st.session_state["revenu_pct"])
        cout_paiement_pct = float(st.session_state["cout_paiement_pct"])
        cout_liquidite_10j_pct = float(st.session_state["cout_liquidite_10j_pct"])
        defaut_30j_pct = float(st.session_state["defaut_30j_pct"])
        loan_book_k = float(st.session_state["loan_book_k"])
        cycles_per_month = float(st.session_state["cycles_per_month"])
        fixed_opex_monthly = float(st.session_state["fixed_opex_monthly"])

        # Core calculations
        cm1_pct = revenu_pct - cout_paiement_pct - cout_liquidite_10j_pct
        cm2_pct = cm1_pct - defaut_30j_pct
        contribution_margin_pct = cm2_pct

        loan_book_eur = loan_book_k * 1000
        monthly_tpv_eur = loan_book_eur * cycles_per_month
        monthly_revenue_eur = monthly_tpv_eur * revenu_pct / 100
        monthly_cm1_eur = monthly_tpv_eur * cm1_pct / 100
        monthly_contribution_margin_eur = monthly_tpv_eur * contribution_margin_pct / 100
        break_even_gap_eur = monthly_contribution_margin_eur - fixed_opex_monthly
        fixed_opex_pct_of_tpv = safe_div(fixed_opex_monthly, monthly_tpv_eur) * 100
        break_even_pct = contribution_margin_pct - fixed_opex_pct_of_tpv

        # Revenue needed for break-even
        cm2_rate = contribution_margin_pct / 100
        mrr_needed_for_break_even = safe_div(fixed_opex_monthly, cm2_rate) if cm2_rate > 0 else None
        tpv_needed_for_break_even = mrr_needed_for_break_even / (revenu_pct / 100) if revenu_pct > 0 and mrr_needed_for_break_even is not None else None

        st.markdown('<div class="wb-card">', unsafe_allow_html=True)
        st.subheader("Lecture business")

        st.metric("CM1 (%)", pct(cm1_pct), help="Revenu - coût paiement - coût liquidité")
        st.metric("CM2 (%)", pct(cm2_pct), help="CM1 - défaut 30j")
        st.metric("Contribution mensuelle", euro(monthly_contribution_margin_eur))
        st.metric("Break-even gap", euro(break_even_gap_eur))

        if mrr_needed_for_break_even is not None:
            st.metric("MRR requis pour break-even", euro(mrr_needed_for_break_even))
        else:
            st.metric("MRR requis pour break-even", "N/A")

        if tpv_needed_for_break_even is not None:
            st.metric("TPV requis pour break-even", euro(tpv_needed_for_break_even))
        else:
            st.metric("TPV requis pour break-even", "N/A")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        st.markdown('<div class="wb-card">', unsafe_allow_html=True)
        st.subheader("Tableau synthétique")

        summary_df = pd.DataFrame(
            {
                "Métrique": [
                    "Revenue %",
                    "Coût paiement %",
                    "Coût liquidité %",
                    "Défaut 30j %",
                    "CM1 %",
                    "CM2 %",
                    "Loan book (€)",
                    "TPV mensuel (€)",
                    "Contribution mensuelle (€)",
                    "OPEX fixes mensuels (€)",
                    "Break-even gap (€)",
                ],
                "Valeur": [
                    pct(revenu_pct),
                    pct(cout_paiement_pct),
                    pct(cout_liquidite_10j_pct),
                    pct(defaut_30j_pct),
                    pct(cm1_pct),
                    pct(cm2_pct),
                    euro(loan_book_eur),
                    euro(monthly_tpv_eur),
                    euro(monthly_contribution_margin_eur),
                    euro(fixed_opex_monthly),
                    euro(break_even_gap_eur),
                ],
            }
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        if st.button("SAVE"):
            d = st.session_state["scenario_date"]
            record = {
                "date": d,
                "name": scenario_name,
                "cm1_pct": cm1_pct,
                "cm2_pct": cm2_pct,
                "contribution_margin_pct": contribution_margin_pct,
                "break_even_gap_eur": break_even_gap_eur,
            }

            replaced = False
            for i, s in enumerate(st.session_state.scenarios):
                if s.get("date") == d:
                    st.session_state.scenarios[i] = record
                    replaced = True
                    break
            if not replaced:
                st.session_state.scenarios.append(record)

            st.success(f"Scénario '{scenario_name}' sauvegardé ({d}).")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --------------------------------------------------
    # WATERFALL 1 : proche du dashboard existant
    # --------------------------------------------------
    st.markdown("### Décomposition par transaction (waterfall CM2)")
    wf_df = make_waterfall_df_cm2(
        revenu_pct,
        cout_paiement_pct,
        cout_liquidite_10j_pct,
        defaut_30j_pct,
        contribution_margin_pct,
    )

    color_scale = alt.Scale(domain=["positive", "negative", "total"], range=["#1B5A43", "#F83131", "#064C72"])
    waterfall_chart = (
        alt.Chart(wf_df)
        .mark_bar()
        .encode(
            x=alt.X("step:N", title=None, sort=list(wf_df["step"])),
            y=alt.Y("start:Q", axis=alt.Axis(title="%")),
            y2="end:Q",
            color=alt.Color("type:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("step:N", title="Step"),
                alt.Tooltip("value:Q", title="Valeur", format=".2f"),
            ],
        )
    )
    wf_labels = (
        alt.Chart(wf_df)
        .mark_text(dy=-6, color="#333", fontSize=11)
        .encode(
            x=alt.X("step:N", sort=list(wf_df["step"])),
            y="end:Q",
            text=alt.Text("value:Q", format=".2f"),
        )
    )
    st.altair_chart((waterfall_chart + wf_labels).properties(height=260), use_container_width=True)

    # --------------------------------------------------
    # WATERFALL 2 : version enrichie demandée au board
    # --------------------------------------------------
    st.markdown("### Décomposition complète (CM1, CM2, Break-even)")
    wf_full_df = make_waterfall_df_full(
        revenu_pct,
        cout_paiement_pct,
        cout_liquidite_10j_pct,
        defaut_30j_pct,
        cm1_pct,
        fixed_opex_pct_of_tpv,
        break_even_pct,
    )

    waterfall_full_chart = (
        alt.Chart(wf_full_df)
        .mark_bar()
        .encode(
            x=alt.X("step:N", title=None, sort=list(wf_full_df["step"])),
            y=alt.Y("start:Q", axis=alt.Axis(title="% du TPV")),
            y2="end:Q",
            color=alt.Color("type:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("step:N", title="Step"),
                alt.Tooltip("value:Q", title="Valeur", format=".2f"),
            ],
        )
    )
    waterfall_full_labels = (
        alt.Chart(wf_full_df)
        .mark_text(dy=-6, color="#333", fontSize=11)
        .encode(
            x=alt.X("step:N", sort=list(wf_full_df["step"])),
            y="end:Q",
            text=alt.Text("value:Q", format=".2f"),
        )
    )
    st.altair_chart((waterfall_full_chart + waterfall_full_labels).properties(height=300), use_container_width=True)

    # --------------------------------------------------
    # TIME SERIES
    # --------------------------------------------------
    st.markdown("### Évolution dans le temps")
    df_hist = pd.DataFrame(st.session_state.scenarios)
    df_hist = df_hist[df_hist["date"].isin(HISTORY_DATES)].sort_values("date")
    df_hist = df_hist.drop_duplicates(subset=["date"], keep="last")

    if not df_hist.empty:
        df_long = df_hist.melt(
            id_vars=["date", "name"],
            value_vars=["cm1_pct", "cm2_pct"],
            var_name="metric",
            value_name="value",
        )

        line_chart = (
            alt.Chart(df_long)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("value:Q", title="%"),
                color=alt.Color("metric:N", title=None),
                tooltip=[
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("name:N", title="Scénario"),
                    alt.Tooltip("metric:N", title="Metric"),
                    alt.Tooltip("value:Q", title="Valeur", format=".2f"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(line_chart, use_container_width=True)

    st.dataframe(df_hist, use_container_width=True)
