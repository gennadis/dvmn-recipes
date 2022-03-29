from ast import Sub
from environs import Env

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(
    resize_keyboard=True
).add(*["Мои подписки", "Создать подписку"])

ASK_FOR_PHONE_KEYBOARD = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    types.KeyboardButton(
        "Отправить номер телефона",
        request_contact=True
    )
)


class UserProfile(StatesGroup):
    id = State()
    name = State()
    surname = State()
    phone = State()


class Subscription(StatesGroup):
    type_menu = State()
    persons = State()
    eatings = State()
    allergens = State()
    period = State()
    promo = State()
    payment = State()
    

async def save_profile(state, fs, cursor):
    profile = await state.get_data()
    cursor.execute(
        "INSERT INTO users VALUES(?, ?, ?, ?);",
        (
            profile.get("id"),
            profile.get("name"),
            profile.get("surname"),
            profile.get("phone")
        )
    )
    fs.commit()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    # JUST FOR TEST
    import sqlite3
    fs = sqlite3.connect('test_base.sqlite3')
    cursor = fs.cursor()

    bot_init = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    bot = Dispatcher(bot_init, storage=storage)


    @bot.message_handler(commands="start")
    async def hello(message: types.Message):
        # Check if it is new user
        #    await message.answer(f'{user_name}, hello again!', reply_markup=MAIN_KEYBOARD)
        # else:
        await message.answer('Здравствуйте!\n\nКак Вас зовут?\n(введите имя)')
        await UserProfile.name.set()


    @bot.message_handler(state=UserProfile.name)
    async def get_user_name(message: types.Message, state: FSMContext):
        await state.update_data(id=message.from_user.id)
        await state.update_data(name=message.text)
        await message.answer('Спасибо.\n\nНапишите еще фамилию, пожалуйста')
        await UserProfile.surname.set()

    
    @bot.message_handler(state=UserProfile.surname)
    async def get_user_surname(message: types.Message, state: FSMContext):
        await state.update_data(surname=message.text)
        await message.answer(
            'Супер!\n\nОсталось отправить номер телефона для управления подписками.',
            reply_markup=ASK_FOR_PHONE_KEYBOARD
        )
        await UserProfile.phone.set()
    

    @bot.message_handler(state=UserProfile.phone, content_types=types.ContentTypes.CONTACT)
    async def get_user_phone(message: types.Message, state: FSMContext):
        await state.update_data(phone=message.contact.phone_number)
        
        # delete fs, cursor before MVP
        await save_profile(state, fs, cursor)
        await state.finish()
        await message.answer('Отлично, ваш профиль сохранен!', reply_markup=MAIN_KEYBOARD)


    @bot.message_handler(lambda message: message.text == "Мои подписки")
    async def get_user_subscriptions(message: types.Message):
        await message.answer('Здесь будут Ваши подписки!')

    
    @bot.message_handler(lambda message: message.text == "Создать подписку")
    async def create_subscription(message: types.Message):
        await message.answer('Здесь можно будет создать подписку.\n\nСовсем скоро...')


    @bot.message_handler(state=Subscription.type_menu)
    async def get_type_menu(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.persons)
    async def get_number_of_persons(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.eatings)
    async def get_number_of_eatings(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.allergens)
    async def get_allergens(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.period)
    async def get_subscription_period(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.promo)
    async def get_promo(message: types.Message):
        pass


    @bot.message_handler(state=Subscription.payment)
    async def make_payment(message: types.Message):
        pass







    executor.start_polling(bot)