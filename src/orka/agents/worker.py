from orka.core.llm import chat
from orka.core.router import get_model_for_tier
from orka.core.state import OrkaState


def worker_node(state: OrkaState) -> OrkaState:
    model = get_model_for_tier(state["tier"])

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Orka's implementation agent.\n"
                    "Return a clear implementation proposal.\n"
                    "DO NOT return empty responses.\n"
                    "Be specific and actionable."
                ),
            },
            {
                "role": "user",
                "content": f"""
Task: {state["prompt"]}

Context:
{state.get("context", "")}
""",
            },
        ],
    )

    # 🔥 fallback defensivo
    if not response or not response.strip():
        response = "No implementation generated."

    return {
        **state,
        "result": response,
    }
