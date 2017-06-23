class NotEnoughGoods(Exception):
    def __init__(self, name, available, required):
        super().__init__(name + " available %d but required %d" % (available, required))
        self.available = available
        self.required = required

    def getAvailable(self):
        return self.available

    def getRequired(self):
        return self.required

    def getDifference(self):
        return self.required - self.available
