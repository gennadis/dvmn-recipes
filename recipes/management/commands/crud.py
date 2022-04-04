import datetime
import random

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from recipes.models import (
    Allergy,
    Ingredient,
    MealType,
    PromoCode,
    Recipe,
    RecipeStep,
    SubscriptionPlan,
    TelegramUser,
    Subscription,
    RecipeIngredientAmount,
)


class SubscriptionIsOver(Exception):
    """Raised when the Subscription.end_date has come"""

    pass


class NoSuitableRecipeWasFound(Exception):
    """Raised when there's no suitable Recipe"""

    pass


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


@sync_to_async
def get_user(telegram_id: str) -> TelegramUser:
    return TelegramUser.objects.get(telegram_id=telegram_id)


@sync_to_async
def get_user_subscription_plan(name: str) -> SubscriptionPlan:
    return SubscriptionPlan.objects.get(name=name)


@sync_to_async
def get_user_subscriptions_list(user: TelegramUser) -> list[Subscription]:
    return [
        subscription for subscription in Subscription.objects.filter(owner=user).all()
    ]


@sync_to_async
def get_user_allergies_pk_list(allergies) -> list[Subscription.pk]:
    return [Allergy.objects.get(name=allergy_name).pk for allergy_name in allergies]


@sync_to_async
def create_user_subscription(subscription_details: dict) -> Subscription:
    subscription = Subscription.objects.create(
        name=subscription_details.get("name"),
        owner=subscription_details.get("owner"),
        plan=subscription_details.get("plan"),
        meal_type=subscription_details.get("meal_type"),
        servings=subscription_details.get("servings"),
        daily_meals_amount=subscription_details.get("daily_meals_amount"),
        start_date=subscription_details.get("start_date"),
        end_date=subscription_details.get("end_date"),
        promo_code=subscription_details.get("promo_code"),
        is_paid=subscription_details.get("is_paid"),
    )
    for allergy in subscription_details.get("allergies"):
        subscription.allergy.add(allergy)

    return subscription


@sync_to_async
def delete_user_subscription(
    user: TelegramUser, subscription_name: str
) -> Subscription:
    subscription_to_delete = Subscription.objects.filter(
        owner=user, name=subscription_name
    ).delete()
    return subscription_to_delete


@sync_to_async
def get_random_suitable_recipe(user: TelegramUser, menu: str) -> Recipe:
    subscription = Subscription.objects.get(owner=user, name=menu)

    if subscription.end_date < datetime.date.today():
        raise SubscriptionIsOver

    subscription_meal_type = subscription.meal_type
    subscription_allergies = subscription.allergy.all()
    subscription_banned_ingredients = Ingredient.objects.filter(
        allergy__in=subscription_allergies
    )

    suitable_recipes = Recipe.objects.filter(meal_type=subscription_meal_type).exclude(
        ingredients__in=subscription_banned_ingredients
    )
    if not suitable_recipes:
        raise NoSuitableRecipeWasFound

    return random.choice(suitable_recipes)


@sync_to_async
def get_recipe_ingredients(recipe: Recipe) -> dict:
    recipe_ingredients_amount = RecipeIngredientAmount.objects.filter(
        recipe=recipe.pk
    ).all()

    ingredients = {}
    for item in recipe_ingredients_amount:
        ingredients[item.ingredient.name] = f"{int(item.amount)} {item.ingredient.unit}"

    return ingredients


@sync_to_async
def get_recipe_steps(recipe: Recipe) -> list[dict]:
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


@sync_to_async
def get_promo_code(user_code: str) -> PromoCode:
    return PromoCode.objects.get(code=user_code.upper())


@sync_to_async
def get_subscription_plans_names() -> list[str]:
    return [
        subscription_plan.name for subscription_plan in SubscriptionPlan.objects.all()
    ]


@sync_to_async
def get_meal_types_names() -> list[str]:
    return [meal_type.name for meal_type in MealType.objects.all()]


class Command(BaseCommand):
    help = "Some basic test CRUD operations"

    def handle(self, *args, **kwargs):
        pass
