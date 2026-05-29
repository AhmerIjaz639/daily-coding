# backend/schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import datetime

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProfileInput(BaseModel):
    user_id: int
    age: int
    income: float
    savings: float
    debts: float
    goals: str
    investment_horizon: int
    risk_tolerance: str  # very_low, low, moderate, high, very_high
    monthly_expenses: float
    dependents: Optional[int] = 0
    employment_status: Optional[str] = "employed"
    existing_investments: Optional[str] = "none"

    @field_validator("risk_tolerance")
    @classmethod
    def validate_risk(cls, v):
        valid = ["very_low", "low", "moderate", "high", "very_high"]
        if v not in valid:
            raise ValueError(f"risk_tolerance must be one of {valid}")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if not (18 <= v <= 100):
            raise ValueError("Age must be between 18 and 100")
        return v

class RiskAssessmentResponse(BaseModel):
    risk_score: int
    risk_label: str
    message: str

class RecommendResponse(BaseModel):
    recommendation_id: int
    user_id: int
    profile_id: int
    allocation: dict
    risk_label: str
    risk_score: int
    certainty_factor: float
    rules_fired_count: int
    message: str

class RuleTraceItem(BaseModel):
    rule_id: str
    rule_name: str
    condition_matched: str
    action_taken: str
    certainty_factor: float
    priority: int
    category: str
    explanation: str

class ExplainResponse(BaseModel):
    recommendation_id: int
    rules: List[dict]
    total_rules_fired: int
    overall_cf: float

class ScenarioInput(BaseModel):
    user_id: int
    scenario_name: str
    profile_snapshot: dict
    recommendation_snapshot: dict

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str