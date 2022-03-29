from environs import Env

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(
    resize_keyboard=True
).add(*["Мои подписки", "Создать подписку"])

ASK_FOR_PHONE_KEYBOARD = types.ReplyKeyboardMarkup(
    resize_keyboard=True
).add(
    types.KeyboardButton(
        "Отправить номер телефона", request_contact=True
    )
)


class user_profile(StatesGroup):
    user_name = State()
    user_surname = State()
    user_phone = State()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    bot_init = Bot(token=env.str("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    bot = Dispatcher(bot_init, storage=storage)


    @bot.message_handler(commands="start")
    async def hello(message: types.Message):
        await message.answer('Hello!')

    executor.start_polling(bot)