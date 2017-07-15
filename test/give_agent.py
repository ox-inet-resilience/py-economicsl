import economicsl


class GiveAgent(economicsl.Trade):
    def __init__(self, name, teddies, money, simulation):
        super().__init__(name, simulation)
        self.addCash(money)
        self.getMainLedger().create("teddies", teddies, 100.0)

    def give(self, receiver):
        try:
            super().give(receiver, "ball", 1)
            print(" gave ball ")
        except economicsl.NotEnoughGoods:
            pass
