from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.labeled_price import LabeledPrice
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from environs import Env
import uuid
import datetime
import time
import re
from dateutil.relativedelta import relativedelta


from recipes.management.commands.crud import (
    create_new_user,
    get_existing_user,
    get_meal_types,
    get_subscriptions,
    make_user_allergies_list,
    save_subscription,
    get_telegram_user,
    get_promo_code,
    get_random_allowed_recipe,
    get_recipe_ingredients,
    get_recipe_steps,
    get_subscription_plans_names,
    get_subscription_plan,
)

from recipes.management.commands.keyboards import (
    ASK_FOR_PHONE_KEYBOARD,
    MAIN_KEYBOARD,
    await_keyboard,
    make_digit_keyboard,
    make_keyboard,
    make_inline_keyboard,
    make_dynamic_keyboard,
    await_keyboard
)
from recipes.management.commands.bot_processing import (
    create_payment,
    check_payment,
    send_invoice,
)
from recipes.models import (
    PromoCode,
    TelegramUser,
    Allergy,
    MealType,
    Ingredient,
    Recipe,
    Subscription as Subs,
)

# delete
def valid_promocodes():
    return ["blabla", "Wylsa", "bullshit"]


# delete
# PROMO = {"blabla": 10, "Wylsa": 45, "bullshit": 13}


# MENU_TYPES = ("Классическое", "Низкоуглеводное", "Вегетарианское", "Кето")

# SUBSCRIPTIONS = {
#     "1 месяц": {
#         "cost": 300,
#         "currency": "RUR",
#         "timedelta": datetime.timedelta(days=31),
#     },
#     "3 месяца": {
#         "cost": 550,
#         "currency": "RUR",
#         "timedelta": datetime.timedelta(days=92),
#     },
#     "6 месяцев": {
#         "cost": 1650,
#         "currency": "RUR",
#         "timedelta": datetime.timedelta(days=183),
#     },
#     "12 месяцев": {
#         "cost": 3000,
#         "currency": "RUR",
#         "timedelta": datetime.timedelta(days=365),
#     },
# }

ALLERGENS = ["аллерген 1", "аллерген 2", "аллерген 3", "аллерген 4", "аллерген 5"]


class GetRecipe(StatesGroup):
    menu = State()


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


@sync_to_async
def get_allergens_objects():
    return list(Allergy.objects.all())


class Command(BaseCommand):
    help = "Start Telegram bot"

    def handle(self, *args, **kwargs):

        env = Env()
        env.read_env()

        bot_init = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
        storage = MemoryStorage()
        bot = Dispatcher(bot_init, storage=storage)

        @bot.message_handler(commands="start")
        async def hello(message: types.Message):
            try:
                user_data = await get_telegram_user(telegram_id=message.from_user.id)
                await message.answer(
                    f"{user_data.first_name}, hello again!", reply_markup=MAIN_KEYBOARD
                )
            except TelegramUser.DoesNotExist:
                print(
                    f"ERROR hello - TelegramUser.DoesNotExist id={message.from_user.id}"
                )
                await message.answer("Здравствуйте!\n\nКак Вас зовут?\n(введите имя)")
                await UserProfile.first_name.set()

        @bot.message_handler(commands="main", state="*")
        @bot.message_handler(
            lambda message: message.text == "Вернуться на главную", state="*"
        )
        async def return_to_main(message: types.Message, state: FSMContext):
            await state.finish()
            await message.reply("Возвращаемся на главную", reply_markup=MAIN_KEYBOARD)

        @bot.message_handler(state=UserProfile.first_name)
        async def get_user_name(message: types.Message, state: FSMContext):
            await state.update_data(id=message.from_user.id)
            await state.update_data(username=message.from_user.username)
            await state.update_data(first_name=message.text)
            await message.answer("Спасибо.\n\nНапишите еще фамилию, пожалуйста")
            await UserProfile.last_name.set()

        @bot.message_handler(state=UserProfile.last_name)
        async def get_user_surname(message: types.Message, state: FSMContext):
            await state.update_data(last_name=message.text)
            await message.answer(
                "Супер!\n\nОсталось отправить номер телефона для управления подписками.",
                reply_markup=ASK_FOR_PHONE_KEYBOARD,
            )
            await UserProfile.phone_number.set()

        @bot.message_handler(
            state=UserProfile.phone_number, content_types=types.ContentTypes.CONTACT
        )
        async def get_user_phone(message: types.Message, state: FSMContext):
            await state.update_data(phone_number=message.contact.phone_number)
            user_data = await state.get_data()
            await create_new_user(user_data)
            await state.finish()
            await message.answer(
                "Отлично, ваш профиль сохранен!", reply_markup=MAIN_KEYBOARD
            )

        @bot.message_handler(lambda message: message.text == "Мои подписки")
        async def get_user_subscriptions(message: types.Message):
            user = await get_telegram_user(telegram_id=message.from_user.id)
            subscriptions = await get_subscriptions(user)
            subscriptions_names = [subscription.name for subscription in subscriptions]

            if subscriptions_names:
                await message.answer(
                    "Выберите вашу подписку из списка внизу",
                    reply_markup=make_keyboard(subscriptions_names, 1),
                )
                await GetRecipe.menu.set()
            else:
                await message.answer(
                    "Похоже что у вас нет подписок.\nХотите создать первую?",
                    reply_markup=make_keyboard(["Создать подписку"], 1),
                )
      
        @bot.message_handler(state=GetRecipe.menu)
        async def get_recipe_from_subscription(message: types.Message, state: FSMContext):
            user = await get_telegram_user(telegram_id=message.from_user.id)
            random_recipe = await get_random_allowed_recipe(user=user, menu=message.text)
            
            keyboard = types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton('Необходимые ингредиенты', callback_data='get_ingredient'),
                types.InlineKeyboardButton('Рецепт пошагово', callback_data='step_by_step'),
                types.InlineKeyboardButton('Выбрать другое блюдо', callback_data='other_recipe')
            )
            await message.answer(random_recipe.name, reply_markup=MAIN_KEYBOARD)
            await message.answer_photo(
                photo=random_recipe.image_url,
                reply_markup=keyboard
            )
            await state.finish()

        @bot.callback_query_handler(lambda callback: callback.data == 'other_recipe')
        async def other_recipe(callback_query: types.CallbackQuery):
            user = await get_telegram_user(telegram_id=callback_query.from_user.id)
            subscriptions = await get_subscriptions(user)
            subscriptions_names = [subscription.name for subscription in subscriptions]
            await bot_init.send_message(
                chat_id=callback_query.from_user.id,
                text="Напомните пожалуйста для какого меню подобрать блюдо.",
                reply_markup=make_keyboard(subscriptions_names, 1)
            )
            await GetRecipe.menu.set()


        @bot.callback_query_handler(lambda callback: callback.data == 'get_ingredient')
        async def get_ingredients(callback_query: types.CallbackQuery):
            recipe = await sync_to_async(Recipe.objects.get)(name=callback_query.message.caption)
            recipe_ingredients = await get_recipe_ingredients(recipe=recipe)
            ingredient_message = 'ИНГРЕДИЕНТЫ\n'
            for ingredient, how_much in recipe_ingredients.items():
                ingredient_message += f'\n{ingredient}: {how_much}'
            await bot_init.send_message(chat_id=callback_query.from_user.id, text=ingredient_message, reply_markup=MAIN_KEYBOARD)
            
        
        @bot.callback_query_handler(lambda callback: callback.data == 'step_by_step')
        async def step_by_step(callback_query: types.CallbackQuery):
            recipe = await sync_to_async(Recipe.objects.get)(name=callback_query.message.caption)
            recipe_steps = await get_recipe_steps(recipe=recipe)
            for step in recipe_steps:
                time.sleep(0.5)
                await bot_init.send_photo(
                    chat_id=callback_query.from_user.id,
                    photo=step["image_url"],
                    caption=step["instruction"]
                )
            await bot_init.send_message(chat_id=callback_query.from_user.id, text='Приятного аппетита!')
            await bot_init.send_message(chat_id=callback_query.from_user.id, text='😋', reply_markup=MAIN_KEYBOARD)


        @bot.message_handler(lambda message: message.text == "Создать подписку")
        async def create_subscription(message: types.Message):
            await message.answer("Как назовем меню?", reply_markup=make_keyboard(row_width=1))
            await Subscription.name.set()

        @bot.message_handler(state=Subscription.name)
        async def get_subscription_name(message: types.Message, state: FSMContext):
            await state.update_data(name=message.text)
            meal_types = await get_meal_types()
            await message.answer(
                "Укажите тип меню.", reply_markup=make_keyboard(meal_types, 1)
            )
            await Subscription.type_menu.set()

        @bot.message_handler(state=Subscription.type_menu)
        async def get_type_menu(message: types.Message, state: FSMContext):
            await state.update_data(type_menu=message.text)
            await message.answer(
                "Отлично, укажите количество персон", reply_markup=make_digit_keyboard()
            )
            await Subscription.persons.set()

        @bot.message_handler(state=Subscription.persons)
        async def get_number_of_persons(message: types.Message, state: FSMContext):
            await state.update_data(persons=message.text)
            await message.answer(
                "Отлично, укажите количество приемов пищи",
                reply_markup=make_digit_keyboard(),
            )
            await Subscription.eatings.set()

        @bot.message_handler(state=Subscription.eatings)
        async def get_number_of_eatings(message: types.Message, state: FSMContext):
            global allergens
            allergens = [x.name for x in await get_allergens_objects()]

            await state.update_data(eatings=message.text)
            await message.answer(
                "Отлично, укажите аллергены - продукты которых не должно быть ",
                reply_markup=make_dynamic_keyboard(
                    allergens, [], extended_buttons=["Аллергенов нет"]
                ),
            )
            await Subscription.allergens.set()

        @bot.message_handler(state=Subscription.allergens)
        async def get_allergens(message: types.Message, state: FSMContext):
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
        async def get_subscription_period(message: types.Message, state: FSMContext):
            await state.update_data(period=message.text)
            await message.answer(
                "Введите промокод", reply_markup=make_keyboard(["Пропустить"])
            )
            await Subscription.promo.set()

        @bot.message_handler(state=Subscription.promo)
        async def get_promo(message: types.Message, state: FSMContext):
            plan = await state.get_data()
            subscription_plan = await get_subscription_plan(name=plan.get("period"))

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
                        "Такого промокода нет.\n\nВведите корректный или пропустите шаг.",
                        reply_markup=make_keyboard(["Пропустить"]),
                    )
                    await Subscription.promo.set()
                    return

            await message.answer(
                (
                    f"Ура, подписка сформирована.\n\nСтоимость подписки = {price} {currency}\n"
                    f"{benefit_text}\nОсталось ее оплатить и можно идти за продуктами."
                ),
                reply_markup=make_keyboard([]),
            )

            payment_id = uuid.uuid1
            await state.update_data(payment_id=payment_id)
            # print(state_data["name"], cost, payment_id)

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
        async def pre_checkout_answer(pre_checkout_query: types.PreCheckoutQuery):
            print(pre_checkout_query)
            await bot_init.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id,
                ok=True,
                error_message="FUCK!",
            )

        @bot.message_handler(
            content_types=types.ContentTypes.SUCCESSFUL_PAYMENT, state="*"
        )
        async def got_payment(message: types.Message, state: FSMContext):
            state_data = await state.get_data()
            user = await get_telegram_user(telegram_id=message.from_user.id)
            user_meal_type = await sync_to_async(MealType.objects.get)(
                name=state_data["type_menu"]
            )
            user_allergies = await make_user_allergies_list(state_data["allergens"])
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
                "Поздравляю!\nПодписка успешно оплачена и сохранена.\n\nНастало время воспользоваться ей. "
                'Для этого нажмите "Мои подписки" и выберете нужную',
                reply_markup=MAIN_KEYBOARD,
            )
            await state.finish()

        # @sync_to_async
        # def get_subscriptions(user):
        #     return list(Subs.objects.filter(owner=user).all())

        @bot.message_handler(commands="test")
        async def run_test(message: types.Message):
            #user = await sync_to_async(TelegramUser.objects.get)(telegram_id=message.from_user.id)
            user = await get_telegram_user(telegram_id=message.from_user.id)
            try:
                random_recipe = await get_random_allowed_recipe(user=user, menu='Воововлв')
            except:
                random_recipe = await get_random_allowed_recipe(user=user, menu='Подписка номер один')
                
            keyboard = types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton('Необходимые ингредиенты', callback_data='get_ingredient'),
                types.InlineKeyboardButton('Рецепт пошагово', callback_data='step_by_step')
            )

            await message.answer_photo(
                photo=random_recipe.image_url,
                caption=f"{random_recipe.name}",
                reply_markup=keyboard
            )


        


        @bot.message_handler(lambda message: message.text != "Загружаю рецепт...")
        async def return_to_main(message: types.Message, state: FSMContext):
            await state.finish()
            await message.reply(
                "Перехват не распознанных сообщений", reply_markup=MAIN_KEYBOARD
            )

        executor.start_polling(bot)
