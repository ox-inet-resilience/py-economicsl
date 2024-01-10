from collections import defaultdict


eps = 5e-9


class NotEnoughGoods(Exception):
    def __init__(self, name: str, available, required) -> None:
        super().__init__(name + " available %f but required %f" % (available, required))
        self.available = available
        self.required = required

    def get_available(self) -> float:
        return self.available

    def get_required(self) -> float:
        return self.required

    def get_difference(self) -> float:
        return self.required - self.available


# Accounting classes: Inventory


class Inventory(defaultdict):
    def __init__(self) -> None:
        super().__init__(float)

    def get_good(self, name: str) -> float:
        return self[name]

    @property
    def cash(self) -> float:
        return self.get_good("cash")

    def create(self, name: str, amount) -> None:
        assert amount >= 0.0, amount
        self[name] += amount

    def destroy(self, name: str, amount) -> None:
        assert amount >= 0.0, amount
        have = self.get_good(name)
        if abs(have - amount) <= 2 * eps:
            amount = have
        if amount - have > eps:
            raise NotEnoughGoods(name, have, amount)
        self[name] = have - amount
