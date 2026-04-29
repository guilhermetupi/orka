from typing import Literal
import typer
from rich.console import Console

from orka.core.config import settings
from orka.core.graph import build_implement_graph
from orka.core.llm import chat, setup_litellm
from orka.core.router import get_model_for_tier
from orka.rag.indexer import index_project
from orka.tools.patch import PatchError, apply_patch, extract_diff, normalize_diff
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
def implement(
    prompt: str, tier: Literal["t0", "t1", "t2"] | None = None, dry_run: bool = False
) -> None:
    """Propose an implementation using Orka's multi-agent flow."""

    setup_litellm()

    results = search(prompt, k=5)

    context = ""
    for r in results:
        context += f"File: {r['path']}\n{r['content']}\n\n"

    graph = build_implement_graph()

    initial_state = {
        "mode": "implement",
        "prompt": prompt,
        "context": context,
    }
    if tier:
        initial_state["tier"] = tier
    final_state = graph.invoke(initial_state)

    console.print(f"[dim]Tier:[/dim] {final_state.get('tier')}")
    console.print(f"[dim]Risk score:[/dim] {final_state.get('risk_score')}")
    console.print(f"[dim]Needs review:[/dim] {final_state.get('needs_review')}")

    diff = final_state.get("result", "")
    diff = extract_diff(diff)
    diff = normalize_diff(diff)

    console.print("\n[bold green]Patch:[/bold green]\n")
    console.print(diff)

    if not diff.startswith("---"):
        console.print("[yellow]LLM did not return a diff. Showing raw output.[/yellow]")
        console.print(final_state.get("result", ""))
        return

    if not dry_run:
        confirm = typer.confirm("Apply this patch?")
        if not confirm:
            console.print("Aborted.")
            return
        else:
            console.print("[red]Mode:[/red] APPLYING CHANGES")
    else:
        console.print("[yellow]Mode:[/yellow] DRY RUN")

    try:
        apply_patch(diff, dry_run=dry_run)
    except PatchError as e:
        console.print(f"[red]Patch error:[/red] {e}")

    console.print(final_state.get("result", ""))

    if final_state.get("review"):
        console.print("\n[bold yellow]Review:[/bold yellow]\n")
        console.print(final_state["review"])
