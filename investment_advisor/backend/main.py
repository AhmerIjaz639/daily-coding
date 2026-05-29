# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json

from database import execute_query, init_database
from schemas import (
    UserRegister, UserLogin, ProfileInput,
    RiskAssessmentResponse, RecommendResponse,
    ExplainResponse, ScenarioInput, TokenResponse
)
from auth import hash_password, verify_password, create_token, decode_token
from rules_engine import run_inference, compute_risk_score, get_risk_label

app = FastAPI(
    title="Investment Recommendation Advisor",
    description="Rule-based expert system for investment advice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

@app.on_event("startup")
def startup():
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database init warning: {e}")

# ─── AUTH ENDPOINTS ──────────────────────────────────────────────────────────

@app.post("/register", response_model=TokenResponse)
def register(data: UserRegister):
    # Check if email exists
    existing = execute_query(
        "SELECT id FROM users WHERE email = %s",
        (data.email,), fetch_one=True
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    user_id = execute_query(
        "INSERT INTO users (name, email, hashed_password) VALUES (%s, %s, %s)",
        (data.name, data.email, hashed)
    )
    token = create_token({"sub": str(user_id), "email": data.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        name=data.name
    )

@app.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    user = execute_query(
        "SELECT id, name, email, hashed_password FROM users WHERE email = %s",
        (data.email,), fetch_one=True
    )
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": str(user["id"]), "email": user["email"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user["id"],
        name=user["name"]
    )

# ─── RISK ASSESSMENT ENDPOINT ────────────────────────────────────────────────

@app.post("/assess-risk", response_model=RiskAssessmentResponse)
def assess_risk(profile: ProfileInput):
    profile_dict = profile.model_dump()
    risk_score = compute_risk_score(profile_dict)
    risk_label = get_risk_label(risk_score)

    messages = {
        "Aggressive": "You have high risk capacity. Growth-oriented portfolio recommended.",
        "Moderately Aggressive": "You have good risk capacity with some caution needed.",
        "Moderate": "Balanced approach suits your profile.",
        "Moderately Conservative": "Capital protection is important for your situation.",
        "Conservative": "Capital preservation is the priority for your profile."
    }

    return RiskAssessmentResponse(
        risk_score=risk_score,
        risk_label=risk_label,
        message=messages.get(risk_label, "Assessment complete.")
    )

# ─── RECOMMENDATION ENDPOINT ─────────────────────────────────────────────────

@app.post("/recommend", response_model=RecommendResponse)
def recommend(profile: ProfileInput):
    profile_dict = profile.model_dump()

    # Save profile to DB
    profile_id = execute_query(
        """INSERT INTO user_profiles 
           (user_id, age, income, savings, debts, goals, investment_horizon,
            risk_tolerance, monthly_expenses, dependents, employment_status, existing_investments)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            profile.user_id, profile.age, profile.income, profile.savings,
            profile.debts, profile.goals, profile.investment_horizon,
            profile.risk_tolerance, profile.monthly_expenses,
            profile.dependents, profile.employment_status, profile.existing_investments
        )
    )

    # Run inference engine
    allocation, fired_rules, overall_cf, risk_score, risk_label = run_inference(profile_dict)

    # Save recommendation
    rec_id = execute_query(
        """INSERT INTO recommendations 
           (user_id, profile_id, stocks_pct, bonds_pct, mutual_funds_pct,
            gold_pct, real_estate_pct, cash_pct, risk_label, certainty_factor, risk_score)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            profile.user_id, profile_id,
            allocation["stocks"], allocation["bonds"], allocation["mutual_funds"],
            allocation["gold"], allocation["real_estate"], allocation["cash"],
            risk_label, overall_cf, risk_score
        )
    )

    # Save rule trace
    for rule in fired_rules:
        execute_query(
            """INSERT INTO rule_trace 
               (recommendation_id, rule_id, rule_name, condition_matched,
                action_taken, certainty_factor, priority, category)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                rec_id, rule["rule_id"], rule["rule_name"],
                rule["condition_matched"], rule["action_taken"],
                rule["certainty_factor"], rule["priority"], rule["category"]
            )
        )

    return RecommendResponse(
        recommendation_id=rec_id,
        user_id=profile.user_id,
        profile_id=profile_id,
        allocation=allocation,
        risk_label=risk_label,
        risk_score=risk_score,
        certainty_factor=overall_cf,
        rules_fired_count=len(fired_rules),
        message=f"Portfolio recommendation generated. {len(fired_rules)} rules applied."
    )
# ─── EXPLAIN ENDPOINT ────────────────────────────────────────────────────────

@app.get("/explain/{recommendation_id}", response_model=ExplainResponse)
def explain(recommendation_id: int):
    rec = execute_query(
        "SELECT * FROM recommendations WHERE id = %s",
        (recommendation_id,), fetch_one=True
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rules = execute_query(
        """SELECT * FROM rule_trace 
           WHERE recommendation_id = %s 
           ORDER BY priority ASC""",
        (recommendation_id,), fetch=True
    )


    from knowledge_base import RULES
    rules_map = {r["id"]: r["explanation"] for r in RULES}

    enriched_rules = []
    for rule in rules:
        enriched_rules.append({
            "rule_id": rule["rule_id"],
            "rule_name": rule["rule_name"],
            "category": rule["category"],
            "priority": rule["priority"],
            "condition_matched": rule["condition_matched"],
            "action_taken": rule["action_taken"],
            "certainty_factor": float(rule["certainty_factor"]),
            "explanation": rules_map.get(rule["rule_id"], rule["rule_name"])
        })

    overall_cf = float(rec["certainty_factor"])

    return ExplainResponse(
        recommendation_id=recommendation_id,
        rules=enriched_rules,
        total_rules_fired=len(enriched_rules),
        overall_cf=overall_cf
    )

# ─── HISTORY ENDPOINT ────────────────────────────────────────────────────────

@app.get("/history/{user_id}")
def get_history(user_id: int):
    recs = execute_query(
        """SELECT r.*, up.age, up.income, up.goals, up.risk_tolerance, up.investment_horizon
           FROM recommendations r
           JOIN user_profiles up ON r.profile_id = up.id
           WHERE r.user_id = %s
           ORDER BY r.created_at DESC
           LIMIT 20""",
        (user_id,), fetch=True
    )
    result = []
    for r in recs:
        result.append({
            "recommendation_id": r["id"],
            "risk_label": r["risk_label"],
            "certainty_factor": float(r["certainty_factor"]),
            "risk_score": r["risk_score"],
            "allocation": {
                "stocks": float(r["stocks_pct"]),
                "bonds": float(r["bonds_pct"]),
                "mutual_funds": float(r["mutual_funds_pct"]),
                "gold": float(r["gold_pct"]),
                "real_estate": float(r["real_estate_pct"]),
                "cash": float(r["cash_pct"])
            },
            "profile": {
                "age": r["age"],
                "income": float(r["income"]),
                "goals": r["goals"],
                "risk_tolerance": r["risk_tolerance"],
                "investment_horizon": r["investment_horizon"]
            },
            "created_at": str(r["created_at"])
        })
    return {"user_id": user_id, "history": result, "total": len(result)}

# ─── SCENARIO ENDPOINT ───────────────────────────────────────────────────────

@app.post("/scenario")
def save_scenario(data: ScenarioInput):
    scenario_id = execute_query(
        """INSERT INTO scenarios 
           (user_id, scenario_name, profile_snapshot, recommendation_snapshot)
           VALUES (%s, %s, %s, %s)""",
        (
            data.user_id, data.scenario_name,
            json.dumps(data.profile_snapshot),
            json.dumps(data.recommendation_snapshot)
        )
    )
    return {"scenario_id": scenario_id, "message": "Scenario saved successfully"}

@app.get("/scenarios/{user_id}")
def get_scenarios(user_id: int):
    scenarios = execute_query(
        "SELECT * FROM scenarios WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,), fetch=True
    )
    result = []
    for s in scenarios:
        result.append({
            "id": s["id"],
            "scenario_name": s["scenario_name"],
            "profile_snapshot": json.loads(s["profile_snapshot"]),
            "recommendation_snapshot": json.loads(s["recommendation_snapshot"]),
            "created_at": str(s["created_at"])
        })
    return {"scenarios": result}

@app.get("/")
def root():
    return {"message": "Investment Advisor API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)