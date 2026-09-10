import random
import uuid
import asyncio
import datetime
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from aioplatega import Platega, PaymentDetails, PaymentMethodInt, PlategaAPIError
from aioplatega.enums.payment_status import PaymentStatus
from aioyookassa import YooKassa
from aioyookassa.types.payment import (Money, Confirmation, Receipt, Customer,
                                       PaymentItem, PaymentAmount, PaymentSubject, PaymentMode)
from aioyookassa.types.enum import PaymentStatus, ConfirmationType, Currency
from aioyookassa.types.params import CreatePaymentParams, GetPaymentsParams

from config_data.config import Config, load_config


config: Config = load_config()
proxy = config.proxy

proxy = f'http://{proxy.login}:{proxy.password}@{proxy.ip}:{proxy.port}'


async def get_client() -> YooKassa:
    timeout = ClientTimeout(60)
    client = YooKassa(api_key=config.yookassa.secret_key, shop_id=config.yookassa.account_id, proxy=proxy,
                      timeout=timeout)  # proxy=proxy
    return client


async def get_yookassa_url(amount: float | int, description: str):
    client = await get_client()
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
    client = await get_client()
    payment = await client.payments.get_payment(payment_id)
    await client.close()
    if payment.paid:
        return True
    return False


# result = (asyncio.run(get_yookassa_url(10.0, 'Тест')))
# print(result)
# asyncio.run(asyncio.sleep(5))
# print(asyncio.run(check_yookassa_payment(result.get('id'))))


client = Platega(
    merchant_id=config.platega.merchant_id,
    secret=config.platega.secret_key
)


async def get_platega_sbp(amount: float, user_id: int):
    try:
        data = await client.create_transaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(
                amount=float(amount),
                currency='RUB'
            ),
            description=f'TgId:{user_id}',
            return_url='https://t.me/VedmaAstroBot',
            failed_url='https://t.me/VedmaAstroBot',
            payload=str(user_id),

        )
        # print(data.transaction_id, int(data.transaction_id), str(data.transaction_id))
        return {
            'url': data.redirect,
            'id': data.transaction_id
        }
    except PlategaAPIError as err:
        print(err.message, err.errors, err.body)
        print(err)
        return False
    except Exception as err:
        print(err)
        return False
    finally:
        try:
            await client.close()
        except Exception:
            ...


async def get_platega_card(amount: float, user_id: int):
    try:
        data = await client.create_transaction(
            payment_method=PaymentMethodInt.CARDS_RUB,
            payment_details=PaymentDetails(
                amount=float(amount),
                currency='RUB'
            ),
            description=f'TgId:{user_id}',
            return_url='https://t.me/VedmaAstroBot',
            failed_url='https://t.me/VedmaAstroBot',
            payload=str(random.randint(100000, 999999)),

        )
        print(data)
        # print(data.transaction_id, int(data.transaction_id), str(data.transaction_id))
        return {
            'url': data.redirect,
            'id': data.transaction_id
        }
    except PlategaAPIError as err:
        print(err.message, err.errors)
        print(f'platega api err: {err}')
        return False
    except Exception as err:
        print(err)
        return False
    finally:
        try:
            await client.close()
        except Exception:
            ...


# print(asyncio.run(get_platega_sbp(500.0, 8005178596)))


async def check_platega_transaction(transaction_id):
    transaction = await client.get_transaction_status(transaction_id)
    print(transaction.status)
    return transaction.status == 'CONFIRMED'


print(asyncio.run(check_platega_transaction('9fd95581-63fb-4ba3-a650-8a72e0914cf6')))
