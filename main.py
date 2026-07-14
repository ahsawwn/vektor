import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from database.connection import init_db
from database.models import UserPreference, ConversationLog
from memory.vector_store import VectorMemory
from core.agent import VektorAgent
from database.connection import engine
from sqlmodel import Session, select

app = typer.Typer()
console = Console()


@app.command()
def chat() -> None:
    init_db()
    agent = VektorAgent()
    console.print(Panel.fit("Vektor — Persistent Local AI", border_style="blue"))
    console.print("[dim]Type /exit to quit, /clear to reset context.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Goodbye.[/yellow]")
            sys.exit(0)

        if user_input.strip().lower() in ("/exit", "/quit"):
            console.print("[yellow]Goodbye.[/yellow]")
            break
        if user_input.strip().lower() == "/clear":
            with Session(engine) as session:
                stmt = select(ConversationLog)
                logs = session.exec(stmt).all()
                for log in logs:
                    session.delete(log)
                session.commit()
            vm = VectorMemory()
            vm.delete_all()
            console.print("[green]Conversation history cleared.[/green]")
            continue

        console.print("[dim]Thinking...[/dim]")
        try:
            reply = agent.chat(user_input)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            continue

        console.print(Panel(reply, border_style="green", title="[bold]Vektor[/bold]"))


@app.command()
def remember(key: str, value: str) -> None:
    init_db()
    with Session(engine) as session:
        stmt = select(UserPreference).where(UserPreference.key == key)
        existing = session.exec(stmt).one_or_none()
        if existing:
            existing.value = value
        else:
            session.add(UserPreference(key=key, value=value))
        session.commit()
    console.print(f"[green]Stored[/green] {key} → {value}")


@app.command()
def forget(
    all: bool = typer.Option(False, "--all", help="Clear all memory indexes"),
) -> None:
    if all:
        with Session(engine) as session:
            stmt = select(ConversationLog)
            logs = session.exec(stmt).all()
            for log in logs:
                session.delete(log)
            session.commit()

        with Session(engine) as session:
            stmt = select(UserPreference)
            prefs = session.exec(stmt).all()
            for p in prefs:
                session.delete(p)
            session.commit()

        vm = VectorMemory()
        vm.delete_all()
        console.print("[green]All conversation logs, preferences, and vector indexes cleared.[/green]")


@app.command()
def status() -> None:
    init_db()

    with Session(engine) as session:
        stmt = select(ConversationLog)
        logs = session.exec(stmt).all()
        pref_stmt = select(UserPreference)
        prefs = session.exec(pref_stmt).all()

    vm = VectorMemory()

    table = Table(title="Vektor System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Conversation Logs", str(len(logs)))
    table.add_row("User Preferences", str(len(prefs)))
    table.add_row("Vector Memory Entries", str(vm.count()))
    table.add_row("SQLite Path", str(engine.url))

    console.print(table)


@app.callback()
def callback() -> None:
    pass


def main() -> None:
    app()


if __name__ == "__main__":
    main()
