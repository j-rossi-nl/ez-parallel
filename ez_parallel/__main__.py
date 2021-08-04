# type: ignore[attr-defined]
import random
import time

import typer
from ez_parallel import __version__, list_iterator, multiprocess, queue_worker
from rich.console import Console
from rich.syntax import Syntax

app = typer.Typer(
    name="ez-parallel",
    help="Easy Parallel Multiprocessing",
    add_completion=False,
)
console = Console()


@app.command()
def main():
    console.print(
        f"[yellow]ez-parallel[/] version: [bold blue]{__version__}[/]"
    )

    with open(__file__) as src:
        lines = src.readlines()

    code = "".join(lines[5:6] + list(map(lambda x: x[4:], lines[37:54])))
    syntax = Syntax(code=code, lexer_name="python", line_numbers=True)

    console.print("\n:arrow_forward: This sample code :arrow_heading_down:\n")
    console.print(syntax)
    console.print()
    console.print(
        "\n:arrow_forward: Generates this output :arrow_heading_down:\n"
    )

    # noinspection DuplicatedCode
    @queue_worker
    def square(x: float):
        _ = x ** 2
        time.sleep(0.1)
        return 1

    num_rows = 1000
    data = [random.random() for _ in range(num_rows)]

    gen, count = list_iterator(data)
    multiprocess(
        worker_fn=square,
        input_iterator_fn=gen,
        total=count,
        nb_workers=8,
        description="Compute Squares",
    )

    console.print()


if __name__ == "__main__":
    app()
