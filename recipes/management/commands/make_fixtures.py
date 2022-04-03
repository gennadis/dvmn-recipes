import json
import os

from django.core.management.base import BaseCommand


FIXTURES_PATH = "./recipes/fixtures/"

MEAL_TYPES = [
    "Классическое",
    "Низкоуглеводное",
    "Веганское",
    "Кето",
]
ALLERGIES = [
    "Морепродукты",
    "Мясо",
    "Зерновые",
    "Мёд",
    "Орехи",
    "Молоко",
]
PROMO_CODES = [
    "ПРИВЕТ",
    "ПОЕХАЛИ",
    "РЕЦЕПТЫ",
]


def save_json(data: list[dict], filename: str) -> str:
    with open(filename, "w") as file:
        json.dump(
            obj=data,
            fp=file,
            indent=4,
            ensure_ascii=False,
        )

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


def make_allergies_fixtures(allergies_names: list[str], filename: str) -> list[dict]:
    allergies = []
    for count, name in enumerate(allergies_names, start=1):
        meal_type = {
            "model": "recipes.allergy",
            "pk": count,
            "fields": {
                "name": name,
            },
        }
        allergies.append(meal_type)

    save_json(data=allergies, filename=filename)
    return allergies


def make_promo_code_fixtures(promo_codes_list: list[str], filename: str) -> list[dict]:
    promo_codes = []
    for count, code in enumerate(promo_codes_list, start=1):
        promo_code = {
            "model": "recipes.promocode",
            "pk": count,
            "fields": {
                "code": code,
                "discount": count * 10,
                "valid_thru": "2030-10-10",
            },
        }
        promo_codes.append(promo_code)

    save_json(data=promo_codes, filename=filename)
    return promo_codes


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
            meal_type_names=MEAL_TYPES,
            filename=os.path.join(
                FIXTURES_PATH,
                "mealtypes.json",
            ),
        )
        make_allergies_fixtures(
            allergies_names=ALLERGIES,
            filename=os.path.join(FIXTURES_PATH, "allergies.json"),
        )
        make_promo_code_fixtures(
            promo_codes_list=PROMO_CODES,
            filename=os.path.join(FIXTURES_PATH, "promocodes.json"),
        )
