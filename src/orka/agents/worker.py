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
                    "You are Orka's coding agent.\n"
                    "Return ONLY a valid unified git diff.\n"
                    "No explanations.\n"
                    "No markdown.\n"
                    "No text before or after.\n"
                    "Make minimal changes only.\n"
                    "Do not rewrite entire files unless necessary.\n"
                    "Only modify the necessary lines.\n"
                    "The output MUST start with '---'.\n"
                    """
Strictly follow this format:

--- a/path/to/file
+++ b/path/to/file

Never inline them on the same line.\n
                    """
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
