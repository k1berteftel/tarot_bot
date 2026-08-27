import uuid
import asyncio
import datetime
from aiohttp import ClientSession

from aioyookassa import YooKassa
from aioyookassa.types.payment import (Money, Confirmation, Receipt, Customer,
                                       PaymentItem, PaymentAmount, PaymentSubject, PaymentMode)
from aioyookassa.types.enum import PaymentStatus, ConfirmationType, Currency
from aioyookassa.types.params import CreatePaymentParams, GetPaymentsParams

from config_data.config import Config, load_config


config: Config = load_config()
proxy = config.proxy
proxy = f'http://{proxy.login}:{proxy.password}@{proxy.ip}:{proxy.port}'
client = YooKassa(api_key=config.yookassa.secret_key, shop_id=config.yookassa.account_id) # proxy=proxy


async def get_yookassa_url(amount: float | int, description: str):
    params = CreatePaymentParams(
        amount=Money(value=float(amount), currency=Currency.RUB),
        confirmation=Confirmation(type=ConfirmationType.REDIRECT, return_url="https://t.me/VedmaAstroBot"),
        description=description,
        receipt=Receipt(
            customer=Customer(
                email='kkulis985@gmail.com'
            ),
            items=[
                PaymentItem(
                    description=description,
                    amount=PaymentAmount(value=float(amount), currency=Currency.RUB),
                    measure='another',
                    vat_code=1,
                    quantity=1,
                    payment_subject=PaymentSubject.PAYMENT,
                    payment_mode=PaymentMode.FULL_PAYMENT
                )
            ]
        )

    )
    payment = await client.payments.create_payment(params)

    await client.close()

    return {
        'url': payment.confirmation.url,
        'id': payment.id
    }


async def check_yookassa_payment(payment_id: str):
    payment = await client.payments.get_payment(payment_id)
    await client.close()
    if payment.paid:
        return True
    return False


# result = (asyncio.run(get_yookassa_url(10.0, 'Тест')))
# print(result)
# asyncio.run(asyncio.sleep(5))
# print(asyncio.run(check_yookassa_payment(result.get('id'))))