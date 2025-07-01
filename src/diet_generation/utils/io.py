import pandas as pd

from diet_generation.config.settings import Settings, get_settings


settings: Settings = get_settings()


def _load_food_database() -> pd.DataFrame:
    """
    Loads the csv file with food's data by reading the file in settings.
    """
    if not settings.food_database_file.exists():
        raise ValueError("The food database file wans't found. " \
            "Confirm that the file was generated first by calling " \
            "the endpoint `generate-food-database`.")
            
    return pd.read_csv(settings.food_database_file)