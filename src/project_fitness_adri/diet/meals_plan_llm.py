from __future__ import annotations
import json
import re
from typing import Any

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from project_fitness_adri.config.settings import Settings, get_settings
from project_fitness_adri.diet.food_database import FoodDatabaseGenerator
from project_fitness_adri.diet.types import MealsPlan, Meal, MealItem, FoodItem
from project_fitness_adri.user.types import Macros
from project_fitness_adri.user.user import User

import logging

from project_fitness_adri.utils.io import _load_food_database

log = logging.getLogger(__name__)
settings: Settings = get_settings()


def clean_json_from_llm(text: str) -> str:
    if text.strip().startswith("```"):
        # Extrae el contenido dentro del bloque
        text = re.sub(r"```(?:json)?\n(.*?)```", r"\1", text, flags=re.DOTALL).strip()
    return text


class MealsPlanLLM:
    """
    Generates a meals plan (diet) based on given parameters about the
    user. It does it by calling to an external LLM.
    """

    def __init__(self, user: User) -> "MealsPlanLLM":
        self.food_db = _load_food_database()
        self.user = user
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key=settings.openai_api_key)


    def _format_food_db(self) -> str:
        """
        Formats the food DB to a compact string for the LLM.
        """
        top_foods = self.food_db.head(15)
        formatted = [
            f"{row['name']} ({row['grams']}g): {row['kcal']} kcal, "
            f"{row['protein']}g protein, {row['carbs']}g carbs, {row['fat']}g fat"
            for _, row in top_foods.iterrows()
        ]
        return "\n".join(formatted)


    def _build_prompt(self, training_day: bool = True) -> str:
        macros = self.user.macros
        profile = f"{self.user.identifier}, {'entrena' if self.user.data.training_days > 0 else 'no entrena'}"

        prompt = f"""
            Eres un nutricionista experto en nutrición deportiva y planificación alimentaria.

            Crea un plan de alimentación diario dividido en 3 a 7 comidas ("Comida 1", "Comida 2", "Comida 3", "Comida 4", 
                  "Snack", "Post entreno", "Pre entreno") para el siguiente usuario en un día en que{'' if training_day else 'no'} entrena:
            - Nombre: {profile}
            - Objetivo: {self.user.data.goal}
            - Sexo: {self.user.data.sex}
            - Nivel de actividad: {self.user.data.activity_level}
            - Tipo de Dieta: {self.user.data.diet_type}
            - Restricciones médicas: {self.user.data.condition or "ninguna"}
            - Otras consideraciones: {self.user.data.notes}

            El plan debe cumplir estos macronutrientes:
            - Calorías: {macros.calories} kcal
            - Proteínas: {macros.protein} g
            - Grasas: {macros.fat} g
            - Carbohidratos: {macros.carbohydrates} g
            - Fibra: {macros.fiber} g

            **Reglas importantes:**
            - Solo entrega los nombres de los alimentos y la cantidad en gramos.
            - No des la información nutricional. Eso será calculado automáticamente luego.
            - Prefiere alimentos con alta calidad proteica, buena densidad de fibra y bajo costo relativo.
            - Puedes usar cualquier alimento que conozcas que se pueda conseguir Chile. Si no es muy común, asegúrate de usar su nombre lo más preciso posible.
            - El total diario no debe exceder los requerimientos de macronutrientes indicados.
            - No se pueden incluir alimentos que violen las Restricciones Médicas, el Tipo de Dieta, y se deben tener en cuenta las "Otras consideraciones".

            Entrega la respuesta en formato JSON con esta estructura:

            {{
            "user": "{self.user.identifier}",
            "training_day": {training_day},
            "meals": [
                {{
                "name": "Desayuno",
                "items": [
                    {{"food": "Avena", "amount": 50}},
                    {{"food": "Claras de huevo", "amount": 120}}
                ]
                }},
                ...
            ]
            }}
        """
        
        return prompt


    def _parse_llm_result(self, llm_result: str | list[str | dict]) -> MealsPlan:
        """
        Parses the LLM result (assumed to be a JSON-like dict) into MealsPlan.
        """
        log.info(f"Response type of LLM: {type(llm_result)}")
        if isinstance(llm_result, str):
            llm_result = json.loads(llm_result)

        meals = []
        for meal in llm_result["meals"]:
            items = []
            for item in meal["items"]:
                name = item["food"]
                amount = item["amount"]
                
                food_row = self.food_db[self.food_db["name"].str.lower() == name.lower()]

                if food_row.empty:
                    log.info(f"'{name}' not found in DB, trying to fetch from FatSecret")
                    success = self._try_add_food(name)
                    if not success:
                        log.warning(f"Failed to add food: {name}, skipping")
                        continue
                    self.food_db = _load_food_database()
                    food_row = self.food_db[self.food_db["name"].str.lower() == name.lower()]

                log.info(f"food_raw: {food_row}")
                food = FoodItem(**food_row.iloc[0].to_dict())
                items.append(MealItem(food=food, amount=amount))

            meals.append(Meal(name=meal["name"], items=items))

        return MealsPlan(
            user=llm_result["user"],
            training_day=llm_result["training_day"],
            macros=self.user.macros,
            meals=meals
        )


    def _try_add_food(self, food_name: str) -> bool:
        """
        Tries to add the food included in the plan that's not in the database.
        """
        generator = FoodDatabaseGenerator()
        return generator.add_new_food(food_name)


    def generate_with_openai(self) -> MealsPlan:
        """
        Generates a meals plan using the OpenAI LLM via LangChain.
        """
        prompt_text = self._build_prompt()
        prompt = ChatPromptTemplate.from_template("{prompt}")
        chain = prompt | self.llm

        result = chain.invoke({"prompt": prompt_text})
        raw_text: str | list[str | dict] = result.content
        log.info(f"The response from OpenAI was this one:")
        raw_text = clean_json_from_llm(raw_text)
        log.info(raw_text)

        try:
            return self._parse_llm_result(raw_text)
        except Exception as e:
            log.error(f"Error parsing LLM result: {e}")
            raise
