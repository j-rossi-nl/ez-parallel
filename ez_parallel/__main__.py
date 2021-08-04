# type: ignore[attr-defined]
import random
import time
from enum import Enum

import typer
from ez_parallel import __version__, list_iterator, multiprocess, queue_worker
from rich.console import Console

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


if __name__ == "__main__":
    app()
