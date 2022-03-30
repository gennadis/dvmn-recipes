from environs import Env

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


from keyboards import (
    MAIN_KEYBOARD,
    ASK_FOR_PHONE_KEYBOARD,
    how_much_persons_keyboard,
    make_one_time_keyboard
)


ALLERGENS = [
    'аллерген 1',
    'аллерген 2',
    'аллерген 3',
    'аллерген 4',
    'аллерген 5'

]

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

        # Здесь будут список названий подписок пользователя
        user_subscriptions_titles = ['Крутая подписка', 'Очень крутая подписка', 'Супер-пупер подписка']

        # проверка есть ли хотя бы одна подписка. Если нет - сообщить
        await message.answer('Выберите вашу подписку из списка внизу', reply_markup=make_one_time_keyboard(user_subscriptions_titles))

    
    @bot.message_handler(lambda message: message.text == "Создать подписку")
    async def create_subscription(message: types.Message):
        await message.answer('Укажите тип меню.')
        await Subscription.type_menu.set()


    @bot.message_handler(state=Subscription.type_menu)
    async def get_type_menu(message: types.Message, state: FSMContext):
        await state.update_data(type_menu=message.text)
        await message.answer('Отлично, укажите количество персон', reply_markup=how_much_persons_keyboard())
        await Subscription.persons.set()


    @bot.message_handler(state=Subscription.persons)
    async def get_number_of_persons(message: types.Message, state: FSMContext):
        await state.update_data(persons=message.text)
        await message.answer(
            'Отлично, укажите количество приемов пищи',
            reply_markup=make_one_time_keyboard([str(x + 1) for x in range(4)])
        )
        await Subscription.eatings.set()


    @bot.message_handler(state=Subscription.eatings)
    async def get_number_of_eatings(message: types.Message, state: FSMContext):
        await state.update_data(eatings=message.text)
        await message.answer('Отлично, укажите аллергены - продукты которых не должно быть ', reply_markup=make_one_time_keyboard(ALLERGENS))
        await Subscription.allergens.set()


    @bot.message_handler(state=Subscription.allergens)
    async def get_allergens(message: types.Message, state: FSMContext):
        if message.text == 'Готово':
            
            await message.answer(
                'Отлично, выберите период подписки',
                reply_markup=make_one_time_keyboard([
                    '7 дней',
                    '14 дней',
                    '1 месяц'
                ])
            )
            await Subscription.period.set()
        elif message.text in ALLERGENS:
            try:
                state_data = await state.get_data()
                user_allergens = state_data.get('allergens')
                user_allergens.append(message.text)
            except AttributeError:
                user_allergen = [f'{message.text}']
            await state.update_data(allergens=user_allergens)
            await message.answer("Добавим еще один?", reply_markup=make_one_time_keyboard(ALLERGENS + ['Готово']))
            await Subscription.allergens.set()


    @bot.message_handler(state=Subscription.period)
    async def get_subscription_period(message: types.Message, state: FSMContext):
        await state.update_data(period=message.text)
        await message.answer('Введите промокод')
        await Subscription.promo.set()


    @bot.message_handler(state=Subscription.promo)
    async def get_promo(message: types.Message, state: FSMContext):
        await state.update_data(promo=message.text)
        await message.answer('Итак, подписка сформирована. Осталось ее оплатить и можно идти за продуктами.', reply_markup=make_one_time_keyboard(['Оплатить подписку']))
        await Subscription.payment.set()


    @bot.message_handler(state=Subscription.payment)
    async def make_payment(message: types.Message, state: FSMContext):
        await state.update_data(payment=message.text)
        await message.answer('Оплата успешно завершена.', reply_markup=MAIN_KEYBOARD)
        await state.finish()
        



    @bot.message_handler(lambda message: message.text == 'Вернуться на главную', state='*')
    async def return_to_main(message: types.Message, state: FSMContext):
        await state.finish()
        await message.reply('Возвращаемся на главную', reply_markup=MAIN_KEYBOARD)
    
    @bot.message_handler()
    async def return_to_main(message: types.Message, state: FSMContext):
        await state.finish()
        await message.reply('Перехват не распознанных сообщений', reply_markup=MAIN_KEYBOARD)


    executor.start_polling(bot)