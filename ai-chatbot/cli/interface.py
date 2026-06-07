"""
cli/interface.py
----------------
Terminal user interface built with the Rich library.
Handles all user input, command parsing, and formatted output.

Commands are parsed here and delegated to the Conversation orchestrator.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box

from core.conversation import Conversation
from features.persona import PERSONAS
from features.sentiment import SENTIMENT_EMOJI
from utils.helpers import export_conversation_json, export_conversation_txt
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)
console = Console()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    banner = Text(justify="center")
    banner.append("🤖 AI Chatbot ", style="bold cyan")
    banner.append(f"v{settings.APP_VERSION}\n", style="dim")
    banner.append(f"Powered by Claude ({settings.MODEL_NAME})", style="italic dim")
    console.print(Panel(banner, border_style="cyan", padding=(1, 4)))


def _print_help(conv: Conversation) -> None:
    table = Table(title="Available Commands", box=box.ROUNDED, border_style="cyan")
    table.add_column("Command", style="bold yellow", no_wrap=True)
    table.add_column("Description", style="white")

    commands = [
        ("/help",              "Show this help menu"),
        ("/persona <name>",    f"Switch persona. Options: {', '.join(conv.available_personas)}"),
        ("/summary",           "Summarize the current conversation"),
        ("/sentiment",         "Show the last detected sentiment"),
        ("/history",           "Print full conversation history"),
        ("/export json",       "Save conversation to JSON file"),
        ("/export txt",        "Save conversation to plain text file"),
        ("/clear",             "Clear conversation history"),
        ("/quit  or  /exit",   "Exit the chatbot"),
    ]
    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)


def _print_personas() -> None:
    table = Table(title="Available Personas", box=box.SIMPLE, border_style="magenta")
    table.add_column("Key", style="bold yellow")
    table.add_column("Name", style="bold")
    table.add_column("Description", style="dim")

    for key, info in PERSONAS.items():
        table.add_row(key, info["name"], info["description"])
    console.print(table)


def _print_history(conv: Conversation) -> None:
    messages = conv.memory.get_all()
    if not messages:
        console.print("[dim]No messages in history yet.[/dim]")
        return

    console.print(f"\n[bold]Conversation History[/bold] ({len(messages)} messages)\n")
    for i, msg in enumerate(messages, 1):
        if msg.role == "user":
            emoji = SENTIMENT_EMOJI.get(msg.sentiment or "neutral", "😐")
            header = Text(f"[{i}] You {emoji}", style="bold green")
        else:
            header = Text(f"[{i}] 🤖 Bot", style="bold cyan")
        console.print(header)
        console.print(f"    {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}")
        console.print()


# ── Command Dispatcher ─────────────────────────────────────────────────────────

def _handle_command(raw: str, conv: Conversation) -> bool:
    """
    Parse and execute a slash command.

    Args:
        raw:  The raw input string (starts with /).
        conv: The active Conversation instance.

    Returns:
        True to continue the loop, False to exit.
    """
    parts = raw.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/quit", "/exit"):
        console.print("\n[bold cyan]👋 Goodbye! Come back soon.[/bold cyan]\n")
        return False

    elif cmd == "/help":
        _print_help(conv)

    elif cmd == "/persona":
        if not arg:
            _print_personas()
            console.print("[dim]Usage: /persona <name>[/dim]")
        elif conv.switch_persona(arg):
            console.print(
                f"[bold green]✅ Switched to persona: [yellow]{conv.current_persona}[/yellow][/bold green]"
            )
        else:
            console.print(f"[bold red]❌ Unknown persona '{arg}'.[/bold red]")
            _print_personas()

    elif cmd == "/summary":
        console.print("\n[bold cyan]📝 Generating summary...[/bold cyan]")
        summary = conv.get_summary()
        console.print(Panel(Markdown(summary), title="Conversation Summary", border_style="cyan"))

    elif cmd == "/sentiment":
        sentiment = conv.last_sentiment
        emoji = SENTIMENT_EMOJI.get(sentiment, "😐")
        console.print(
            f"\n[bold]Last detected sentiment:[/bold] {emoji} [yellow]{sentiment}[/yellow]\n"
        )

    elif cmd == "/history":
        _print_history(conv)

    elif cmd == "/export":
        messages = conv.memory.get_all()
        if not messages:
            console.print("[dim]Nothing to export yet.[/dim]")
        else:
            fmt = arg.lower() if arg else "json"
            if fmt == "txt":
                path = export_conversation_txt(messages, conv.current_persona)
            else:
                path = export_conversation_json(messages, conv.current_persona)
            console.print(f"[bold green]✅ Saved to:[/bold green] [underline]{path}[/underline]")

    elif cmd == "/clear":
        conv.clear()
        console.print("[bold green]✅ Conversation history cleared.[/bold green]")

    else:
        console.print(f"[bold red]❓ Unknown command '{cmd}'. Type /help for options.[/bold red]")

    return True


# ── Main Loop ──────────────────────────────────────────────────────────────────

def run() -> None:
    """Start the interactive CLI chatbot loop."""
    _print_banner()

    # Validate config before starting
    settings.validate()

    conv = Conversation()

    console.print(
        f"\n[dim]Persona:[/dim] [bold cyan]{conv.current_persona}[/bold cyan]  "
        f"[dim]|  Type[/dim] [bold yellow]/help[/bold yellow] [dim]for commands[/dim]\n"
    )

    while True:
        try:
            # ── Get user input ─────────────────────────────────────────────
            user_input = Prompt.ask("[bold green]You[/bold green]").strip()

            if not user_input:
                continue

            # ── Command? ───────────────────────────────────────────────────
            if user_input.startswith("/"):
                should_continue = _handle_command(user_input, conv)
                if not should_continue:
                    break
                continue

            # ── Regular message → send to LLM ─────────────────────────────
            with console.status("[bold cyan]🤖 Thinking...[/bold cyan]", spinner="dots"):
                reply = conv.send(user_input)

            sentiment = conv.last_sentiment
            emoji = SENTIMENT_EMOJI.get(sentiment, "😐")

            console.print(
                f"\n[bold cyan]🤖 Bot[/bold cyan] "
                f"[dim](Persona: {conv.current_persona} | Sentiment: {emoji} {sentiment})[/dim]"
            )
            console.print(Panel(Markdown(reply), border_style="dim", padding=(0, 1)))

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]👋 Interrupted. Goodbye![/bold cyan]\n")
            break

        except RuntimeError as exc:
            console.print(f"\n[bold red]⚠️  Error:[/bold red] {exc}\n")
            logger.error("Runtime error in main loop: %s", exc)

        except Exception as exc:
            console.print(f"\n[bold red]💥 Unexpected error:[/bold red] {exc}\n")
            logger.exception("Unexpected error in main loop")
