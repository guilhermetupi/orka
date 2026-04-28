from orka.core.llm import chat
from orka.core.router import get_model_for_tier
from orka.core.state import OrkaState


def self_check_node(state: OrkaState) -> OrkaState:
    # barato e determinístico por enquanto
    result = state.get("result", "")

    if not result.strip():
        return {
            **state,
            "needs_review": True,
        }

    return state


def reviewer_node(state: OrkaState) -> OrkaState:
    # economiza: reviewer no máximo T1 por padrão
    review_tier = "t1" if state["tier"] in ("t1", "t2") else "t0"
    model = get_model_for_tier(review_tier)

    review = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Orka's review agent.\n"
                    "Review the proposed implementation.\n"
                    "Focus on risk, missing steps, bugs, and unsafe assumptions.\n"
                    "Be concise."
                ),
            },
            {
                "role": "user",
                "content": f"""
                  Task:
                  {state["prompt"]}

                  Implementation proposal:
                  {state.get("result", "")}
                """,
            },
        ],
    )

    return {
        **state,
        "review": review,
    }
