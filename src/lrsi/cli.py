"""Minimal CLI for LRSI outer stack."""

import typer
from rich import print

app = typer.Typer(name="lrsi", help="LRSI — Local Recursive Self-Improvement")


@app.command()
def status():
    """Show high-level status of the LRSI outer stack."""
    print("[bold green]LRSI outer stack[/] — scaffolding ready")
    print("Foundation: clone & verify https://github.com/marcuszimmermann365/IRSI")
    print("Next: Phase 1 local model serving (vLLM / SGLang)")


if __name__ == "__main__":
    app()
