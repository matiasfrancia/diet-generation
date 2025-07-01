import typer

from project_fitness_adri.cli import diet_cmd, exercises_cmd, user_cmd

app = typer.Typer()
app.add_typer(diet_cmd.app, name="diet")
app.add_typer(exercises_cmd.app, name="exercises")
app.add_typer(user_cmd.app, name="user")
