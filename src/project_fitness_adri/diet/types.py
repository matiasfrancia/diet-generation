from dataclasses import dataclass
from typing import List, Literal, Optional

from project_fitness_adri.user.types import Macros

@dataclass(frozen=True)
class FoodItem:
    name: str
    serving_id: Optional[int]
    serving_description: str
    grams: float  # metric_serving_amount
    kcal: float
    protein: float
    carbs: float
    fat: float

    # Optional nutritional info (None means unavailable)
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None

    cholesterol: Optional[float] = None  # mg
    sodium: Optional[float] = None       # mg
    potassium: Optional[float] = None    # mg
    calcium: Optional[float] = None      # mg
    iron: Optional[float] = None         # mg
    vitamin_a: Optional[float] = None    # µg
    vitamin_c: Optional[float] = None    # mg
    vitamin_d: Optional[float] = None    # µg
    added_sugars: Optional[float] = None

    def macros_per_gram(self) -> dict:
        return {
            "kcal": self.kcal / self.grams if self.grams else 0,
            "protein": self.protein / self.grams if self.grams else 0,
            "carbs": self.carbs / self.grams if self.grams else 0,
            "fat": self.fat / self.grams if self.grams else 0,
        }

@dataclass()
class MealItem:
    food: FoodItem
    amount: int # in grams


@dataclass(frozen=True)
class Meal:
    name: Literal["Comida 1", "Comida 2", "Comida 3", "Comida 4", 
                  "Snack", "Post entreno", "Pre entreno"]
    items: List[MealItem]


@dataclass(frozen=True)
class MealsPlan:
    user: str
    training_day: bool  # True for training days, False for rest days
    macros: Macros
    meals: List[Meal]
