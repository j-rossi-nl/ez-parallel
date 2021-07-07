# type: ignore[attr-defined]

from typing import Optional

import random
from enum import Enum

import typer
from ez_parallel import __version__
from rich.console import Console


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="ez-parallel",
    help="Easy Parallel Multiprocessing",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Prints the version of the package."""
    if value:
        console.print(
            f"[yellow]ez-parallel[/] version: [bold blue]{__version__}[/]"
        )
        raise typer.Exit()


@app.command(name="")
def main(
    version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the ez-parallel package.",
    ),
):
    pass


if __name__ == "__main__":
    app()
