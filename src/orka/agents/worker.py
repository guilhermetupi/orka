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
                    "Use the provided context when relevant.\n"
                    "For now, do not edit files directly.\n"
                    "Return a concise implementation proposal."
                ),
            },
            {
                "role": "user",
                "content": f"""
                  Mode: {state["mode"]}
                  Task: {state["prompt"]}

                  Context:
                  {state.get("context", "")}
                """,
            },
        ],
    )

    return {
        **state,
        "result": response,
    }
