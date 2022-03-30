import json
import os

from django.core.management.base import BaseCommand

from . import recipes_raw_data

"""python manage.py loaddata mealtypes.json ingredients.json"""


FIXTURES_PATH = "./recipes/fixtures/"


def save_json(data: list[dict], filename: str) -> str:
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    return filename


def make_meal_types_fixtures(meal_type_names: list[str], filename: str) -> list[dict]:
    meal_types = []
    for count, name in enumerate(meal_type_names, start=1):
        meal_type = {
            "model": "recipes.mealtype",
            "pk": count,
            "fields": {"name": name},
        }
        meal_types.append(meal_type)

    save_json(data=meal_types, filename=filename)
    return meal_types


def make_ingredients_fixtures(
    ingredients_data: list[tuple], filename: str
) -> list[dict]:

    ingredients = []
    for count, ingredient_pair in enumerate(ingredients_data, start=1):
        name, unit = ingredient_pair
        ingredient = {
            "model": "recipes.ingredient",
            "pk": count,
            "fields": {
                "name": name,
                "unit": unit,
            },
        }
        ingredients.append(ingredient)

    save_json(data=ingredients, filename=filename)
    return ingredients


class Command(BaseCommand):
    help = "Fixtures generation command"

    def handle(self, *args, **kwargs):
        os.makedirs(FIXTURES_PATH, exist_ok=True)

        make_meal_types_fixtures(
            meal_type_names=recipes_raw_data.meal_types_names,
            filename=os.path.join(
                FIXTURES_PATH,
                "mealtypes.json",
            ),
        )

        make_ingredients_fixtures(
            ingredients_data=recipes_raw_data.ingredients_pairs,
            filename=os.path.join(FIXTURES_PATH, "ingredients.json"),
        )
