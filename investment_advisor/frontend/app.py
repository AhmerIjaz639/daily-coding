# frontend/app.py
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Investment Advisor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SESSION STATE INIT ──────────────────────────────────────────────────────

def init_session():
    defaults = {
        "user_id": None,
        "user_name": None,
        "token": None,
        "last_recommendation": None,
        "last_profile": None,
        "last_rec_id": None,
        "page": "Login"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def api_post(endpoint, data, use_token=False):
    headers = {"Content-Type": "application/json"}
    if use_token and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers, timeout=15)
        return response.json(), response.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def api_get(endpoint):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=15)
        return response.json(), response.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def make_pie_chart(allocation, title="Portfolio Allocation"):
    labels = list(allocation.keys())
    values = list(allocation.values())
    labels_display = [l.replace("_", " ").title() for l in labels]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#FFD700", "#9C27B0", "#607D8B"]

    fig = go.Figure(data=[go.Pie(
        labels=labels_display,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textfont=dict(size=13)
    )])
    fig.update_layout(
        title=dict(text=title, font=dict(size=18), x=0.5),
        showlegend=True,
        height=450,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    return fig

def make_bar_chart(allocation):
    labels = [k.replace("_", " ").title() for k in allocation.keys()]
    values = list(allocation.values())
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#FFD700", "#9C27B0", "#607D8B"]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside",
        textfont=dict(size=12)
    )])
    fig.update_layout(
        title=dict(text="Allocation Breakdown", font=dict(size=16), x=0.5),
        yaxis=dict(title="Percentage (%)", range=[0, max(values) + 10]),
        xaxis=dict(title="Asset Class"),
        height=380,
        margin=dict(t=50, b=40)
    )
    return fig

def cf_color(cf):
    if cf >= 0.85: return "🟢"
    elif cf >= 0.70: return "🟡"
    else: return "🔴"

def risk_color(label):
    colors = {
        "Aggressive": "#f44336",
        "Moderately Aggressive": "#FF9800",
        "Moderate": "#2196F3",
        "Moderately Conservative": "#4CAF50",
        "Conservative": "#607D8B"
    }
    return colors.get(label, "#2196F3")

# ─── SIDEBAR ────────────────────────────────────────────────────────────────

def sidebar():
    st.sidebar.markdown("##  Investment Advisor")
    st.sidebar.markdown("---")

    if st.session_state.user_id:
        st.sidebar.success(f" {st.session_state.user_name}")
        st.sidebar.markdown("---")

        pages = {
            " Risk Profile": "Risk Profile",
            " Portfolio Dashboard": "Portfolio Dashboard",
            " Explanation Viewer": "Explanation Viewer",
            "Scenario Tester": "Scenario Tester",
            " History": "History"
        }
        for label, page in pages.items():
            if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        st.sidebar.markdown("---")
        if st.sidebar.button(" Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session()
            st.rerun()
    else:
        st.session_state.page = "Login"

sidebar()

# ─── PAGE: LOGIN / REGISTER ──────────────────────────────────────────────────

def page_login():
    st.markdown("""
        <div style='text-align:center; padding: 20px 0'>
            <h1 style='color:#2196F3; font-size:2.5em'> Investment Recommendation Advisor</h1>
            <p style='font-size:1.1em; color:#555'>Rule-based Expert System for Personalized Portfolio Advice</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs([" Login", " Register"])

        with tab1:
            st.markdown("### Login to your account")
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        result, code = api_post("/login", {"email": email, "password": password})
                        if code == 200:
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_name = result["name"]
                            st.session_state.token = result["access_token"]
                            st.session_state.page = "Risk Profile"
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result.get("detail", "Login failed"))

        with tab2:
            st.markdown("### Create a new account")
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pass")
                password2 = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register", use_container_width=True, type="primary")
                if submitted:
                    if not name or not email or not password:
                        st.error("Please fill in all fields")
                    elif password != password2:
                        st.error("Passwords do not match")
                    else:
                        result, code = api_post("/register", {"name": name, "email": email, "password": password})
                        if code == 200:
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_name = result["name"]
                            st.session_state.token = result["access_token"]
                            st.session_state.page = "Risk Profile"
                            st.success("Account created! Welcome aboard!")
                            st.rerun()
                        else:
                            st.error(result.get("detail", "Registration failed"))

# ─── PAGE: RISK PROFILE FORM ─────────────────────────────────────────────────

def page_risk_profile():
    st.markdown("##  Risk Profile & Investment Assessment")
    st.info("Fill in your financial details. The expert system will apply 60+ rules to generate your personalized portfolio.")
    st.markdown("---")

    with st.form("profile_form"):
        st.markdown("###  Personal Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        with col2:
            dependents = st.number_input("Number of Dependents", min_value=0, max_value=20, value=0, step=1)
        with col3:
            employment_status = st.selectbox(
                "Employment Status",
                ["employed", "self_employed", "freelancer", "government", "stable", "unemployed", "retired"]
            )

        st.markdown("###  Financial Information")
        col1, col2 = st.columns(2)
        with col1:
            income = st.number_input("Annual Income (PKR)", min_value=0.0, value=60000.0, step=1000.0,
                                     help="Your total annual income")
            savings = st.number_input("Total Savings (PKR)", min_value=0.0, value=25000.0, step=1000.0,
                                      help="Total savings and liquid assets")
        with col2:
            debts = st.number_input("Total Debts (PKR)", min_value=0.0, value=10000.0, step=1000.0,
                                    help="Total outstanding debts (loans, credit cards, etc.)")
            monthly_expenses = st.number_input("Monthly Expenses (PKR)", min_value=0.0, value=3000.0, step=100.0,
                                               help="Average monthly living expenses")

        st.markdown("###  Investment Preferences")
        col1, col2 = st.columns(2)
        with col1:
            investment_horizon = st.slider("Investment Horizon (Years)", min_value=1, max_value=40, value=10)
            risk_tolerance = st.selectbox(
                "Risk Tolerance",
                ["very_low", "low", "moderate", "high", "very_high"],
                index=2,
                format_func=lambda x: {
                    "very_low": "Very Low — Capital Safety Only",
                    "low": "Low — Prefer Stability",
                    "moderate": "Moderate — Balanced Approach",
                    "high": "High — Growth Focused",
                    "very_high": "Very High — Maximum Growth"
                }.get(x, x)
            )
        with col2:
            existing_investments = st.selectbox(
                "Existing Investments",
                ["none", "stocks", "bonds", "mutual_funds", "mixed", "real_estate"],
                format_func=lambda x: x.replace("_", " ").title()
            )
            goals = st.multiselect(
                "Investment Goals",
                ["retirement", "home purchase", "education", "wealth growth", "income generation", "capital preservation"],
                default=["retirement"]
            )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            assess_btn = st.form_submit_button("Assess Risk Only", use_container_width=True)
        with col2:
            recommend_btn = st.form_submit_button(" Get Full Recommendation", use_container_width=True, type="primary")

    goals_str = ", ".join(goals) if goals else "wealth growth"

    profile_data = {
        "user_id": st.session_state.user_id,
        "age": age,
        "income": income,
        "savings": savings,
        "debts": debts,
        "goals": goals_str,
        "investment_horizon": investment_horizon,
        "risk_tolerance": risk_tolerance,
        "monthly_expenses": monthly_expenses,
        "dependents": dependents,
        "employment_status": employment_status,
        "existing_investments": existing_investments
    }

    if assess_btn:
        with st.spinner("Assessing risk profile..."):
            result, code = api_post("/assess-risk", profile_data)
        if code == 200:
            st.markdown("---")
            st.markdown("### Risk Assessment Result")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{result['risk_score']} / 100")
            with col2:
                st.metric("Risk Label", result["risk_label"])
            with col3:
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result["risk_score"],
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": risk_color(result["risk_label"])},
                        "steps": [
                            {"range": [0, 35], "color": "#E8F5E9"},
                            {"range": [35, 65], "color": "#E3F2FD"},
                            {"range": [65, 100], "color": "#FFEBEE"}
                        ]
                    }
                ))
                gauge.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(gauge, use_container_width=True)
            st.info(result["message"])
        else:
            st.error(result.get("detail", "Risk assessment failed"))

    if recommend_btn:
        with st.spinner("Running inference engine — applying 60+ rules..."):
            result, code = api_post("/recommend", profile_data)

        if code == 200:
            st.session_state.last_recommendation = result["allocation"]
            st.session_state.last_profile = profile_data
            st.session_state.last_rec_id = result["recommendation_id"]

            st.success(f"{result['message']}")
            st.markdown("---")
            st.markdown("###  Your Portfolio Recommendation")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Risk Profile", result["risk_label"])
            with col2:
                st.metric("Risk Score", f"{result['risk_score']}/100")
            with col3:
                st.metric("Confidence", f"{result['certainty_factor']:.1%}")
            with col4:
                st.metric("Rules Applied", result["rules_fired_count"])

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(make_pie_chart(result["allocation"]), use_container_width=True)
            with col2:
                st.plotly_chart(make_bar_chart(result["allocation"]), use_container_width=True)

            st.markdown("###  Asset Allocation Details")
            asset_cols = st.columns(6)
            asset_icons = {
                "stocks": "", "bonds": "", "mutual_funds": "",
                "gold": "", "real_estate": "", "cash": ""
            }
            for i, (asset, pct) in enumerate(result["allocation"].items()):
                with asset_cols[i]:
                    icon = asset_icons.get(asset, "")
                    st.metric(
                        f"{icon} {asset.replace('_', ' ').title()}",
                        f"{pct}%"
                    )

            st.info(" Navigate to **Portfolio Dashboard** or **Explanation Viewer** from the sidebar for more details.")
        else:
            st.error(result.get("detail", "Recommendation failed"))

# ─── PAGE: PORTFOLIO DASHBOARD ───────────────────────────────────────────────

def page_portfolio_dashboard():
    st.markdown("##  Portfolio Dashboard")

    if not st.session_state.last_recommendation:
        st.warning("No recommendation yet. Please complete the Risk Profile form first.")
        if st.button("Go to Risk Profile"):
            st.session_state.page = "Risk Profile"
            st.rerun()
        return

    allocation = st.session_state.last_recommendation
    profile = st.session_state.last_profile

    # Header metrics
    st.markdown("### Current Recommendation Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Investment Horizon:** {profile.get('investment_horizon', 'N/A')} years")
    with col2:
        st.info(f"**Risk Tolerance:** {profile.get('risk_tolerance', 'N/A').replace('_', ' ').title()}")
    with col3:
        st.info(f"**Goals:** {profile.get('goals', 'N/A').title()}")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(make_pie_chart(allocation, "Portfolio Allocation"), use_container_width=True)
    with col2:
        st.plotly_chart(make_bar_chart(allocation), use_container_width=True)

    # Allocation table
    st.markdown("###  Detailed Allocation Table")
    table_data = []
    asset_descriptions = {
        "stocks": "High growth potential, higher volatility. Best for long horizons.",
        "bonds": "Stable income, lower risk. Government & corporate bonds.",
        "mutual_funds": "Diversified basket of assets. Professional management.",
        "gold": "Inflation hedge. Safe haven in market uncertainty.",
        "real_estate": "Tangible asset. Long-term appreciation and rental income.",
        "cash": "Maximum liquidity. Emergency fund and opportunity buffer."
    }
    risk_levels = {
        "stocks": "High", "bonds": "Low", "mutual_funds": "Medium",
        "gold": "Medium", "real_estate": "Medium-High", "cash": "Very Low"
    }
    for asset, pct in allocation.items():
        table_data.append({
            "Asset Class": asset.replace("_", " ").title(),
            "Allocation (%)": f"{pct}%",
            "Risk Level": risk_levels.get(asset, "Medium"),
            "Description": asset_descriptions.get(asset, "")
        })

    for row in table_data:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 4])
        with col1:
            st.write(f"**{row['Asset Class']}**")
        with col2:
            st.write(row["Allocation (%)"])
        with col3:
            st.write(row["Risk Level"])
        with col4:
            st.write(row["Description"])
        st.divider()

    # Investment amount calculator
    st.markdown("###  Investment Amount Calculator")
    investment_amount = st.number_input(
        "How much do you plan to invest? ($)",
        min_value=100.0,
        value=10000.0,
        step=500.0
    )

    if investment_amount > 0:
        st.markdown("**Dollar amounts based on your allocation:**")
        calc_cols = st.columns(6)
        for i, (asset, pct) in enumerate(allocation.items()):
            amount = (pct / 100) * investment_amount
            with calc_cols[i]:
                st.metric(
                    asset.replace("_", " ").title(),
                    f"${amount:,.0f}"
                )

# ─── PAGE: EXPLANATION VIEWER ────────────────────────────────────────────────

def page_explanation_viewer():
    st.markdown("##  Explanation Viewer — Rule Trace")
    st.info("Every recommendation is fully explainable. See exactly which rules fired and why.")

    if not st.session_state.last_rec_id:
        st.warning("No recommendation found. Please complete the Risk Profile form first.")
        return

    rec_id = st.session_state.last_rec_id

    with st.spinner("Loading rule trace..."):
        result, code = api_get(f"/explain/{rec_id}")

    if code != 200:
        st.error(f"Could not load explanation: {result.get('detail', 'Error')}")
        return

    rules = result["rules"]
    total = result["total_rules_fired"]
    overall_cf = result["overall_cf"]

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rules Fired", total)
    with col2:
        st.metric("Overall Confidence", f"{overall_cf:.1%}")
    with col3:
        st.metric("Recommendation ID", f"#{rec_id}")

    st.markdown("---")

    # Category filter
    categories = list(set(r["category"] for r in rules))
    categories = ["All"] + sorted(categories)
    selected_category = st.selectbox("Filter by Category", categories)

    # Search
    search = st.text_input(" Search rules...", placeholder="Type rule name or keyword...")

    filtered_rules = rules
    if selected_category != "All":
        filtered_rules = [r for r in rules if r["category"] == selected_category]
    if search:
        filtered_rules = [r for r in filtered_rules
                          if search.lower() in r["rule_name"].lower()
                          or search.lower() in r["explanation"].lower()]

    st.markdown(f"###  Fired Rules ({len(filtered_rules)} shown)")

    # Category breakdown chart
    cat_counts = {}
    for rule in rules:
        cat_counts[rule["category"]] = cat_counts.get(rule["category"], 0) + 1

    fig = px.bar(
        x=list(cat_counts.keys()),
        y=list(cat_counts.values()),
        title="Rules Fired by Category",
        labels={"x": "Category", "y": "Rules Fired"},
        color=list(cat_counts.values()),
        color_continuous_scale="Blues"
    )
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Rules list
    for rule in filtered_rules:
        cf = rule["certainty_factor"]
        icon = cf_color(cf)
        with st.expander(f"{icon} [{rule['rule_id']}] {rule['rule_name']} | CF: {cf:.0%} | {rule['category']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Category:** {rule['category']}")
                st.markdown(f"**Priority:** {rule['priority']}")
                st.markdown(f"**Certainty Factor:** {cf:.1%}")
            with col2:
                st.markdown(f"**Action Taken:** `{rule['action_taken']}`")
                progress_val = cf
                st.progress(progress_val, text=f"Confidence: {cf:.0%}")
            st.markdown(f"** Explanation:** {rule['explanation']}")

# ─── PAGE: SCENARIO TESTER ───────────────────────────────────────────────────

def page_scenario_tester():
    st.markdown("##  Scenario Tester")
    st.info("Change a single input and see how your portfolio recommendation changes in real time.")

    if not st.session_state.last_profile:
        st.warning("Please complete the Risk Profile form first to use Scenario Tester.")
        return

    base_profile = dict(st.session_state.last_profile)
    base_allocation = dict(st.session_state.last_recommendation) if st.session_state.last_recommendation else {}

    st.markdown("###  Adjust Scenario Parameters")

    col1, col2 = st.columns(2)
    with col1:
        scenario_name = st.text_input("Scenario Name", value="My Scenario")
        new_age = st.slider("Age", 18, 80, int(base_profile.get("age", 30)),
                            help="Change age to see impact")
        new_horizon = st.slider("Investment Horizon (Years)", 1, 40, int(base_profile.get("investment_horizon", 10)),
                                help="Extend or shorten your investment timeline")
        new_income = st.number_input("Annual Income ($)", value=float(base_profile.get("income", 60000)),
                                     min_value=0.0, step=5000.0)
    with col2:
        new_risk = st.selectbox(
            "Risk Tolerance",
            ["very_low", "low", "moderate", "high", "very_high"],
            index=["very_low", "low", "moderate", "high", "very_high"].index(
                base_profile.get("risk_tolerance", "moderate")
            ),
            format_func=lambda x: x.replace("_", " ").title()
        )
        new_savings = st.number_input("Total Savings ($)", value=float(base_profile.get("savings", 25000)),
                                      min_value=0.0, step=5000.0)
        new_debts = st.number_input("Total Debts ($)", value=float(base_profile.get("debts", 10000)),
                                    min_value=0.0, step=1000.0)
        new_dependents = st.number_input("Dependents", value=int(base_profile.get("dependents", 0)),
                                         min_value=0, max_value=20, step=1)

    scenario_profile = {
        **base_profile,
        "age": new_age,
        "investment_horizon": new_horizon,
        "income": new_income,
        "risk_tolerance": new_risk,
        "savings": new_savings,
        "debts": new_debts,
        "dependents": new_dependents
    }

    col1, col2 = st.columns(2)
    with col1:
        run_btn = st.button(" Run Scenario", use_container_width=True, type="primary")
    with col2:
        save_btn = st.button("Save Scenario", use_container_width=True)

    if run_btn:
        with st.spinner("Running scenario through inference engine..."):
            result, code = api_post("/recommend", scenario_profile)

        if code == 200:
            new_allocation = result["allocation"]
            st.markdown("---")
            st.markdown("###  Scenario Comparison")

            # Side by side
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🔵 Original Portfolio")
                if base_allocation:
                    st.plotly_chart(make_pie_chart(base_allocation, "Original"), use_container_width=True)
            with col2:
                st.markdown("#### 🟢 Scenario Portfolio")
                st.plotly_chart(make_pie_chart(new_allocation, "Scenario"), use_container_width=True)

            # Changes
            st.markdown("### Changes in Allocation")
            if base_allocation:
                change_cols = st.columns(6)
                for i, (asset, new_pct) in enumerate(new_allocation.items()):
                    old_pct = base_allocation.get(asset, 0)
                    delta = round(new_pct - old_pct, 2)
                    with change_cols[i]:
                        st.metric(
                            asset.replace("_", " ").title(),
                            f"{new_pct}%",
                            delta=f"{delta:+.1f}%"
                        )

            # Summary metrics
            st.markdown("###  Scenario Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Risk Label", result["risk_label"])
            with col2:
                st.metric("Risk Score", f"{result['risk_score']}/100")
            with col3:
                st.metric("Confidence", f"{result['certainty_factor']:.1%}")
            with col4:
                st.metric("Rules Fired", result["rules_fired_count"])

            # Store for saving
            st.session_state["current_scenario_profile"] = scenario_profile
            st.session_state["current_scenario_result"] = result
            st.session_state["current_scenario_name"] = scenario_name
        else:
            st.error(result.get("detail", "Scenario failed"))

    if save_btn:
        if "current_scenario_result" not in st.session_state:
            st.warning("Please run the scenario first before saving.")
        else:
            save_data = {
                "user_id": st.session_state.user_id,
                "scenario_name": st.session_state.get("current_scenario_name", "Scenario"),
                "profile_snapshot": st.session_state["current_scenario_profile"],
                "recommendation_snapshot": {
                    "allocation": st.session_state["current_scenario_result"]["allocation"],
                    "risk_label": st.session_state["current_scenario_result"]["risk_label"],
                    "risk_score": st.session_state["current_scenario_result"]["risk_score"],
                    "certainty_factor": st.session_state["current_scenario_result"]["certainty_factor"]
                }
            }
            save_result, code = api_post("/scenario", save_data)
            if code == 200:
                st.success(f" Scenario saved! ID: {save_result['scenario_id']}")
            else:
                st.error("Failed to save scenario")

    # Saved scenarios
    st.markdown("---")
    st.markdown("### 📂 Saved Scenarios")
    with st.spinner("Loading saved scenarios..."):
        scenarios_result, code = api_get(f"/scenarios/{st.session_state.user_id}")

    if code == 200 and scenarios_result["scenarios"]:
        for scenario in scenarios_result["scenarios"]:
            with st.expander(f"📁 {scenario['scenario_name']} — {scenario['created_at'][:16]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Profile Snapshot:**")
                    snap = scenario["profile_snapshot"]
                    st.write(f"Age: {snap.get('age')}, Horizon: {snap.get('investment_horizon')}y, Risk: {snap.get('risk_tolerance')}")
                    st.write(f"Income: ${snap.get('income', 0):,.0f}, Savings: ${snap.get('savings', 0):,.0f}")
                with col2:
                    st.markdown("**Recommendation Snapshot:**")
                    rec_snap = scenario["recommendation_snapshot"]
                    st.write(f"Risk Label: {rec_snap.get('risk_label')}")
                    alloc = rec_snap.get("allocation", {})
                    if alloc:
                        st.plotly_chart(make_pie_chart(alloc, ""), use_container_width=True)
    else:
        st.info("No saved scenarios yet. Run and save a scenario above.")

# ─── PAGE: HISTORY ───────────────────────────────────────────────────────────

def page_history():
    st.markdown("##  Recommendation History")

    with st.spinner("Loading your history..."):
        result, code = api_get(f"/history/{st.session_state.user_id}")

    if code != 200:
        st.error("Could not load history")
        return

    history = result["history"]
    total = result["total"]

    if not history:
        st.info("No recommendation history yet. Complete the Risk Profile form to get started!")
        return

    st.success(f"Found {total} recommendations in your history")

    for rec in history:
        with st.expander(
            f"{rec['created_at'][:16]} | Risk: {rec['risk_label']} | "
            f"Confidence: {rec['certainty_factor']:.1%} | ID: #{rec['recommendation_id']}"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Profile Used:**")
                st.write(f"Age: {rec['profile']['age']}")
                st.write(f"Horizon: {rec['profile']['investment_horizon']} years")
                st.write(f"Risk: {rec['profile']['risk_tolerance'].replace('_', ' ').title()}")
                st.write(f"Goals: {rec['profile']['goals']}")
            with col2:
                st.markdown("**Results:**")
                st.metric("Risk Score", f"{rec['risk_score']}/100")
                st.metric("Confidence", f"{rec['certainty_factor']:.1%}")
            with col3:
                st.plotly_chart(
                    make_pie_chart(rec["allocation"], ""),
                    use_container_width=True
                )

            if st.button(f"Load Explanation #{rec['recommendation_id']}", key=f"load_{rec['recommendation_id']}"):
                st.session_state.last_rec_id = rec["recommendation_id"]
                st.session_state.page = "Explanation Viewer"
                st.rerun()

# ─── ROUTER ──────────────────────────────────────────────────────────────────

def main():
    if not st.session_state.user_id:
        page_login()
        return

    page = st.session_state.page
    if page == "Risk Profile":
        page_risk_profile()
    elif page == "Portfolio Dashboard":
        page_portfolio_dashboard()
    elif page == "Explanation Viewer":
        page_explanation_viewer()
    elif page == "Scenario Tester":
        page_scenario_tester()
    elif page == "History":
        page_history()
    else:
        page_risk_profile()

main()