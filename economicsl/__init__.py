from typing import List
import numpy as np

from .accounting import Ledger
from .obligations import ObligationMessage, ObligationsAndGoodsMailbox

from .obligations import Obligation
from .accounting import AccountType  # NOQA
from abce import NotEnoughGoods  # NOQA
import abce


class Agent(abce.Agent):
    def __init__(self, id, group, trade_logging,
                 database, logger, random_seed, num_managers):
        super().__init__(id, group, trade_logging,
                 database, logger, random_seed, num_managers)
        self.name = (group, self.id)
        self.alive = True
        self.mainLedger = Ledger(self, self._haves)
        self.obligationsAndGoodsMailbox = ObligationsAndGoodsMailbox(self)

    def init(self, agent_parameters, sim_parameters):
        self.simulation = sim_parameters

    def add(self, contract) -> None:
        if (contract.getAssetParty() == self):
            # This contract is an asset for me.
            self.mainLedger.addAsset(contract)
        elif (contract.getLiabilityParty() == self):
            # This contract is a liability for me
            self.mainLedger.addLiability(contract)

    def getName(self):
        return str(self.name)

    def getTime(self):
        return self.simulation.time

    def getSimulation(self):
        return self.simulation

    def isAlive(self) -> bool:
        return self.alive

    def addCash(self, amount: np.longdouble) -> None:
        self.mainLedger.inventory.create('money', amount)

    def getCash_(self) -> np.longdouble:
        return self.mainLedger.inventory['money']

    def getMainLedger(self) -> Ledger:
        return self.mainLedger

    def step(self) -> None:
        self.obligationsAndGoodsMailbox.step()

    def sendObligation(self, recipient, obligation: Obligation) -> None:
        if isinstance(obligation, ObligationMessage):
            self.message(recipient.group, recipient.id, '!oblmsg', obligation)
            self.obligationsAndGoodsMailbox.addToObligationOutbox(obligation)
        else:
            msg = ObligationMessage(self, obligation)
            self.message(recipient.group, recipient.id, '!oblmsg', msg)


    def printMailbox(self) -> None:
        self.obligationsAndGoodsMailbox.printMailbox()

    def message(self, receiver, topic, content, overload=None):

        if not isinstance(receiver, tuple):
            receiver = receiver.name
        super().message(receiver[0], receiver[1], topic, content)


    def get_obligation_outbox(self) -> List[Obligation]:
        return self.obligationsAndGoodsMailbox.getObligation_outbox()


class Action:
    def __init__(self, me: Agent) -> None:
        self.me = me
        self.amount = np.longdouble(0.0)

    def perform(self) -> None:
        print("Model.actionsRecorder.recordAction(this); not called because deleted")

    def getAmount(self) -> np.longdouble:
        return self.amount

    def setAmount(self, amount: np.longdouble):
        self.amount = np.longdouble(amount)

    def getTime(self) -> int:
        return self.me.getTime()

    def print(self, actions=None) -> None:
        if actions:
            counter = 1
            for action in actions:
                print("Action", counter, "->", action.getName())
                counter += 1

    def getAgent(self) -> Agent:
        return self.me

    def getSimulation(self):
        return self.me.getSimulation()


class Contract:
    def getAssetParty(self):
        pass

    def getLiabilityParty(self):
        pass

    def getValue(self, me):
        pass

    def getAvailableActions(self, me):
        pass

    def getName(self, me):
        pass


class BankersRounding:
    def bankersRounding(self, value: np.longdouble) -> int:
        s = int(value)
        t = abs(value - s)

        if ((t < 0.5) or (t == 0.5 and s % 2 == 0)):
            return s
        else:
            if (value < 0):
                return s - 1
            else:
                return s + 1
