# backend/rules_engine.py
from knowledge_base import RULES

BASE_ALLOCATION = {
    "stocks": 25,
    "bonds": 20,
    "mutual_funds": 20,
    "gold": 5,
    "real_estate": 10,
    "cash": 20
}

def clamp(value, min_val=0, max_val=100):
    return max(min_val, min(max_val, value))

def normalize_allocation(allocation):
    """Ensure all allocations sum to 100"""
    total = sum(allocation.values())
    if total == 0:
        return allocation
    factor = 100.0 / total
    normalized = {k: round(v * factor, 2) for k, v in allocation.items()}
    # Fix rounding
    diff = 100 - sum(normalized.values())
    # Add the rounding difference to the largest allocation
    if diff != 0:
        max_key = max(normalized, key=normalized.get)
        normalized[max_key] = round(normalized[max_key] + diff, 2)
    return normalized

def enforce_constraints(allocation):
    """No single asset > 50%, minimum 5% cash"""
    for key in allocation:
        if allocation[key] > 50:
            excess = allocation[key] - 50
            allocation[key] = 50
            # Distribute excess equally to others
            others = [k for k in allocation if k != key]
            per_other = excess / len(others)
            for o in others:
                allocation[o] += per_other

    # Ensure min 5% cash
    if allocation.get("cash", 0) < 5:
        deficit = 5 - allocation["cash"]
        allocation["cash"] = 5
        # Take from stocks first
        allocation["stocks"] = max(0, allocation.get("stocks", 0) - deficit)

    return allocation

def compute_risk_score(profile):
    """
    Compute numeric risk score 0-100
    Higher = more risk capacity
    """
    score = 50  # base

    # Age factor (younger = more risk capacity)
    age = profile["age"]
    if age < 25: score += 20
    elif age < 35: score += 15
    elif age < 45: score += 10
    elif age < 55: score += 0
    elif age < 65: score -= 10
    else: score -= 20

    # Risk tolerance
    rt_map = {"very_high": 20, "high": 10, "moderate": 0, "low": -10, "very_low": -20}
    score += rt_map.get(profile.get("risk_tolerance", "moderate"), 0)

    # Horizon
    horizon = profile["investment_horizon"]
    if horizon >= 20: score += 15
    elif horizon >= 10: score += 10
    elif horizon >= 5: score += 5
    elif horizon >= 2: score -= 5
    else: score -= 15

    # Debt factor
    if profile["income"] > 0:
        dti = profile["debts"] / profile["income"]
        if dti > 0.5: score -= 15
        elif dti > 0.3: score -= 8
        elif dti == 0: score += 5

    # Emergency fund factor
    months_covered = profile["savings"] / profile["monthly_expenses"] if profile["monthly_expenses"] > 0 else 0
    if months_covered >= 6: score += 5
    elif months_covered < 3: score -= 10

    return max(0, min(100, score))

def get_risk_label(score):
    if score >= 80: return "Aggressive"
    elif score >= 65: return "Moderately Aggressive"
    elif score >= 50: return "Moderate"
    elif score >= 35: return "Moderately Conservative"
    else: return "Conservative"

def run_inference(profile):
    """
    Main inference engine
    Returns: allocation dict, fired_rules list, certainty_factor, risk_score, risk_label
    """
    # Sort rules by priority
    sorted_rules = sorted(RULES, key=lambda r: r["priority"])

    allocation = dict(BASE_ALLOCATION)
    fired_rules = []
    certainty_factors = []

    for rule in sorted_rules:
        try:
            condition_met = rule["condition"](profile)
        except Exception:
            condition_met = False

        if condition_met:
            # Apply action (adjustments to allocation)
            for asset, delta in rule["action"].items():
                if asset in allocation:
                    allocation[asset] = clamp(allocation[asset] + delta)

            fired_rules.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "condition_matched": f"Profile satisfied: {rule['name']}",
                "action_taken": str(rule["action"]) if rule["action"] else "Principle applied",
                "certainty_factor": rule["cf"],
                "priority": rule["priority"],
                "category": rule["category"],
                "explanation": rule["explanation"]
            })
            certainty_factors.append(rule["cf"])

    # Enforce constraints
    allocation = enforce_constraints(allocation)

    # Normalize to 100%
    allocation = normalize_allocation(allocation)

    # Round all values
    allocation = {k: round(v, 2) for k, v in allocation.items()}

    # Compute overall certainty factor (average of fired rules)
    overall_cf = round(sum(certainty_factors) / len(certainty_factors), 4) if certainty_factors else 0.5

    # Risk score
    risk_score = compute_risk_score(profile)
    risk_label = get_risk_label(risk_score)

    return allocation, fired_rules, overall_cf, risk_score, risk_label