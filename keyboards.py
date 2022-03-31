from aiogram import types


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


def make_keyboard(buttons: list, row_width: int = 2, extended_buttons: list = []):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width
    ).add(*buttons)
    for button in extended_buttons + ['Вернуться на главную']:
        keyboard.add(button)
    return keyboard


def make_digit_keyboard(how_much: int = 6, row_width: int = 3, one_time: bool = False):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width, one_time_keyboard=one_time)
    keyboard.add(*[str(x + 1) for x in range(how_much)])
    keyboard.add("Вернуться на главную")
    return keyboard