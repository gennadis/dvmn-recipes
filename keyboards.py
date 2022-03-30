from aiogram import types


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
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


def make_one_time_keyboard(buttons):
    return types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    ).add(*buttons).add('Вернуться на главную')
    

def how_much_persons_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, one_time_keyboard=True)
    keyboard.add(*[str(x + 1) for x in range(8)])
    keyboard.add("Вернуться на главную")
    return keyboard