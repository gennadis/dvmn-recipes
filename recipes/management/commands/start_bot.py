from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from environs import Env

from recipes.management.commands.crud import create_new_user
from recipes.management.commands.keyboards import (ASK_FOR_PHONE_KEYBOARD,
                                                   MAIN_KEYBOARD,
                                                   make_digit_keyboard,
                                                   make_keyboard,
                                                   make_inline_keyboard)
from recipes.management.commands.bot_processing import (create_payment,
                                                        check_payment)
from recipes.models import (TelegramUser,
                            Allergy,
                            Subscription)

# delete
def valid_promocodes():
    return ['blabla', 'Wylsa', 'bullshit']

#delete
PROMO = {
    'blabla': 10,
    'Wylsa': 45,
    'bullshit': 13
}




MENU_TYPES = ("Классическое", "Низкоуглеводное", "Вегетарианское", "Кето")

SUBSCRIPTIONS = {
    "1 месяц": {
        "cost": 300,
        "currency": 'RUR'
    },
    "3 месяца": {
        "cost": 550,
        "currency": 'RUR'
    },
    "6 месяцев": {
        "cost": 1650,
        "currency": 'RUR'
    },
    "12 месяцев": {
        "cost": 3000,
        "currency": 'RUR'
    }
}

ALLERGENS = ["аллерген 1", "аллерген 2", "аллерген 3", "аллерген 4", "аллерген 5"]



class UserProfile(StatesGroup):
    id = State()
    username = State()
    first_name = State()
    last_name = State()
    phone_number = State()


class Subscription(StatesGroup):
    type_menu = State()
    persons = State()
    eatings = State()
    allergens = State()
    period = State()
    promo = State()
    payment_id = State()


@sync_to_async
def get_allergens_objects():
    return list(
        Allergy.objects.all()
    )


class Command(BaseCommand):
    help = "Start Telegram bot"

    def handle(self, *args, **kwargs):

        env = Env()
        env.read_env()

        bot_init = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
        storage = MemoryStorage()
        bot = Dispatcher(bot_init, storage=storage)

        yookassa_shop_id = env.int("YOOKASSA_SHOP_ID")
        yookassa_secret_key = env.str("YOOKASSA_SECRET_KEY")

        
        @bot.message_handler(commands="start")
        async def hello(message: types.Message):
            try:
                user_data = await sync_to_async(TelegramUser.objects.get)(telegram_id=message.from_user.id)
                print(user_data)
                await message.answer(
                    f"{user_data.first_name}, hello again!", reply_markup=MAIN_KEYBOARD
                )
            except TelegramUser.DoesNotExist:
                print('ERROR hello')
                await message.answer("Здравствуйте!\n\nКак Вас зовут?\n(введите имя)")
                await UserProfile.first_name.set()

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


        @bot.message_handler(state=UserProfile.phone_number, content_types=types.ContentTypes.CONTACT)
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

            # Здесь будут список названий подписок пользователя
            user_subscriptions_titles = [
                "Крутая подписка",
                "Очень крутая подписка",
                "Супер-пупер подписка",
            ]

            # проверка есть ли хотя бы одна подписка. Если нет - сообщить
            await message.answer(
                "Выберите вашу подписку из списка внизу",
                reply_markup=make_keyboard(user_subscriptions_titles, 1),
            )


        @bot.message_handler(lambda message: message.text == "Создать подписку")
        async def create_subscription(message: types.Message):
            await message.answer(
                "Укажите тип меню.", reply_markup=make_keyboard(MENU_TYPES, 1)
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
                reply_markup=make_keyboard(
                    allergens, extended_buttons=["Аллергенов нет"]
                ),
            )
            await Subscription.allergens.set()

        @bot.message_handler(state=Subscription.allergens)
        async def get_allergens(message: types.Message, state: FSMContext):
            if message.text in ["Готово", "Аллергенов нет"]:
                await message.answer(
                    "Отлично, выберите период подписки",
                    reply_markup=make_keyboard(list(SUBSCRIPTIONS.keys())),
                )
                await Subscription.period.set()
            elif message.text in allergens:
                try:
                    state_data = await state.get_data()
                    user_allergens = state_data.get("allergens")
                    if message.text not in user_allergens:
                        user_allergens.append(message.text)
                except TypeError:
                    user_allergens = [f"{message.text}"]
                await state.update_data(allergens=user_allergens)
                await message.answer(
                    "Добавим еще один?",
                    reply_markup=make_keyboard(allergens, extended_buttons=["Готово"]),
                )
                await Subscription.allergens.set()


        @bot.message_handler(state=Subscription.period)
        async def get_subscription_period(message: types.Message, state: FSMContext):
            await state.update_data(period=message.text)
            await message.answer("Введите промокод", reply_markup=make_keyboard(["Пропустить"]))
            await Subscription.promo.set()


        @bot.message_handler(state=Subscription.promo)
        async def get_promo(message: types.Message, state: FSMContext):
            state_data = await state.get_data()
            currency = SUBSCRIPTIONS[state_data["period"]]["currency"]

            if message.text == 'Пропустить':
                await state.update_data(promo=None)
                cost = SUBSCRIPTIONS[state_data["period"]]["cost"]
                benefit_text = ''

            elif message.text in valid_promocodes():
                await state.update_data(promo=message.text)
                benefit = round(SUBSCRIPTIONS[state_data["period"]]["cost"] * PROMO[message.text] * 0.01)
                cost = SUBSCRIPTIONS[state_data["period"]]["cost"] - benefit
                benefit_text = f'Вы сэкономили {benefit} {currency}\n'

            else:
                await message.reply(
                    'Такого промокода нет.\n\nВведите корректный или пропустите шаг.',
                    reply_markup=make_keyboard(["Пропустить"])
                )
                await Subscription.promo.set()
                return

            await message.answer(
                (f'Ура, подписка сформирована.\n\nСтоимость подписки = {cost} {currency}\n'
                 f'{benefit_text}\nОсталось ее оплатить и можно идти за продуктами.'),
                reply_markup=types.ReplyKeyboardRemove()
            )

            
            payment = create_payment(yookassa_shop_id, yookassa_secret_key)
            await state.update_data(payment_id=payment.id)
            await message.answer(
                payment.confirmation.confirmation_url,
                reply_markup=make_keyboard(["Платеж прошел?"])
            )
            await Subscription.payment_id.set()


        @bot.message_handler(state=Subscription.payment_id)
        async def make_payment(message: types.Message, state: FSMContext):
            state_data = await state.get_data()
            if check_payment(state_data.get("payment_id"), yookassa_shop_id, yookassa_secret_key):
                await message.answer(
                    "Оплата успешно завершена.", reply_markup=MAIN_KEYBOARD
                )
                await state.finish()
            else:
                await message.answer(
                    "А вы точно оплатили? Если да, подождите пару минут и нажмите кнопку проверки еще раз.",
                    reply_markup=make_keyboard(["Платеж прошел?"])
                )
                await Subscription.payment_id.set()

        

        @bot.message_handler()
        async def return_to_main(message: types.Message, state: FSMContext):
            await state.finish()
            await message.reply(
                "Перехват не распознанных сообщений", reply_markup=MAIN_KEYBOARD
            )

        executor.start_polling(bot)
