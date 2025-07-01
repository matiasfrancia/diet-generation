from dataclasses import dataclass
from enum import Enum
from typing import List, Literal, Optional


@dataclass(frozen=True)
class Macros:
    protein: int
    fat: int
    carbohydrates: int
    calories: int
    fiber: int


class Sex(str, Enum):
    male = "male"
    female = "female"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    low = "low"
    medium = "medium"
    high = "high"

class Implementation(str, Enum):
    gym = "gym"
    bodyweight = "bodyweight"

class Goal(str, Enum):
    weight_loss = "weight loss"
    gain_muscle = "gain muscle"
    body_recomposition = "body recomposition"

class DietType(str, Enum):
    omnivore = "omnivore"
    vegetarian = "vegetarian"
    vegan = "vegan"

@dataclass(frozen=True)
class UserData:
    name: str
    lastname: str
    age: int
    weight: float  # in kg
    height: float  # in cm

    sex: Sex
    activity_level: ActivityLevel
    implementation: Implementation
    goal: Goal
    training_days: int  # between 2 and 7

    condition: Optional[List[str]] = None  # e.g., 'diabetic', 'celiac', etc.
    diet_type: Optional[DietType] = DietType.omnivore
    notes: Optional[str] = None  # any additional info or constraints
