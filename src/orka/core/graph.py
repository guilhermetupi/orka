from langgraph.graph import END, START, StateGraph

from orka.agents.reviewer import reviewer_node, self_check_node
from orka.agents.router import router_node
from orka.agents.worker import worker_node
from orka.core.state import OrkaState


def should_review(state: OrkaState) -> str:
    if state.get("needs_review", False):
        return "reviewer"

    return END


def build_implement_graph():
    graph = StateGraph(OrkaState)

    graph.add_node("router", router_node)
    graph.add_node("worker", worker_node)
    graph.add_node("self_check", self_check_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "router")
    graph.add_edge("router", "worker")
    graph.add_edge("worker", "self_check")

    graph.add_conditional_edges(
        "self_check",
        should_review,
        {
            "reviewer": "reviewer",
            END: END,
        },
    )

    graph.add_edge("reviewer", END)

    return graph.compile()
