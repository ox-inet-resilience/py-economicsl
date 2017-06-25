class NotEnoughGoods(Exception):
    def __init__(self, name, available, required) -> None:
        super().__init__(name + " available %d but required %d" % (available, required))
        self.available = available
        self.required = required

    def getAvailable(self) -> float:
        return self.available

    def getRequired(self) -> float:
        return self.required

    def getDifference(self) -> float:
        return self.required - self.available
