from __future__ import annotations
from pathlib import Path

import pandas as pd


class FoodVectorSpace:
    """
    Class to implement all the methods related to the vector's 
    space generation and storing. So the foods can be filtered 
    easily before giving them to the LLM.

    To create an instance of this class whether a food database
    or an already created vector space must be passed as argument.
    """

    def __init__(
        self, 
        *,
        food_db: pd.Dataframe = None,
        vector_space_path: Path = None
    ) -> "FoodVectorSpace":
        
        if food_db is None and vector_space_path is None:
            raise ValueError("To instantiate the vector space you must" \
                "pass to the constructor the food database or an already" \
                "created vector space.")
        
        if food_db:     # prioritizes the generation of a new vector space
            self.food_db: pd.DataFrame = food_db
        else:
            self.vector_space = self.load(vector_space_path)


    def vectorize_foods(self) -> None:
        """
        Converts all the foods in the database into vector space.
        It considers the allergens, whether it's vegan, vegetarian or 
        or neither, non-dairy or dairy, etc.

        This vector's space allows clustering and filtering for foods,
        making possible to give the LLM just a few foods to make the plan.
        """
        pass
    

    def vectorize_query(self, n: int = 15) -> pd.DataFrame:
        """
        Vectorizes the search query and returns a list of `n` foods that 
        best fit the query.
        """
        pass


    def save(self) -> None:
        """
        Saves the vector space to a file.
        """
        pass


    def load(self, vector_space_path: Path) -> None:
        """
        Loads the vector space from the given path.
        """

