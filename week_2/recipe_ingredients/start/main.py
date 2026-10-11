from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from pprint import pprint
import os
import instructor

class Ingredient(BaseModel):
    amount: float = Field(description = "A float representing the quantity of the ingredient")
    unit: str = Field(description = "A string representing the unit of measurement (e.g., 'cups', 'tablespoons', 'grams')")
    name: str = Field(description = "A string representing the name of the ingredient")

class Recipe(BaseModel):
    """
    Use this model when working with complete cooking recipes.
    """
    title: str = Field ( description = "Name of the recipe")
    ingredients: List [Ingredient] = Field ( description="List of structured ingredients needed for the recipe")
    instructions: List [str] = Field ( description="Step-by-step instructions to prepare the recipe")

def get_recipe_from_text(recipe_text: str) -> Recipe:
    """
    Convert recipe text into a structured Recipe object using Gemini via Instructor.
    """
    # Initialize the instructor client for Gemini (plug in your key)
    client = instructor.from_provider("google/gemini-3-flash-preview", api_key = os.environ["GEMINI_API_KEY"])

    # Make the API call using instructor's standardized format
    response = client.chat.completions.create(
        response_model=Recipe,
        messages=[
            {"role": "user", "content": f"Convert this recipe into the specified format:\n\n{recipe_text}"}
        ]
    )
    
    return response
  
# Example usage
if __name__ == "__main__":
    # Read recipe text from file
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    recipe_path = os.path.join(script_dir, "mac_and_cheese_recipe.txt")
    with open(recipe_path, "r") as file:
        recipe_text = file.read()

    # Get structured recipe
    recipe = get_recipe_from_text(recipe_text)
    
    # Print results
    pprint(recipe.ingredients[0])
    # pprint(recipe) # to see the whole object
