from __future__ import annotations
from project_fitness_adri.user.types import Macros, UserData


ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "low": 1.375,
    "medium": 1.55,
    "high": 1.725
}


class User:
    """
    Contains the user's information and methods to calculate
    the macros or the amount of training needed.
    """
    def __init__(self, data: UserData) -> "User":
        self.data: UserData = data
        self.identifier = self._generate_identifier()
        self.macros: Macros = self._calculate_macros()

    def _generate_identifier(self) -> str:
        identifier: str = self.data.name + self.data.lastname
        return identifier.lower()

    def _calculate_macros(self, method: str = "default") -> Macros:
        d = self.data

        # Base BMR (Mifflin-St Jeor)
        if method == "default" or method == "mifflin":
            if d.sex == "male":
                bmr = 10 * d.weight + 6.25 * d.height - 5 * d.age + 5
            else:
                bmr = 10 * d.weight + 6.25 * d.height - 5 * d.age - 161
        elif method == "harris":
            if d.sex == "male":
                bmr = 66.5 + (13.75 * d.weight) + (5.003 * d.height) - (6.75 * d.age)
            else:
                bmr = 655.1 + (9.563 * d.weight) + (1.850 * d.height) - (4.676 * d.age)
        else:
            raise ValueError(f"Unknown macro calculation method: {method}")

        # Factor de actividad
        activity_factor = ACTIVITY_FACTORS.get(d.activity_level)
        if activity_factor is None:
            raise ValueError(f"Unknown activity level: {d.activity_level}")

        tdee = bmr * activity_factor

        # Distribución estándar de macros
        grams_protein = d.weight * 2.0  # g/kg
        grams_fat = d.weight * 0.9      # g/kg

        kcal_from_protein = grams_protein * 4
        kcal_from_fat = grams_fat * 9

        kcal_remaining = tdee - kcal_from_protein - kcal_from_fat
        grams_carbs = max(kcal_remaining / 4, 0)  # prevent negative

        # Fibra estándar aproximada
        fiber = 15 + (d.weight // 10)

        return Macros(
            protein=round(grams_protein, 1),
            fat=round(grams_fat, 1),
            carbohydrates=round(grams_carbs, 1),
            calories=round(tdee, 0),
            fiber=round(fiber, 1)
        )
    
    def __str__(self) -> str:
        return (
            f"Daily consume of macronutrients for User: {self.identifier}\n"
            f"Data: {self.data}\n"
            f"Macros:\n"
            f"  - Protein: {self.macros.protein} g\n"
            f"  - Fat: {self.macros.fat} g\n"
            f"  - Carbs: {self.macros.carbohydrates} g\n"
            f"  - Calories: {self.macros.calories} kcal\n"
            f"  - Fiber: {self.macros.fiber} g"
        )
