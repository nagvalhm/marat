from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from epure import epure, proto
from .member import Member
from aiogram.types.user import User as TgUser
from ..token.currency import Currency
if TYPE_CHECKING:
    from ..token.transaction import Transaction

# from epure.generics import Check

@epure()
class User(Member):    
    first_name: str
    last_name: str
    username: str

    @classmethod
    def users(cls):
        res = User.resource.read()
        return res


    def __init__(self, user: TgUser=None):
        # super().__init__()
        if user:
            self.telegram_id = user.id
            self.first_name = user.first_name
            self.last_name = user.last_name
            self.username = user.username

    @classmethod
    def tg_user_is_saved(cls, user: TgUser) -> bool:
        users = cls.users()
        filtered = list(filter(lambda u: u.telegram_id == user.id, users))
        res = len(filtered) > 0
        return res
    
    @classmethod
    def save_user(cls, user: TgUser):
        res = cls(user).save()
        return res
    
    def send_currency(self, to_user: User, currency: Currency, amount: float) -> Transaction:
        from ..token.transaction import Transaction
        res = Transaction(self, to_user, currency, amount)
        res = res.save()

        return res
    
    def __str__(self):
        return f'@{self.username}'