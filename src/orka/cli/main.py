import typer
from rich.console import Console

from orka.core.config import settings
from orka.core.graph import build_implement_graph
from orka.core.llm import chat, setup_litellm
from orka.core.router import get_model_for_tier
from orka.rag.indexer import index_project
from orka.tools.rag import search

app = typer.Typer(
    name="orka", help="Orka: local-first multi-agent coding orchestrator."
)

console = Console()


@app.command()
def version() -> None:
    """Show the version and exit."""
    console.print("[bold cyan]Orka[/bold cyan] v0.1.0")


@app.command()
def ask(prompt: str, tier: str = "t0") -> None:
    """Ask Orka something about the current project."""

    setup_litellm()

    model = get_model_for_tier(tier)

    console.print(f"[dim]Using model:[/dim] {model}")

    results = search(prompt, k=8)
    seen = set()
    filtered = []

    for r in results:
        if r["path"] not in seen:
            filtered.append(r)
            seen.add(r["path"])

    results = filtered[:5]

    console.print("\n[dim]Context sources:[/dim]")

    MAX_CONTEXT_CHARS = 4000

    context = ""
    for r in results:
        console.print(f" - {r['path']}")
        if len(context) + len(r["content"]) > MAX_CONTEXT_CHARS:
            break
        context += r["content"] + "\n\n"

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer.\n"
                    "Answer based on the provided context.\n"
                    "If the answer is not in the context, say you don't know.\n"
                    "Be concise and technical."
                ),
            },
            {
                "role": "user",
                "content": f"""
                    Context:
                    {context}

                    Question:
                    {prompt}
                """,
            },
        ],
    )

    console.print("\n[bold green]Response:[/bold green]\n")
    console.print(response)


@app.command()
def index():
    """Index the current project."""
    console.print("[cyan]Indexing project...[/cyan]")
    index_project(".")
    console.print("[green]Done.[/green]")


@app.command()
def implement(prompt: str) -> None:
    """Propose an implementation using Orka's multi-agent flow."""

    setup_litellm()

    results = search(prompt, k=5)

    context = ""
    for r in results:
        context += f"File: {r['path']}\n{r['content']}\n\n"

    graph = build_implement_graph()

    final_state = graph.invoke(
        {
            "mode": "implement",
            "prompt": prompt,
            "context": context,
        }
    )

    console.print(f"[dim]Tier:[/dim] {final_state.get('tier')}")
    console.print(f"[dim]Risk score:[/dim] {final_state.get('risk_score')}")
    console.print(f"[dim]Needs review:[/dim] {final_state.get('needs_review')}")

    console.print("\n[bold green]Implementation:[/bold green]\n")
    console.print(final_state.get("result", ""))

    if final_state.get("review"):
        console.print("\n[bold yellow]Review:[/bold yellow]\n")
        console.print(final_state["review"])
