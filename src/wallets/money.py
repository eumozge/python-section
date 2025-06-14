import decimal
from dataclasses import KW_ONLY, dataclass
from typing import Self

from src.wallets.currency import Currency
from src.wallets.exceptions import NegativeValueException, NotComparisonException


@dataclass(slots=True, frozen=True, repr=True)
class Money:
    _: KW_ONLY
    value: decimal
    currency: Currency

    def __add__(self, other):
        self.check_same_currency(other)
        return Money(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other):
        self.check_same_currency(other)
        return Money(value=self.value - other.value, currency=self.currency)

    def check_same_currency(self, other):
        if not self.currency == other.currency:
            raise NotComparisonException(self, other)

    def is_negative(self):
        return self.value < 0


class Wallet:
    def __init__(self, *args: Money):
        self.__container = {}
        self.add(*args)

    def __getitem__(self, item: Currency):
        return self.__container.setdefault(item, Money(value=0, currency=item))

    def __setitem__(self, key: Currency, value: Money):
        assert key == value.currency, (key, value.currency)
        self.__container[key] = value

    def __delitem__(self, key):
        if key in self:
            del self.__container[key]

    def __contains__(self, item: Currency):
        return item in self.currencies

    def __len__(self):
        return len(self.currencies)

    @property
    def currencies(self):
        return self.__container.keys()

    def add(self, money: Money) -> Self:
        self[money.currency] = self[money.currency] + money
        return self

    def sub(self, money: Money) -> Self:
        val = self[money.currency] - money
        if val.is_negative():
            raise NegativeValueException(self[money.currency], money)
        self[money.currency] = val
        return self
