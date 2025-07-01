from typing import Literal, Optional
import typer
import logging

from diet_generation.diet.food_database import FoodDatabaseGenerator
from diet_generation.pipelines.diet_pipeline import DietPipeline
from diet_generation.user.types import ActivityLevel, DietType, Goal, Implementation, Sex, UserData


logging.basicConfig(level=logging.INFO)
app = typer.Typer(help="Endpoints related to meals plan (diet) generation")


@app.command("generate-meals-plan")
def generate_meals_plan(
    name: str = typer.Option(...),
    lastname: str = typer.Option(...),
    age: int = typer.Option(...),
    weight: float = typer.Option(..., help="Weight in kg"),
    height: float = typer.Option(..., help="Height in cm"),
    sex: Sex = typer.Option(...),
    activity_level: ActivityLevel = typer.Option(...),
    implementation: Implementation = typer.Option(...),
    goal: Goal = typer.Option(...),
    training_days: int = typer.Option(..., min=2, max=7),

    condition: Optional[str] = typer.Option(None),
    diet_type: Optional[DietType] = typer.Option("omnivore"),
    notes: Optional[str] = typer.Option(None),
):
    """Generates a meals plan for a user."""

    user_data = UserData(
        name=name,
        lastname=lastname,
        age=age,
        weight=weight,
        height=height,
        sex=sex,
        activity_level=activity_level,
        implementation=implementation,
        goal=goal,
        training_days=training_days,
        condition=condition,
        diet_type=diet_type,
        notes=notes,
    )

    DietPipeline(user_data).generate()


@app.command("generate-food-db")
def generate_food_database() -> None:
    """
    Endpoint to generate a .csv file containing a list
    of food items with their respective nutritional information.
    The data is retrieved from FatSecret's API, and it's saved in
    `data/databases/food.csv` (specified in settings file).
    """
    db_generator = FoodDatabaseGenerator()
    search_terms = ["cooked chicken breast", "egg", "oat", "banana", 
                        "cooked salmon", "cooked lentils", "milk", "cooked broccoli"]
    
    db_generator.generate(search_terms=search_terms)

