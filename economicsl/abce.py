from collections import defaultdict
import numpy as np


class NotEnoughGoods(Exception):
    def __init__(self, name, available, required) -> None:
        super().__init__(name + " available %d but required %d" % (available, required))
        self.available = available
        self.required = required

    def getAvailable(self) -> np.longdouble:
        return self.available

    def getRequired(self) -> np.longdouble:
        return self.required

    def getDifference(self) -> np.longdouble:
        return self.required - self.available


# Accounting classes: Inventory

class Inventory(defaultdict):
    def __init__(self) -> None:
        # cash defaults to 0.0
        super(Inventory, self).__init__(np.longdouble)

    def getGood(self, name) -> np.longdouble:
        return self[name]

    def getCash(self) -> np.longdouble:
        return self.getGood("cash")

    def create(self, name, amount) -> None:
        assert amount >= 0.0
        self[name] += amount

    def destroy(self, name, amount) -> None:
        assert amount >= 0.0
        have = self.getGood(name)
        if amount > have:
            raise NotEnoughGoods(name, have, amount)
        self[name] = have - amount
