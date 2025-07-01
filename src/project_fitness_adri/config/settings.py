from pydantic import Field
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    
    # General
    package_name: str = "project_fitness_adri"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    databases_dir: Path = data_dir / "databases"
    output_dir: Path = data_dir / "output"

    # Templates
    templates_dir: Path = data_dir / "templates"
    diet_template_file: Path = templates_dir / "meals_generation_template.xlsx"
    exercise_template_file: Path = templates_dir / "exercise_generation_template.xlsx"

    # Diet Database
    food_database_api: str = "https://platform.fatsecret.com/rest/server.api"
    api_access_token_url: str = "https://oauth.fatsecret.com/connect/token"
    food_db_client_id: str = Field(..., env="FOOD_DB_CLIENT_ID")
    food_db_client_secret: str = Field(..., env="FOOD_DB_CLIENT_SECRET")
    food_database_file: Path = databases_dir / "food.csv"
    
    # Exercise Database
    exercises_database_file: Path = databases_dir / "exercises.csv"

    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
