import uuid
import asyncio
import datetime
from aiohttp import ClientSession

from yookassa import Payment, Configuration, Payout
from yookassa.payment import PaymentResponse

from config_data.config import Config, load_config


config: Config = load_config()


Configuration.account_id = config.yookassa.account_id
Configuration.secret_key = config.yookassa.secret_key


async def get_yookassa_url(amount: int, description: str):
    payment = await Payment.create({
        "amount": {
            "value": str(amount) + '.00',
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/childrenhelprobot"
        },
        "receipt": {
            "customer": {
                "email": "kkulis985@gmail.com"
            },
            'items': [
                {
                    'description': description,
                    "amount": {
                        "value": str(amount) + '.00',
                        "currency": "RUB"
                    },
                    'measure': 'another',
                    'vat_code': 1,
                    'quantity': 1,
                    'payment_subject': 'payment',
                    'payment_mode': 'full_payment'
                }
            ]
        },
        "capture": True,
        "description": description
    }, uuid.uuid4())
    url = payment.confirmation.confirmation_url
    return {
        'url': url,
        'id': payment.id
    }


async def check_yookassa_payment(payment_id):
    payment: PaymentResponse = await Payment.find_one(payment_id)
    if payment.paid:
        return True
    return False