from dataclasses import dataclass

from environs import Env

'''
    При необходимости конфиг базы данных или других сторонних сервисов
'''


@dataclass
class tg_bot:
    token: str
    admin_ids: list[int]


@dataclass
class DB:
    dns: str


@dataclass
class NatsConfig:
    servers: list[str]


@dataclass
class Yookassa:
    account_id: int
    secret_key: str


@dataclass
class APIMart:
    api_key: str


@dataclass
class Proxy:
    login: str
    password: str
    ip: str
    port: int


@dataclass
class Config:
    bot: tg_bot
    db: DB
    nats: NatsConfig
    yookassa: Yookassa
    apimart: APIMart
    proxy: Proxy


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        bot=tg_bot(
            token=env('token'),
            admin_ids=list(map(int, env.list('admins')))
            ),
        db=DB(
            dns=env('dns')
        ),
        nats=NatsConfig(
            servers=env.list('nats')
        ),
        yookassa=Yookassa(
            account_id=int(env('account_id')),
            secret_key=env('secret_key')
        ),
        apimart=APIMart(
            api_key=env('apimart_api_key')
        ),
        proxy=Proxy(
            login=env('login'),
            password=env('password'),
            ip=env('ip'),
            port=int(env('port'))
        )
    )
