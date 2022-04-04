import datetime
import re
import time
import uuid

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import PreCheckoutQuery, ParseMode, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes
from aiogram.types.labeled_price import LabeledPrice
from asgiref.sync import sync_to_async
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from environs import Env
from recipes.management.commands.crud import (create_new_user, get_meal_types,
                                              get_promo_code,
                                              get_random_allowed_recipe,
                                              get_recipe_ingredients,
                                              get_recipe_steps,
                                              get_subscription_plan,
                                              get_subscription_plans_names,
                                              get_subscriptions,
                                              get_telegram_user,
                                              make_user_allergies_list,
                                              save_subscription,
                                              delete_subscription,
                                              SubscriptionIsOver,
                                              NoSuitableRecipeWasFound)
from recipes.management.commands.keyboards import (ASK_FOR_PHONE_KEYBOARD,
                                                   MAIN_KEYBOARD,
                                                   make_digit_keyboard,
                                                   make_dynamic_keyboard,
                                                   make_keyboard)
from recipes.models import (Allergy,
                            MealType,
                            PromoCode,
                            Recipe,
                            TelegramUser,
                            Subscription as Subscription_model)


class GetRecipe(StatesGroup):
    menu = State()
    expired = State()


class UserProfile(StatesGroup):
    id = State()
    username = State()
    first_name = State()
    last_name = State()
    phone_number = State()


class Subscription(StatesGroup):
    name = State()
    type_menu = State()
    persons = State()
    eatings = State()
    allergens = State()
    period = State()
    promo = State()
    payment_id = State()


def get_subscriptions_names(subscriptions: Subscription_model) -> list:
    return [subscription.name for subscription in subscriptions]


@sync_to_async
def get_allergens_objects():
    return list(Allergy.objects.all())


class Command(BaseCommand):
    help = "Start Telegram bot"

    def handle(self, *args, **kwargs):

        env = Env()
        env.read_env()

        bot_init = Bot(
            token=env.str("BOT_TOKEN"),
            parse_mode=ParseMode.HTML
        )
        storage = MemoryStorage()
        bot = Dispatcher(bot_init, storage=storage)

        @bot.message_handler(commands="start")
        async def hello(message: Message):
            user_id = message.from_user.id
            try:
                user_data = await get_telegram_user(telegram_id=user_id)
                await message.answer(
                    f"{user_data.first_name}, hello again!",
                    reply_markup=MAIN_KEYBOARD
                )
            except TelegramUser.DoesNotExist:
                await message.answer("Здравствуйте!\n\n"
                                     "Как Вас зовут?\n(введите имя)")
                await UserProfile.first_name.set()

        @bot.message_handler(commands="main", state="*")
        @bot.message_handler(
            lambda message: message.text == "Вернуться на главную", state="*"
        )
        async def return_to_main(message: Message, state: FSMContext):
            await state.finish()
            await message.reply(
                "Возвращаемся на главную",
                reply_markup=MAIN_KEYBOARD
            )

        @bot.message_handler(state=UserProfile.first_name)
        async def get_user_name(message: Message, state: FSMContext):
            await state.update_data(id=message.from_user.id)
            await state.update_data(username=message.from_user.username)
            await state.update_data(first_name=message.text)
            await message.answer("Спасибо.\nНапишите еще фамилию, пожалуйста")
            await UserProfile.last_name.set()

        @bot.message_handler(state=UserProfile.last_name)
        async def get_user_surname(message: Message, state: FSMContext):
            await state.update_data(last_name=message.text)
            await message.answer(
                ("Супер!\n\nОсталось отправить "
                 "номер телефона для управления подписками."),
                reply_markup=ASK_FOR_PHONE_KEYBOARD,
            )
            await UserProfile.phone_number.set()

        @bot.message_handler(
            state=UserProfile.phone_number,
            content_types=ContentTypes.CONTACT
        )
        async def get_user_phone(message: Message, state: FSMContext):
            await state.update_data(phone_number=message.contact.phone_number)
            user_data = await state.get_data()
            await create_new_user(user_data)
            await state.finish()
            await message.answer(
                "Отлично, ваш профиль сохранен!", reply_markup=MAIN_KEYBOARD
            )

        @bot.message_handler(lambda message: message.text == "Мои подписки")
        async def get_user_subscriptions(message: Message):
            user = await get_telegram_user(telegram_id=message.from_user.id)
            subscriptions = await get_subscriptions(user)
            subscriptions_names = get_subscriptions_names(subscriptions)

            if subscriptions_names:
                await message.answer(
                    "Выберите вашу подписку из списка внизу",
                    reply_markup=make_keyboard(
                        buttons=subscriptions_names,
                        row_width=1
                    )
                )
                await GetRecipe.menu.set()
            else:
                await message.answer(
                    "Похоже что у вас нет подписок.\nХотите создать первую?",
                    reply_markup=make_keyboard(["Создать подписку"], 1),
                )

        @bot.message_handler(state=GetRecipe.menu)
        async def get_recipe_from_subscription(message: Message,
                                               state: FSMContext):
            user = await get_telegram_user(telegram_id=message.from_user.id)
            await state.update_data(menu=message.text)
            try:
                random_recipe = await get_random_allowed_recipe(
                    user=user,
                    menu=message.text
                )

                keyboard = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton(
                        text='Необходимые ингредиенты',
                        callback_data='get_ingredient'
                    ),
                    InlineKeyboardButton(
                        text='Рецепт пошагово',
                        callback_data='step_by_step'
                    ),
                    InlineKeyboardButton(
                        text='Выбрать другое блюдо',
                        callback_data='other_recipe'
                    )
                )
                await message.answer(
                    'Как скажете. Выбираю рецепт..',
                    reply_markup=MAIN_KEYBOARD
                )
                await message.answer_photo(
                    photo=random_recipe.image_url,
                    caption=random_recipe.name,
                    reply_markup=keyboard
                )
                await state.finish()
            except SubscriptionIsOver:
                await message.answer(
                    ('Похоже, что срок действия вашей подписки закончился.\n\n'
                     'Хотите продлить?'),
                    reply_markup=make_keyboard(
                        ['Продлить подписку', 'Удалить подписку'],
                        row_width=1
                    )
                )
                await GetRecipe.expired.set()
            except NoSuitableRecipeWasFound:
                await message.answer(
                    ('Вы знаете, не смог найти рецепт удовлетворяющий вашему'
                     'запросу.\n\n'
                     'Я сообщил администратору, он все проверит и починит'),
                    reply_markup=MAIN_KEYBOARD
                )
                await state.finish()

        @bot.message_handler(state=GetRecipe.expired)
        async def expired_subscription(message: Message, state: FSMContext):
            user_id = message.from_user.id
            state_data = await state.get_data()
            if message.text == 'Продлить подписку':
                await message.answer(
                    'Для продления свяжитесь с администратором бота.',
                    reply_markup=MAIN_KEYBOARD
                )
            elif message.text == 'Удалить подписку':
                user = await get_telegram_user(telegram_id=user_id)
                await delete_subscription(user, state_data['menu'])
                await message.answer(
                    'Подписка удалена.',
                    reply_markup=MAIN_KEYBOARD
                )
            await state.finish()

        @bot.callback_query_handler(lambda callback:
                                    callback.data == 'other_recipe')
        async def other_recipe(callback_query: CallbackQuery):
            user = await get_telegram_user(
                telegram_id=callback_query.from_user.id
            )
            subscriptions = await get_subscriptions(user)
            subscriptions_names = get_subscriptions_names(subscriptions)
            await bot_init.send_message(
                chat_id=callback_query.from_user.id,
                text="Напомните пожалуйста для какого меню подобрать блюдо.",
                reply_markup=make_keyboard(subscriptions_names, 1)
            )
            await GetRecipe.menu.set()

        @bot.callback_query_handler(lambda callback:
                                    callback.data == 'get_ingredient')
        async def get_ingredients(callback_query: CallbackQuery):
            recipe = await sync_to_async(Recipe.objects.get)(
                name=callback_query.message.caption
            )
            recipe_ingredients = await get_recipe_ingredients(recipe=recipe)
            ingredient_message = 'ИНГРЕДИЕНТЫ\n'
            for ingredient, how_much in recipe_ingredients.items():
                ingredient_message += f'\n{ingredient}: {how_much}'
            await bot_init.send_message(
                chat_id=callback_query.from_user.id,
                text=ingredient_message,
                reply_markup=MAIN_KEYBOARD
            )

        @bot.callback_query_handler(lambda callback:
                                    callback.data == 'step_by_step')
        async def step_by_step(callback_query: CallbackQuery):
            recipe = await sync_to_async(Recipe.objects.get)(
                name=callback_query.message.caption
            )
            recipe_steps = await get_recipe_steps(recipe=recipe)
            for step in recipe_steps:
                time.sleep(0.5)
                await bot_init.send_photo(
                    chat_id=callback_query.from_user.id,
                    photo=step["image_url"],
                    caption=step["instruction"]
                )
            await bot_init.send_message(
                chat_id=callback_query.from_user.id,
                text='Приятного аппетита!'
            )
            await bot_init.send_message(
                chat_id=callback_query.from_user.id,
                text='😋',
                reply_markup=MAIN_KEYBOARD
            )

        @bot.message_handler(lambda message:
                             message.text == "Создать подписку")
        async def create_subscription(message: Message):
            await message.answer(
                "Как назовем меню?",
                reply_markup=make_keyboard(row_width=1)
            )
            await Subscription.name.set()

        @bot.message_handler(state=Subscription.name)
        async def get_subscription_name(message: Message,
                                        state: FSMContext):
            await state.update_data(name=message.text)
            meal_types = await get_meal_types()
            await message.answer(
                "Укажите тип меню.", reply_markup=make_keyboard(meal_types, 1)
            )
            await Subscription.type_menu.set()

        @bot.message_handler(state=Subscription.type_menu)
        async def get_type_menu(message: Message, state: FSMContext):
            await state.update_data(type_menu=message.text)
            await message.answer(
                "Отлично, укажите количество персон",
                reply_markup=make_digit_keyboard()
            )
            await Subscription.persons.set()

        @bot.message_handler(state=Subscription.persons)
        async def get_number_of_persons(message: Message,
                                        state: FSMContext):
            await state.update_data(persons=message.text)
            await message.answer(
                "Отлично, укажите количество приемов пищи",
                reply_markup=make_digit_keyboard(),
            )
            await Subscription.eatings.set()

        @bot.message_handler(state=Subscription.eatings)
        async def get_number_of_eatings(message: Message,
                                        state: FSMContext):
            global allergens
            allergens = [x.name for x in await get_allergens_objects()]

            await state.update_data(eatings=message.text)
            await message.answer(
                "Отлично, укажите аллергены - продукты которых не должно быть",
                reply_markup=make_dynamic_keyboard(
                    allergens, [], extended_buttons=["Аллергенов нет"]
                ),
            )
            await Subscription.allergens.set()

        @bot.message_handler(state=Subscription.allergens)
        async def get_allergens(message: Message, state: FSMContext):
            state_data = await state.get_data()
            if message.text in ["Готово", "Аллергенов нет"]:
                if state_data.get("allergens") is None:
                    await state.update_data(allergens=[])
                subscription_plans_names = await get_subscription_plans_names()
                await message.answer(
                    "Отлично, выберите период подписки",
                    reply_markup=make_keyboard(subscription_plans_names),
                )
                await Subscription.period.set()
            elif re.split("Добавить |Удалить ", message.text)[1] in allergens:
                allergen = re.split("Добавить |Удалить ", message.text)[1]
                try:

                    user_allergens = state_data.get("allergens")
                    if allergen not in user_allergens:
                        user_allergens.append(allergen)
                    else:
                        user_allergens.remove(allergen)
                except TypeError:
                    user_allergens = [f"{allergen}"]

                await state.update_data(allergens=user_allergens)
                await message.answer(
                    "Добавим еще один?",
                    reply_markup=make_dynamic_keyboard(
                        allergens, user_allergens, extended_buttons=["Готово"]
                    ),
                )
                await Subscription.allergens.set()

        @bot.message_handler(state=Subscription.period)
        async def get_subscription_period(message: Message,
                                          state: FSMContext):
            await state.update_data(period=message.text)
            await message.answer(
                "Введите промокод", reply_markup=make_keyboard(["Пропустить"])
            )
            await Subscription.promo.set()

        @bot.message_handler(state=Subscription.promo)
        async def get_promo(message: Message, state: FSMContext):
            plan = await state.get_data()
            subscription_plan = await get_subscription_plan(
                name=plan.get("period")
            )

            currency = subscription_plan.currency
            price = subscription_plan.price

            if message.text == "Пропустить":
                await state.update_data(promo=None)
                benefit_text = ""
            else:
                try:
                    promo_code = await get_promo_code(user_code=message.text)
                    await state.update_data(promo=promo_code)
                    benefit = round(price * promo_code.discount * 0.01)
                    price = price - benefit
                    benefit_text = f"Вы сэкономили {benefit} {currency}\n"

                except PromoCode.DoesNotExist:
                    await message.reply(
                        ("Такого промокода нет.\n\n"
                         "Введите корректный или пропустите шаг."),
                        reply_markup=make_keyboard(["Пропустить"]),
                    )
                    await Subscription.promo.set()
                    return

            await message.answer(
                (
                    f"Ура, подписка сформирована.\n\nСтоимость подписки = "
                    f"{price} {currency}\n{benefit_text}\n"
                    f"Осталось ее оплатить и можно идти за продуктами."
                ),
                reply_markup=make_keyboard([]),
            )

            payment_id = uuid.uuid1
            await state.update_data(payment_id=payment_id)

            await bot_init.send_invoice(
                chat_id=message.from_user.id,
                title="Счет на оплату",
                description=f'Подписка "{subscription_plan.name}"',
                payload=str(payment_id),
                provider_token=env.str("SBER_TOKEN"),
                currency="RUB",
                prices=[LabeledPrice("ooops", price * 100)],
            )

        @bot.pre_checkout_query_handler(lambda query: True, state="*")
        async def pre_checkout_answer(pre_checkout_query: PreCheckoutQuery):
            await bot_init.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id,
                ok=True,
                error_message="FUCK!",
            )

        @bot.message_handler(
            content_types=ContentTypes.SUCCESSFUL_PAYMENT, state="*"
        )
        async def got_payment(message: Message, state: FSMContext):
            state_data = await state.get_data()
            user = await get_telegram_user(telegram_id=message.from_user.id)
            user_meal_type = await sync_to_async(MealType.objects.get)(
                name=state_data["type_menu"]
            )
            user_allergies = await make_user_allergies_list(
                state_data["allergens"]
            )
            today = datetime.date.today()

            subscription_plan = await get_subscription_plan(
                name=state_data.get("period")
            )

            subscription_details = {
                "name": state_data["name"],
                "owner": user,
                "plan": subscription_plan,
                "meal_type": user_meal_type,
                "servings": int(state_data["persons"]),
                "daily_meals_amount": int(state_data["eatings"]),
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (
                    today + relativedelta(months=subscription_plan.duration)
                ).strftime("%Y-%m-%d"),
                "promo_code": state_data["promo"],
                "is_paid": True,
                "allergies": user_allergies,
            }
            await save_subscription(subscription_details)

            await message.answer(
                'Поздравляю!\nПодписка успешно оплачена и сохранена.\n\n'
                'Настало время воспользоваться ей. '
                'Для этого нажмите "Мои подписки" и выберете нужную',
                reply_markup=MAIN_KEYBOARD,
            )
            await state.finish()

        @bot.message_handler(commands="test")
        async def run_test(message: Message):
            pass

        @bot.message_handler(lambda message:
                             message.text != "Загружаю рецепт...")
        async def wrong_message(message: Message, state: FSMContext):
            await state.finish()
            await message.reply(
                "Перехват не распознанных сообщений",
                reply_markup=MAIN_KEYBOARD
            )

        executor.start_polling(bot)
