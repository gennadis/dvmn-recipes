from typing import Optional

from django.core.management.base import BaseCommand

from recipes.models import TelegramUser, Subscription


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


def get_subscription(user_telegram_id: str) -> Subscription:
    user = TelegramUser.objects.get(telegram_id=user_telegram_id)
    subscription = Subscription.objects.get(owner=user)
    return subscription


class Command(BaseCommand):
    help = "Some basic test CRUD operations"

    def handle(self, *args, **kwargs):
        user_telegram_id = "12345"
        subscription = get_subscription(user_telegram_id=user_telegram_id)
        print(subscription)
        print(subscription.allergy)
        print(subscription.daily_meals_amount)
