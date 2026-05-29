# backend/knowledge_base.py

"""
Knowledge Base — 60+ Investment Rules
Each rule has:
  - id: unique identifier
  - name: human readable name
  - category: grouping
  - priority: lower number = higher priority (fires first)
  - condition: callable that takes profile dict, returns bool
  - action: what this rule does to the allocation
  - explanation: plain English explanation
  - cf: certainty factor (0.0 to 1.0)
"""

RULES = [

    # ─── CATEGORY 1: EMERGENCY FUND RULES (Priority 1-5) ───────────────────

    {
        "id": "R001",
        "name": "No Emergency Fund — Max Cash",
        "category": "Emergency Fund",
        "priority": 1,
        "condition": lambda p: (p["savings"] < p["monthly_expenses"] * 3),
        "action": {"cash": +20, "stocks": -10, "mutual_funds": -10},
        "explanation": "Your savings are less than 3 months of expenses. Emergency fund is critical — increasing cash allocation.",
        "cf": 0.95
    },
    {
        "id": "R002",
        "name": "Adequate Emergency Fund",
        "category": "Emergency Fund",
        "priority": 2,
        "condition": lambda p: (p["savings"] >= p["monthly_expenses"] * 6),
        "action": {"cash": -5, "stocks": +5},
        "explanation": "You have 6+ months emergency fund. You can afford slightly less cash and more growth assets.",
        "cf": 0.85
    },
    {
        "id": "R003",
        "name": "Partial Emergency Fund",
        "category": "Emergency Fund",
        "priority": 3,
        "condition": lambda p: (p["monthly_expenses"] * 3 <= p["savings"] < p["monthly_expenses"] * 6),
        "action": {"cash": +5, "stocks": -5},
        "explanation": "You have 3–6 months emergency fund. Slightly higher cash recommended until fully funded.",
        "cf": 0.80
    },

    # ─── CATEGORY 2: AGE-BASED RULES (Priority 6-15) ────────────────────────

    {
        "id": "R004",
        "name": "Very Young Investor (Under 25)",
        "category": "Age",
        "priority": 6,
        "condition": lambda p: p["age"] < 25,
        "action": {"stocks": +20, "bonds": -10, "cash": -10},
        "explanation": "You are under 25. Time is your greatest asset — heavily favour growth stocks.",
        "cf": 0.90
    },
    {
        "id": "R005",
        "name": "Young Investor (25-35)",
        "category": "Age",
        "priority": 7,
        "condition": lambda p: 25 <= p["age"] < 35,
        "action": {"stocks": +15, "bonds": -5, "mutual_funds": -5, "cash": -5},
        "explanation": "Age 25–35: Strong growth phase. Stocks should dominate your portfolio.",
        "cf": 0.88
    },
    {
        "id": "R006",
        "name": "Mid-Career Investor (35-45)",
        "category": "Age",
        "priority": 8,
        "condition": lambda p: 35 <= p["age"] < 45,
        "action": {"stocks": +5, "mutual_funds": +5, "bonds": -5, "cash": -5},
        "explanation": "Age 35–45: Balance growth with some stability. Mix of stocks and mutual funds.",
        "cf": 0.85
    },
    {
        "id": "R007",
        "name": "Pre-Retirement Investor (45-55)",
        "category": "Age",
        "priority": 9,
        "condition": lambda p: 45 <= p["age"] < 55,
        "action": {"bonds": +10, "stocks": -5, "cash": +5, "mutual_funds": -10},
        "explanation": "Age 45–55: Start shifting toward capital preservation. Increase bonds.",
        "cf": 0.87
    },
    {
        "id": "R008",
        "name": "Near-Retirement Investor (55-65)",
        "category": "Age",
        "priority": 10,
        "condition": lambda p: 55 <= p["age"] < 65,
        "action": {"bonds": +15, "stocks": -10, "cash": +5, "gold": +5, "mutual_funds": -15},
        "explanation": "Age 55–65: Capital preservation is priority. High bonds, some gold as hedge.",
        "cf": 0.90
    },
    {
        "id": "R009",
        "name": "Retirement Age (65+)",
        "category": "Age",
        "priority": 11,
        "condition": lambda p: p["age"] >= 65,
        "action": {"bonds": +20, "cash": +10, "stocks": -15, "mutual_funds": -15},
        "explanation": "Age 65+: Focus on income and capital preservation. Bonds and cash dominate.",
        "cf": 0.92
    },

    # ─── CATEGORY 3: RISK TOLERANCE RULES (Priority 16-22) ──────────────────

    {
        "id": "R010",
        "name": "Very High Risk Tolerance",
        "category": "Risk Tolerance",
        "priority": 16,
        "condition": lambda p: p["risk_tolerance"] == "very_high",
        "action": {"stocks": +25, "bonds": -15, "cash": -10},
        "explanation": "Very high risk tolerance: Aggressive growth portfolio. Maximum stock exposure.",
        "cf": 0.93
    },
    {
        "id": "R011",
        "name": "High Risk Tolerance",
        "category": "Risk Tolerance",
        "priority": 17,
        "condition": lambda p: p["risk_tolerance"] == "high",
        "action": {"stocks": +15, "bonds": -10, "cash": -5},
        "explanation": "High risk tolerance: Growth-focused portfolio with significant stock allocation.",
        "cf": 0.90
    },
    {
        "id": "R012",
        "name": "Moderate Risk Tolerance",
        "category": "Risk Tolerance",
        "priority": 18,
        "condition": lambda p: p["risk_tolerance"] == "moderate",
        "action": {"mutual_funds": +10, "stocks": -5, "bonds": +5, "cash": -10},
        "explanation": "Moderate risk: Balanced approach using mutual funds to diversify risk.",
        "cf": 0.85
    },
    {
        "id": "R013",
        "name": "Low Risk Tolerance",
        "category": "Risk Tolerance",
        "priority": 19,
        "condition": lambda p: p["risk_tolerance"] == "low",
        "action": {"bonds": +15, "cash": +10, "stocks": -15, "mutual_funds": -10},
        "explanation": "Low risk tolerance: Conservative portfolio prioritising bonds and cash.",
        "cf": 0.90
    },
    {
        "id": "R014",
        "name": "Very Low Risk Tolerance",
        "category": "Risk Tolerance",
        "priority": 20,
        "condition": lambda p: p["risk_tolerance"] == "very_low",
        "action": {"bonds": +20, "cash": +15, "stocks": -20, "mutual_funds": -15},
        "explanation": "Very low risk tolerance: Capital preservation above all. Minimal equity exposure.",
        "cf": 0.92
    },

    # ─── CATEGORY 4: INVESTMENT HORIZON RULES (Priority 23-30) ─────────────

    {
        "id": "R015",
        "name": "Very Short Horizon (Under 2 Years)",
        "category": "Investment Horizon",
        "priority": 23,
        "condition": lambda p: p["investment_horizon"] < 2,
        "action": {"cash": +25, "bonds": +10, "stocks": -20, "mutual_funds": -15},
        "explanation": "Investment horizon under 2 years: Cannot risk capital. High cash and short-term bonds.",
        "cf": 0.95
    },
    {
        "id": "R016",
        "name": "Short Horizon (2-5 Years)",
        "category": "Investment Horizon",
        "priority": 24,
        "condition": lambda p: 2 <= p["investment_horizon"] < 5,
        "action": {"bonds": +10, "cash": +10, "stocks": -10, "mutual_funds": -10},
        "explanation": "2–5 year horizon: Moderate conservatism. Bonds and cash buffer against volatility.",
        "cf": 0.88
    },
    {
        "id": "R017",
        "name": "Medium Horizon (5-10 Years)",
        "category": "Investment Horizon",
        "priority": 25,
        "condition": lambda p: 5 <= p["investment_horizon"] < 10,
        "action": {"stocks": +5, "mutual_funds": +5, "cash": -5, "bonds": -5},
        "explanation": "5–10 year horizon: Balanced growth. Good time for stocks and mutual funds.",
        "cf": 0.85
    },
    {
        "id": "R018",
        "name": "Long Horizon (10-20 Years)",
        "category": "Investment Horizon",
        "priority": 26,
        "condition": lambda p: 10 <= p["investment_horizon"] < 20,
        "action": {"stocks": +10, "mutual_funds": +5, "bonds": -10, "cash": -5},
        "explanation": "10–20 year horizon: Long-term compounding. Stocks and mutual funds are ideal.",
        "cf": 0.87
    },
    {
        "id": "R019",
        "name": "Very Long Horizon (20+ Years)",
        "category": "Investment Horizon",
        "priority": 27,
        "condition": lambda p: p["investment_horizon"] >= 20,
        "action": {"stocks": +15, "real_estate": +5, "bonds": -10, "cash": -10},
        "explanation": "20+ year horizon: Maximum compounding power. Aggressive growth with real estate.",
        "cf": 0.90
    },

    # ─── CATEGORY 5: INCOME RULES (Priority 31-38) ──────────────────────────

    {
        "id": "R020",
        "name": "Very High Income",
        "category": "Income",
        "priority": 31,
        "condition": lambda p: p["income"] > 200000,
        "action": {"real_estate": +10, "stocks": +5, "cash": -10, "bonds": -5},
        "explanation": "Very high income (>$200k): Can afford illiquid assets. Real estate recommended.",
        "cf": 0.88
    },
    {
        "id": "R021",
        "name": "High Income",
        "category": "Income",
        "priority": 32,
        "condition": lambda p: 100000 <= p["income"] <= 200000,
        "action": {"stocks": +5, "mutual_funds": +5, "cash": -5, "bonds": -5},
        "explanation": "High income ($100k–$200k): Good capacity for growth investments.",
        "cf": 0.85
    },
    {
        "id": "R022",
        "name": "Moderate Income",
        "category": "Income",
        "priority": 33,
        "condition": lambda p: 50000 <= p["income"] < 100000,
        "action": {"mutual_funds": +10, "stocks": -5, "real_estate": -5},
        "explanation": "Moderate income ($50k–$100k): Mutual funds offer diversification at lower cost.",
        "cf": 0.82
    },
    {
        "id": "R023",
        "name": "Low Income",
        "category": "Income",
        "priority": 34,
        "condition": lambda p: p["income"] < 50000,
        "action": {"cash": +10, "real_estate": -10, "stocks": -5, "mutual_funds": +5},
        "explanation": "Low income (<$50k): Prioritise liquidity and low-cost mutual funds over stocks.",
        "cf": 0.85
    },

    # ─── CATEGORY 6: DEBT RULES (Priority 39-46) ────────────────────────────

    {
        "id": "R024",
        "name": "High Debt-to-Income Ratio",
        "category": "Debt",
        "priority": 39,
        "condition": lambda p: (p["debts"] / p["income"]) > 0.5 if p["income"] > 0 else False,
        "action": {"cash": +15, "stocks": -10, "real_estate": -5},
        "explanation": "Debt exceeds 50% of income. Prioritise debt repayment — reduce risky investments.",
        "cf": 0.92
    },
    {
        "id": "R025",
        "name": "Moderate Debt",
        "category": "Debt",
        "priority": 40,
        "condition": lambda p: 0.2 < (p["debts"] / p["income"]) <= 0.5 if p["income"] > 0 else False,
        "action": {"cash": +5, "stocks": -5},
        "explanation": "Moderate debt (20–50% of income). Keep some cash buffer while investing.",
        "cf": 0.80
    },
    {
        "id": "R026",
        "name": "Low Debt",
        "category": "Debt",
        "priority": 41,
        "condition": lambda p: (p["debts"] / p["income"]) <= 0.2 if p["income"] > 0 else True,
        "action": {"stocks": +5, "cash": -5},
        "explanation": "Low debt (<20% of income). Good financial position — can take more investment risk.",
        "cf": 0.85
    },
    {
        "id": "R027",
        "name": "Debt-Free",
        "category": "Debt",
        "priority": 42,
        "condition": lambda p: p["debts"] == 0,
        "action": {"stocks": +10, "real_estate": +5, "cash": -10, "bonds": -5},
        "explanation": "Debt-free: Excellent position. More capital can go into growth assets.",
        "cf": 0.88
    },

    # ─── CATEGORY 7: GOAL-BASED RULES (Priority 47-56) ──────────────────────

    {
        "id": "R028",
        "name": "Goal: Retirement",
        "category": "Goals",
        "priority": 47,
        "condition": lambda p: "retirement" in p["goals"].lower(),
        "action": {"bonds": +10, "mutual_funds": +5, "stocks": -5, "cash": -10},
        "explanation": "Retirement goal: Long-term stability mix. Bonds and mutual funds for steady growth.",
        "cf": 0.88
    },
    {
        "id": "R029",
        "name": "Goal: Home Purchase",
        "category": "Goals",
        "priority": 48,
        "condition": lambda p: "home" in p["goals"].lower() or "house" in p["goals"].lower(),
        "action": {"cash": +15, "bonds": +5, "stocks": -10, "real_estate": -10},
        "explanation": "Home purchase goal: Need liquid funds. Increase cash and short-term bonds.",
        "cf": 0.90
    },
    {
        "id": "R030",
        "name": "Goal: Education",
        "category": "Goals",
        "priority": 49,
        "condition": lambda p: "education" in p["goals"].lower() or "college" in p["goals"].lower(),
        "action": {"bonds": +10, "mutual_funds": +5, "cash": +5, "stocks": -20},
        "explanation": "Education funding goal: Timeline is fixed. Conservative mix to protect capital.",
        "cf": 0.87
    },
    {
        "id": "R031",
        "name": "Goal: Wealth Building",
        "category": "Goals",
        "priority": 50,
        "condition": lambda p: "wealth" in p["goals"].lower() or "growth" in p["goals"].lower(),
        "action": {"stocks": +15, "real_estate": +5, "cash": -10, "bonds": -10},
        "explanation": "Wealth building goal: Aggressive growth strategy with stocks and real estate.",
        "cf": 0.88
    },
    {
        "id": "R032",
        "name": "Goal: Income Generation",
        "category": "Goals",
        "priority": 51,
        "condition": lambda p: "income" in p["goals"].lower() or "dividend" in p["goals"].lower(),
        "action": {"bonds": +15, "real_estate": +10, "stocks": -10, "cash": -15},
        "explanation": "Income generation goal: Bonds and real estate provide regular income streams.",
        "cf": 0.86
    },
    {
        "id": "R033",
        "name": "Goal: Capital Preservation",
        "category": "Goals",
        "priority": 52,
        "condition": lambda p: "preservation" in p["goals"].lower() or "safe" in p["goals"].lower(),
        "action": {"bonds": +20, "cash": +10, "gold": +5, "stocks": -20, "mutual_funds": -15},
        "explanation": "Capital preservation goal: Safety first. Heavy bonds, cash, and gold.",
        "cf": 0.92
    },

    # ─── CATEGORY 8: EMPLOYMENT STATUS RULES (Priority 57-62) ───────────────

    {
        "id": "R034",
        "name": "Self-Employed / Freelancer",
        "category": "Employment",
        "priority": 57,
        "condition": lambda p: p.get("employment_status", "").lower() in ["self_employed", "freelancer"],
        "action": {"cash": +10, "bonds": +5, "stocks": -10, "real_estate": -5},
        "explanation": "Self-employed: Irregular income means higher cash buffer is essential.",
        "cf": 0.88
    },
    {
        "id": "R035",
        "name": "Unemployed",
        "category": "Employment",
        "priority": 58,
        "condition": lambda p: p.get("employment_status", "").lower() == "unemployed",
        "action": {"cash": +20, "stocks": -15, "mutual_funds": -5},
        "explanation": "Currently unemployed: Do not risk capital needed for living expenses.",
        "cf": 0.95
    },
    {
        "id": "R036",
        "name": "Government / Stable Employment",
        "category": "Employment",
        "priority": 59,
        "condition": lambda p: p.get("employment_status", "").lower() in ["government", "stable"],
        "action": {"stocks": +5, "real_estate": +5, "cash": -5, "bonds": -5},
        "explanation": "Stable government job: Reliable income allows more aggressive investment.",
        "cf": 0.82
    },

    # ─── CATEGORY 9: DEPENDENTS RULES (Priority 63-66) ──────────────────────

    {
        "id": "R037",
        "name": "High Dependents (3+)",
        "category": "Dependents",
        "priority": 63,
        "condition": lambda p: p.get("dependents", 0) >= 3,
        "action": {"cash": +10, "bonds": +5, "stocks": -10, "real_estate": -5},
        "explanation": "3+ dependents: Family obligations require more liquid and safe investments.",
        "cf": 0.87
    },
    {
        "id": "R038",
        "name": "Moderate Dependents (1-2)",
        "category": "Dependents",
        "priority": 64,
        "condition": lambda p: 1 <= p.get("dependents", 0) < 3,
        "action": {"cash": +5, "stocks": -5},
        "explanation": "1–2 dependents: Slight increase in cash for family financial security.",
        "cf": 0.80
    },
    {
        "id": "R039",
        "name": "No Dependents",
        "category": "Dependents",
        "priority": 65,
        "condition": lambda p: p.get("dependents", 0) == 0,
        "action": {"stocks": +5, "cash": -5},
        "explanation": "No dependents: Greater freedom to invest aggressively.",
        "cf": 0.80
    },

    # ─── CATEGORY 10: GOLD / INFLATION HEDGE RULES (Priority 67-70) ─────────

    {
        "id": "R040",
        "name": "Inflation Hedge — Add Gold",
        "category": "Inflation Hedge",
        "priority": 67,
        "condition": lambda p: p["investment_horizon"] > 5 and p["risk_tolerance"] in ["moderate", "low", "very_low"],
        "action": {"gold": +8, "cash": -5, "bonds": -3},
        "explanation": "Medium+ horizon with moderate/low risk: Gold provides inflation protection.",
        "cf": 0.82
    },
    {
        "id": "R041",
        "name": "Long Horizon Gold Allocation",
        "category": "Inflation Hedge",
        "priority": 68,
        "condition": lambda p: p["investment_horizon"] > 15,
        "action": {"gold": +5, "bonds": -5},
        "explanation": "Long horizon: Gold as 5% hedge against long-term currency devaluation.",
        "cf": 0.78
    },

    # ─── CATEGORY 11: REAL ESTATE RULES (Priority 71-74) ────────────────────

    {
        "id": "R042",
        "name": "High Income + Long Horizon = Real Estate",
        "category": "Real Estate",
        "priority": 71,
        "condition": lambda p: p["income"] > 80000 and p["investment_horizon"] >= 10,
        "action": {"real_estate": +10, "bonds": -5, "cash": -5},
        "explanation": "High income and long horizon: Real estate offers excellent long-term returns.",
        "cf": 0.83
    },
    {
        "id": "R043",
        "name": "Short Horizon — No Real Estate",
        "category": "Real Estate",
        "priority": 72,
        "condition": lambda p: p["investment_horizon"] < 5,
        "action": {"real_estate": -10, "cash": +5, "bonds": +5},
        "explanation": "Short horizon: Real estate is illiquid. Remove from short-term portfolio.",
        "cf": 0.90
    },

    # ─── CATEGORY 12: COMBINED / COMPOSITE RULES (Priority 75-85) ──────────

    {
        "id": "R044",
        "name": "Young + High Risk = Aggressive Growth",
        "category": "Composite",
        "priority": 75,
        "condition": lambda p: p["age"] < 35 and p["risk_tolerance"] in ["high", "very_high"],
        "action": {"stocks": +10, "bonds": -5, "cash": -5},
        "explanation": "Young and high risk tolerance: Strong compounding opportunity — maximise stocks.",
        "cf": 0.91
    },
    {
        "id": "R045",
        "name": "Old + Low Risk = Ultra Conservative",
        "category": "Composite",
        "priority": 76,
        "condition": lambda p: p["age"] >= 55 and p["risk_tolerance"] in ["low", "very_low"],
        "action": {"bonds": +10, "cash": +10, "stocks": -15, "mutual_funds": -5},
        "explanation": "Older age with low risk: Strongly conservative. Bonds and cash dominate.",
        "cf": 0.93
    },
    {
        "id": "R046",
        "name": "High Debt + Low Income = Emergency Mode",
        "category": "Composite",
        "priority": 77,
        "condition": lambda p: (p["debts"] / p["income"]) > 0.4 and p["income"] < 60000 if p["income"] > 0 else False,
        "action": {"cash": +20, "stocks": -15, "real_estate": -5},
        "explanation": "High debt with low income: Focus on stability, not investing. Hold cash.",
        "cf": 0.94
    },
    {
        "id": "R047",
        "name": "Long Horizon + High Risk + Young",
        "category": "Composite",
        "priority": 78,
        "condition": lambda p: p["investment_horizon"] > 15 and p["risk_tolerance"] in ["high", "very_high"] and p["age"] < 40,
        "action": {"stocks": +15, "mutual_funds": +5, "bonds": -10, "cash": -10},
        "explanation": "Young, long horizon, high risk: Ideal conditions for maximum equity growth.",
        "cf": 0.92
    },
    {
        "id": "R048",
        "name": "High Savings Rate",
        "category": "Composite",
        "priority": 79,
        "condition": lambda p: (p["savings"] / p["income"]) > 0.5 if p["income"] > 0 else False,
        "action": {"stocks": +5, "mutual_funds": +5, "cash": -5, "bonds": -5},
        "explanation": "High savings rate (>50% of income): Strong financial discipline allows growth focus.",
        "cf": 0.83
    },
    {
        "id": "R049",
        "name": "Low Savings Rate",
        "category": "Composite",
        "priority": 80,
        "condition": lambda p: (p["savings"] / p["income"]) < 0.1 if p["income"] > 0 else False,
        "action": {"cash": +10, "stocks": -5, "real_estate": -5},
        "explanation": "Low savings (<10% of income): Build savings first before aggressive investing.",
        "cf": 0.88
    },
    {
        "id": "R050",
        "name": "Pre-Retirement + Moderate Risk",
        "category": "Composite",
        "priority": 81,
        "condition": lambda p: 50 <= p["age"] < 60 and p["risk_tolerance"] == "moderate",
        "action": {"bonds": +10, "mutual_funds": +5, "stocks": -10, "cash": -5},
        "explanation": "Near retirement with moderate risk: Gradual shift to conservative allocation.",
        "cf": 0.86
    },

    # ─── CATEGORY 13: MUTUAL FUND RULES (Priority 86-90) ────────────────────

    {
        "id": "R051",
        "name": "First-Time Investor — Mutual Funds",
        "category": "Mutual Funds",
        "priority": 86,
        "condition": lambda p: p.get("existing_investments", "none").lower() == "none",
        "action": {"mutual_funds": +15, "stocks": -10, "bonds": -5},
        "explanation": "New investor: Mutual funds provide instant diversification — ideal starting point.",
        "cf": 0.87
    },
    {
        "id": "R052",
        "name": "Experienced Investor",
        "category": "Mutual Funds",
        "priority": 87,
        "condition": lambda p: p.get("existing_investments", "none").lower() in ["stocks", "bonds", "mixed"],
        "action": {"stocks": +5, "mutual_funds": -5},
        "explanation": "Experienced investor: Can manage direct stock investments more efficiently.",
        "cf": 0.80
    },

    # ─── CATEGORY 14: SPECIAL SITUATION RULES (Priority 91-100) ────────────

    {
        "id": "R053",
        "name": "Very High Net Worth",
        "category": "Special Situation",
        "priority": 91,
        "condition": lambda p: p["savings"] > 1000000,
        "action": {"real_estate": +10, "gold": +5, "stocks": +5, "cash": -10, "bonds": -10},
        "explanation": "Very high net worth (>$1M savings): Diversify into real estate and gold at scale.",
        "cf": 0.85
    },
    {
        "id": "R054",
        "name": "Very Low Net Worth",
        "category": "Special Situation",
        "priority": 92,
        "condition": lambda p: p["savings"] < 10000,
        "action": {"cash": +15, "mutual_funds": +5, "stocks": -10, "real_estate": -10},
        "explanation": "Low savings (<$10k): Build foundation first. Low-cost mutual funds and cash.",
        "cf": 0.88
    },
    {
        "id": "R055",
        "name": "Income Exceeds Expenses 3x",
        "category": "Special Situation",
        "priority": 93,
        "condition": lambda p: p["income"] > p["monthly_expenses"] * 3 * 12,
        "action": {"stocks": +5, "real_estate": +5, "cash": -5, "bonds": -5},
        "explanation": "Income greatly exceeds expenses: Strong investable surplus — increase growth assets.",
        "cf": 0.82
    },
    {
        "id": "R056",
        "name": "Income Below Expenses",
        "category": "Special Situation",
        "priority": 94,
        "condition": lambda p: p["income"] < p["monthly_expenses"] * 12,
        "action": {"cash": +20, "stocks": -15, "real_estate": -5},
        "explanation": "Income does not cover annual expenses: Financial distress — hold maximum cash.",
        "cf": 0.96
    },
    {
        "id": "R057",
        "name": "Mid-Age Debt-Free High Income",
        "category": "Special Situation",
        "priority": 95,
        "condition": lambda p: 35 <= p["age"] < 50 and p["debts"] == 0 and p["income"] > 100000,
        "action": {"real_estate": +10, "stocks": +5, "bonds": -10, "cash": -5},
        "explanation": "Mid-age, debt-free, high income: Prime wealth-building opportunity.",
        "cf": 0.87
    },
    {
        "id": "R058",
        "name": "Young With High Debt",
        "category": "Special Situation",
        "priority": 96,
        "condition": lambda p: p["age"] < 30 and (p["debts"] / p["income"]) > 0.3 if p["income"] > 0 else False,
        "action": {"cash": +10, "bonds": +5, "stocks": -15},
        "explanation": "Young but heavily indebted: Pay off debt aggressively before investing.",
        "cf": 0.90
    },
    {
        "id": "R059",
        "name": "Balanced Risk-Horizon Match",
        "category": "Special Situation",
        "priority": 97,
        "condition": lambda p: p["risk_tolerance"] == "moderate" and 5 <= p["investment_horizon"] <= 15,
        "action": {"mutual_funds": +10, "stocks": +5, "bonds": -10, "cash": -5},
        "explanation": "Moderate risk with medium horizon: Mutual funds and stocks in balanced mix.",
        "cf": 0.84
    },
    {
        "id": "R060",
        "name": "Retirement Goal Near (5 Years Out)",
        "category": "Special Situation",
        "priority": 98,
        "condition": lambda p: "retirement" in p["goals"].lower() and p["investment_horizon"] <= 5,
        "action": {"bonds": +15, "cash": +10, "stocks": -15, "mutual_funds": -10},
        "explanation": "Retirement within 5 years: Shift aggressively to capital preservation.",
        "cf": 0.93
    },
    {
        "id": "R061",
        "name": "Young Retirement Saver (Long Run)",
        "category": "Special Situation",
        "priority": 99,
        "condition": lambda p: "retirement" in p["goals"].lower() and p["investment_horizon"] > 20 and p["age"] < 40,
        "action": {"stocks": +10, "mutual_funds": +5, "bonds": -10, "cash": -5},
        "explanation": "Young saving for retirement 20+ years away: Maximise equity compounding.",
        "cf": 0.91
    },
    {
        "id": "R062",
        "name": "Gold for Uncertainty Hedge",
        "category": "Special Situation",
        "priority": 100,
        "condition": lambda p: p["risk_tolerance"] in ["low", "very_low"] and p["income"] > 30000,
        "action": {"gold": +8, "stocks": -5, "bonds": -3},
        "explanation": "Low risk with adequate income: Gold adds stability and inflation protection.",
        "cf": 0.80
    },

    # ─── CATEGORY 15: FINE-TUNING RULES (Priority 101-110) ──────────────────

    {
        "id": "R063",
        "name": "Stock Market Literate",
        "category": "Fine Tuning",
        "priority": 101,
        "condition": lambda p: p.get("existing_investments", "").lower() == "stocks",
        "action": {"stocks": +5, "mutual_funds": -5},
        "explanation": "Already invested in stocks: Comfortable with direct equity. Reduce fund overlap.",
        "cf": 0.75
    },
    {
        "id": "R064",
        "name": "Diversification Rule — No Single Asset > 50%",
        "category": "Fine Tuning",
        "priority": 102,
        "condition": lambda p: True,
        "action": {},
        "explanation": "Diversification principle: No single asset class should exceed 50% of portfolio.",
        "cf": 0.99
    },
    {
        "id": "R065",
        "name": "Minimum Cash Reserve Always",
        "category": "Fine Tuning",
        "priority": 103,
        "condition": lambda p: True,
        "action": {},
        "explanation": "Always maintain minimum 5% cash for opportunities and emergencies.",
        "cf": 0.99
    },
]