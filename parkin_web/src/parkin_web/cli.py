"""Console script for parkin_web."""
import parkin_web

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for parkin_web."""
    console.print("Replace this message by putting your code into "
               "parkin_web.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
