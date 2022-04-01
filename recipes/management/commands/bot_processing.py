from locale import currency
from yookassa import Configuration, Payment
from environs import Env
from aiogram import types
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import invoice
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from environs import Env


def create_payment(shop_id: int, secret_key: str):
    Configuration.account_id = shop_id
    Configuration.secret_key = secret_key

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/dvmn_march_11_bot"
        },
        "capture": True,
        "description": "Заказ №1",
        "metadata": {
        "order_id": "37"
        }
    })
    return payment

def check_payment(payment_id, shop_id: int, secret_key: str):
    Configuration.account_id = shop_id
    Configuration.secret_key = secret_key
    return Payment.find_one(payment_id).paid


def send_invoice(user_id, token):
    params = {
        'chat_id': user_id,
        'title': 'Something',
        'description': 'Something veery baaad!',
        'payload': 'sodgogosgoskjdglkjdf',
        'provider_token': token,
        'currency': 'RUB',
        'price': 100000
    }

if __name__ == '__main__':
    import environs
    env = environs.Env()
    env.read_env()

    bot_init = Bot(token=env.str("TEST_TG_TOKEN"), parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    bot = Dispatcher(bot_init, storage=storage)

    url = f'https://api.telegram.org/bot{env.str("BOT_TOKEN")}/sendinvoice'
    prices = [
        types.labeled_price.LabeledPrice(label='Working Time Machine', amount=500100),
    ]

    @bot.message_handler
    async def blabla():
        payment =  invoice(
                    title = 'blabla',
                    description = 'albalbalb',
                    start_parameter = 'sdsdfsdfsdfsdfsdf',
                    currency = 'RUB',
                    total_amount = 10000
                )
        
    import requests

    #response = requests.post(url, params=params)
    #print(response.json())

    executor.start_polling(bot)
    