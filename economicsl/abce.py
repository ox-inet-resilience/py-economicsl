from collections import defaultdict
import numpy as np


class NotEnoughGoods(Exception):
    def __init__(self, name: str, available, required) -> None:
        super().__init__(name + " available %d but required %d" % (available, required))
        self.available = available
        self.required = required

    def get_available(self) -> np.longdouble:
        return self.available

    def get_required(self) -> np.longdouble:
        return self.required

    def get_difference(self) -> np.longdouble:
        return self.required - self.available


# Accounting classes: Inventory

class Inventory(defaultdict):
    def __init__(self) -> None:
        # cash defaults to 0.0
        super(Inventory, self).__init__(np.longdouble)

    def get_good(self, name: str) -> np.longdouble:
        return self[name]

    def get_cash(self) -> np.longdouble:
        return self.get_good("cash")

    def create(self, name: str, amount) -> None:
        assert amount >= 0.0
        self[name] += amount

    def destroy(self, name: str, amount) -> None:
        assert amount >= 0.0
        have = self.get_good(name)
        if amount > have:
            raise NotEnoughGoods(name, have, amount)
        self[name] = have - amount
