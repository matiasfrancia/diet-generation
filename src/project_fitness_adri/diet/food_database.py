from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import pandas as pd
from dataclasses import asdict
from pyfatsecret import Fatsecret

from project_fitness_adri.config.settings import get_settings
from project_fitness_adri.diet.types import FoodItem

log = logging.getLogger(__name__)


class FoodDatabaseGenerator:
    def __init__(self):
        settings = get_settings()
        self.fs = Fatsecret(
            client_id=settings.food_db_client_id,
            client_secret=settings.food_db_client_secret
        )
        self.db_path = settings.food_database_file


    def _try_float(self, value: str | None) -> Optional[float]:
        """
        Tries to convert the attribute to float, if it exists.
        Else, it returns None, making easier to differentiate when a
        value is 0, or when it does not exist in the database.
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


    def _parse_food_item(self, food_data: dict) -> FoodItem | None:
        """
        Parses the food data returned by food_get_v4 into a FoodItem.
        """
        name = food_data["food_name"]
        servings = food_data["servings"]["serving"]

        if not servings:
            return None

        if isinstance(servings, list):
            serving = next((s for s in servings if s.get("is_default") == 1), servings[0])
        else:
            serving = servings

        try:
            # TODO: implement a way to recognize and save the allergens too, and whether it's
            # vegan, vegetarian or neither
            return FoodItem(
                name=name,
                serving_id=int(serving.get("serving_id")) if serving.get("serving_id") else None,
                serving_description=serving.get("serving_description", ""),
                grams=float(serving.get("metric_serving_amount", 100.0)),
                kcal=float(serving.get("calories", 0.0)),
                protein=float(serving.get("protein", 0.0)),
                carbs=float(serving.get("carbohydrate", 0.0)),
                fat=float(serving.get("fat", 0.0)),

                fiber=self._try_float(serving.get("fiber")),
                sugar=self._try_float(serving.get("sugar")),
                saturated_fat=self._try_float(serving.get("saturated_fat")),
                trans_fat=self._try_float(serving.get("trans_fat")),
                monounsaturated_fat=self._try_float(serving.get("monounsaturated_fat")),
                polyunsaturated_fat=self._try_float(serving.get("polyunsaturated_fat")),

                cholesterol=self._try_float(serving.get("cholesterol")),
                sodium=self._try_float(serving.get("sodium")),
                potassium=self._try_float(serving.get("potassium")),
                calcium=self._try_float(serving.get("calcium")),
                iron=self._try_float(serving.get("iron")),
                vitamin_a=self._try_float(serving.get("vitamin_a")),
                vitamin_c=self._try_float(serving.get("vitamin_c")),
                vitamin_d=self._try_float(serving.get("vitamin_d")),
                added_sugars=self._try_float(serving.get("added_sugars")),
            )
        except Exception as e:
            log.warning(f"Failed to parse food item: {e}")
            return None
        
    
    def _search_food(self, food_name: str) -> FoodItem | None:
        """
        Tries to obtain the best match for the food we're looking for
        in the database of FatSecret.

        It returns the food item if it founds it, else None.
        """
        try:
            search_results = self.fs.foods.foods_search(food_name)
            food_list = search_results.get("foods", {}).get("food", [])
            log.info(f"Food list: {search_results.get('foods')}")

            for item in food_list:
                food_id = item.get("food_id")
                detail = self.fs.foods.food_get_v4(food_id)
                food_dict: Dict[str, Any] = detail.get("food")
                food_type: str = detail.get("food_type")
                log.info(f"Food type: {food_type}")
                
                # skip non-generic foods
                if food_type == "Brand": 
                    log.info(f"Food type is {food_type}")
                    continue
                if not food_dict:
                    log.info(f"Detail of not found item: {detail}")
                    log.info(f"Detail of not found item: {detail}")
                    log.info(f"Detail of not found item: {detail}")
                    log.info(f"Detail of not found item: {detail}")
                    continue

                food_item: FoodItem | None = self._parse_food_item(food_dict)

                if food_item is not None:
                    log.info(f"Parsed: {food_item}")
                    return food_item

        except Exception as e:
            log.warning(f"Failed to retrieve or parse foods for '{food_name}': {e}")
            return None


    def generate(self, search_terms: List[str]) -> None:
        """
        Generates and saves a food database using FatSecret API v4.
        The database is saved in a .csv file in the path specified in settings.
        """
        all_foods: List[FoodItem] = []

        for term in search_terms:
            log.info(f"Searching for: {term}")
            food_item: FoodItem | None = self._search_food(term)

            if food_item is not None:
                all_foods.append(food_item)
            else:
                log.warning(f"The food information for {term} wasn't found.")

        df = pd.DataFrame(asdict(food) for food in all_foods)
        df.to_csv(self.db_path, index=False)
        log.info(f"Saved {len(df)} items to {self.db_path}")


    def add_new_food(self, name: str) -> bool:
        """
        Receives a new food name, searchs it and adds its information
        to the database, if it isn't already there. Returns whether the
        food item is now in the database, or not.
        """
        df_food = pd.read_csv(self.db_path)

        # checks whether the food is already in the db or not
        if df_food["name"].str.lower().isin([name.lower()]).any():
            log.warning(f"The food element is already in the database")
            return True
        
        food_item: FoodItem | None = self._search_food(name)
        if food_item is None:
            log.warning(f"The food item wasn't found in FatSecret's API, " \
                        f"so the LLM has to be called again and exclude it, " \
                        f"or the food must be replaced.")
            return False

        new_row = pd.DataFrame([asdict(food_item)])
        df_food = pd.concat([df_food, new_row], ignore_index=True)
        df_food.to_csv(self.db_path, index=False)
        return True
