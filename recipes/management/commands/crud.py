import random
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand

from recipes.models import (
    Allergy,
    Ingredient,
    MealType,
    PromoCode,
    Recipe,
    RecipeStep,
    TelegramUser,
    Subscription,
    RecipeIngredientAmount,
)

from asgiref.sync import sync_to_async


@sync_to_async
def create_new_user(user_profile: dict) -> TelegramUser:
    new_user = TelegramUser.objects.create(
        telegram_id=user_profile.get("id"),
        telegram_username=user_profile.get("username"),
        first_name=user_profile.get("first_name"),
        last_name=user_profile.get("last_name"),
        phone_number=user_profile.get("phone_number"),
    )
    new_user.save()

    return new_user


def check_user_exist(user_profile: dict) -> Optional[TelegramUser]:
    try:
        telegram_id = user_profile.get("id")
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        return True

    except TelegramUser.DoesNotExist:
        return False


@sync_to_async
def get_existing_user(user_profile: dict) -> Optional[TelegramUser]:
    try:
        telegram_id = user_profile.get("id")
        existing_user = TelegramUser.objects.get(telegram_id=telegram_id)
        return existing_user

    except TelegramUser.DoesNotExist:
        return None


# @sync_to_async
# def get_subscriptions(user_telegram_id: str) -> Subscription:
#     user = TelegramUser.objects.get(telegram_id=user_telegram_id)
#     subscriptions = Subscription.objects.filter(owner=user).all()
#     return subscriptions


def get_subscriptions(user: TelegramUser):
    return list(Subscription.objects.filter(owner=user).all())


@sync_to_async
def save_subscription(user_telegram_id: str, subscription_details: dict):
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    user_meal_type = MealType.objects.get(name=subscription_details.get("meal_type"))
    user_allergies = [
        Allergy.objects.get(name=allergy_name).pk
        for allergy_name in subscription_details.get("allergies")
    ]

    subscription = Subscription.objects.create(
        name=subscription_details.get("name"),
        owner=user,
        meal_type=user_meal_type,
        servings=subscription_details.get("servings"),
        daily_meals_amount=subscription_details.get("daily_meals_amount"),
        start_date=subscription_details.get("start_date"),
        end_date=subscription_details.get("end_date"),
        promo_code=subscription_details.get("promo_code"),
        is_paid=subscription_details.get("is_paid"),
    )
    for allergy in user_allergies:
        subscription.allergy.add(allergy)

    return subscription


def get_random_allowed_recipe(user_telegram_id: str) -> Recipe:
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    user_allergies = Subscription.objects.get(owner=user).allergy.all()
    user_banned_ingredients = Ingredient.objects.filter(allergy__in=user_allergies)

    allowed_recipes = Recipe.objects.exclude(ingredients__in=user_banned_ingredients)
    return random.choice(allowed_recipes)


def get_recipe_ingredients(user_telegram_id: str, recipe: Recipe) -> dict:
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    recipe_ingredients_amount = RecipeIngredientAmount.objects.filter(
        recipe=recipe.pk
    ).all()

    ingredients = {}
    for item in recipe_ingredients_amount:
        ingredients[item.ingredient.name] = f"{int(item.amount)} {item.ingredient.unit}"

    return ingredients


def get_recipe_steps(user_telegram_id: str, recipe: Recipe) -> dict:
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    recipe_steps = RecipeStep.objects.filter(step_recipe=recipe.pk)
    steps = []
    for step in recipe_steps:
        steps.append(
            {
                "order": step.order,
                "instruction": step.instruction,
                "image_url": step.image_url,
            }
        )

    return steps


def validate_promo_code(user_code: str):
    try:
        promo_code = PromoCode.objects.get(code=user_code.upper())
        return promo_code

    except PromoCode.DoesNotExist:
        return False


@sync_to_async
def get_allergies() -> list[str]:
    return [allergy.name for allergy in Allergy.objects.all()]


@sync_to_async
def get_meal_types() -> list[str]:
    return [meal_type.name for meal_type in MealType.objects.all()]


class Command(BaseCommand):
    help = "Some basic test CRUD operations"

    def handle(self, *args, **kwargs):
        allergies = get_allergies()
        meal_types = get_meal_types()
        print(allergies)
        print(meal_types)

        # user_telegram_id = "12345"
        # random_recipe = get_random_allowed_recipe(user_telegram_id)
        # ingredients = get_recipe_ingredients(user_telegram_id, random_recipe)
        # steps = get_recipe_steps(user_telegram_id, random_recipe)

        # print(f"Название: {random_recipe.name}")
        # print(f"Фото: {random_recipe.image_url}")
        # print("____________")
        # print("Ингредиенты:")
        # for name, amount in ingredients.items():
        #     print(name, amount)
        # print("____________")
        # print("Шаги:")
        # print()
        # for step in steps:
        #     print(step["image_url"])
        #     print(f"Шаг {step['order']}: {step['instruction']}")
        #     print()
