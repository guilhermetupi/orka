from orka.core.state import OrkaState, Tier

RISK_KEYWORDS = {
    "auth": 3,
    "login": 2,
    "payment": 4,
    "pagamento": 4,
    "database": 3,
    "db": 3,
    "migration": 4,
    "refactor": 2,
    "security": 4,
    "segurança": 4,
    "delete": 3,
    "remove": 2,
}


def estimate_risk(prompt: str) -> int:
    text = prompt.lower()
    score = 0

    for keyword, value in RISK_KEYWORDS.items():
        if keyword in text:
            score += value

    if len(prompt) > 300:
        score += 1

    return min(score, 10)


def router_node(state: OrkaState) -> OrkaState:
    risk_score = estimate_risk(state["prompt"])

    tier: Tier
    if state.get("tier"):
        tier = state["tier"]
    elif risk_score <= 2:
        tier = "t0"
    elif risk_score <= 6:
        tier = "t1"
    else:
        tier = "t2"

    return {
        **state,
        "risk_score": risk_score,
        "tier": tier,
        "needs_review": risk_score >= 5,
    }
