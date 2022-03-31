from yookassa import Configuration, Payment
from environs import Env
from aiogram import types


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

    url = f'https://api.telegram.org/bot{env.str("BOT_TOKEN")}/sendinvoice'
    prices = [
        types.labeled_price.LabeledPrice(label='Working Time Machine', amount=500100),
        types.labeled_price.LabeledPrice(label='Working Time Machine2', amount=5300100)
    ]

    print(type(prices), prices)
    params = {
        'chat_id': 434137786,
        'title': 'Something',
        'description': 'Something veery baaad!',
        'payload': 'sodgogosgoskjdglkjdf',
        'provider_token': env.str('SBER_TOKEN'),
        'currency': 'RUB',
        'prices': prices
    }
    import requests

    response = requests.post(url, params=params)
    print(response.json())
    