from .token import Token
from epure import epure
from typing import List

@epure()
class Currency(Token):
    _currencies = None
    aliases: List[str]

    @classmethod
    def currencies(cls):
        if not cls._currencies:
            cls._currencies = Currency.resource.read()
        return cls._currencies
   

    @classmethod
    def get_by_alias(cls, alias: str) -> Token:
        res = None

        for cr in cls.currencies():
            if cr.aliases and alias in cr.aliases:
                res = cr
                break
        if res == None:
            raise ValueError(f'there is no currency with {alias} alias')
        
        return res
    
    def __str__(self):
        return self.aliases[0]