from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


MAIN_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True).add(
    *["Мои подписки", "Создать подписку"]
)

ASK_FOR_PHONE_KEYBOARD = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(KeyboardButton("Отправить номер телефона", request_contact=True))


def make_keyboard(buttons: list = [],
                  row_width: int = 2,
                  one_time: bool = False,
                  extended_buttons: list = []) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width,
        one_time_keyboard=one_time
    ).add(*buttons)
    for button in extended_buttons + ["Вернуться на главную"]:
        keyboard.add(button)
    return keyboard


def make_digit_keyboard(how_much: int = 6,
                        row_width: int = 3,
                        one_time: bool = False) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width,
        one_time_keyboard=one_time
    )
    keyboard.add(*[str(x + 1) for x in range(how_much)])
    keyboard.add("Вернуться на главную")
    return keyboard


def make_dynamic_keyboard(buttons: list,
                          comparison: list,
                          row_width: int = 2,
                          one_time: bool = False,
                          extended_buttons: list = []) -> ReplyKeyboardMarkup:
    actual_buttons = [
        f'Удалить {button}'
        if button in comparison
        else f'Добавить {button}'
        for button in buttons
    ]
    return make_keyboard(
        buttons=actual_buttons,
        row_width=row_width,
        one_time=one_time,
        extended_buttons=extended_buttons
    )
