
import logging
from pathlib import Path
import pandas as pd
from project_fitness_adri.config.settings import get_settings
from project_fitness_adri.diet.food_database import FoodDatabaseGenerator
from project_fitness_adri.diet.meals_plan import MealsPlanGenerator
from project_fitness_adri.diet.types import MealsPlan
from project_fitness_adri.user.types import UserData
from project_fitness_adri.user.user import User


settings = get_settings()
log = logging.getLogger(__name__)


class DietPipeline:
    """
    Implements a pipeline that comprehends the steps from
    parsing the user/client information given by the Google Form,
    to generate a basic meals plan in excel format.

    The excel is an editable file, that can be later modified based 
    on the needs of the user, depending on the willing of the coach.
    """
    def __init__(self, user_data: UserData) -> None:
        # creates user object that contains the macros that it has to consume
        self.user = User(user_data)
        log.info(f"User data: {self.user}")
        # creates a meal plan based on the user's information and macros
        self.plan_generator = MealsPlanGenerator(self.user)


    def generate(self) -> MealsPlan:
        meals_plan: MealsPlan = self.plan_generator.generate()
        return meals_plan


    def save_meals_plan_to_excel(self) -> None:
        """
        Saves the meals plan and the user's data into an excel file.
        The generated file is editable and contains the same workflow as 
        the templated already used by the coach.
        """
        template_path: Path = settings.diet_template_file
        output_path: Path = settings.output_dir / self.user.identifier
        log.info(f"The meals plan template will be saved to the following output path: {output_path}")
        pass
