import random
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


from django.core.management.base import BaseCommand

from recipes.models import (
    Allergy,
    Ingredient,
    MealType,
    Recipe,
    TelegramUser,
    Subscription,
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


def get_existing_user(user_profile: dict) -> Optional[TelegramUser]:
    try:
        telegram_id = user_profile.get("id")
        existing_user = TelegramUser.objects.get(telegram_id=telegram_id)
        return existing_user

    except TelegramUser.DoesNotExist:
        return None


def get_subscriptions(user_telegram_id: str) -> Subscription:
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    subscriptions = Subscription.objects.filter(owner=user).all()
    return subscriptions


def save_subscription(user_telegram_id: str, subscription_details: dict):
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    user_meal_type = MealType.objects.get(name=subscription_details.get("meal_type"))
    user_allergies = [
        Allergy.objects.get(name=allergy_name).pk
        for allergy_name in subscription_details.get("allergies")
    ]

    subscription = Subscription.objects.create(
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


class Command(BaseCommand):
    help = "Some basic test CRUD operations"

    def handle(self, *args, **kwargs):
        user_telegram_id = "12345"
        user_subscriptions = get_subscriptions(user_telegram_id=user_telegram_id)
        print(user_subscriptions)
        # subscription_details = {
        #     "meal_type": "keto",
        #     "servings": 1,
        #     "daily_meals_amount": 3,
        #     "allergies": ["milk", "nuts", "honey"],
        #     "start_date": datetime.now(),
        #     "end_date": datetime.now() + relativedelta(month=1),
        #     "promo_code": "EMPTY",
        #     "is_paid": True,
        # }
        # subscription = save_subscription(
        #     user_telegram_id=user_telegram_id,
        #     subscription_details=subscription_details,
        # )
        # print(subscription)
