import typer
import logging


logging.basicConfig(level=logging.INFO)
app = typer.Typer(help="Endpoints related to meals plan (diet) generation")
