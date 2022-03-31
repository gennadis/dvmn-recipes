from typing import Optional

from django.core.management.base import BaseCommand

from recipes.models import TelegramUser


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


class Command(BaseCommand):
    help = "Some basic test CRUD operations"

    def handle(self, *args, **kwargs):
        user_profile = {
            "id": 12345678901234,
            "username": "Test_Username_123",
            "first_name": "Test First Name 123",
            "last_name": "Test Last Name 123",
            "phone_number": "+7-999-123-45-00",
        }
        # new_user = create_new_user(user_profile)
        existing_user = get_existing_user(user_profile)
        print(existing_user)
        print(existing_user.phone_number)
