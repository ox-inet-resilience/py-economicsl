import economicsl
from economicsl.accounting import Ledger


class GiveAgent(economicsl.Trader):
    def __init__(self, name, teddies, money, simulation):
        super().__init__(name, simulation)
        self.main_ledger = Ledger()
        self.add_cash(money)
        self.get_ledger().create("teddies", teddies, 100.0)

    def give(self, receiver):
        try:
            super().give(receiver, "ball", 1)
            print(" gave ball ")
        except economicsl.NotEnoughGoods:
            pass
