from typing import List
import numpy as np

from .accounting import Ledger
from .obligations import Obligation, ObligationMessage, Mailbox
from .accounting import AccountType  # NOQA
from .abce import NotEnoughGoods  # NOQA


class Simulation:
    def __init__(self) -> None:
        self.time = 0

    def advance_time(self) -> None:
        self.time += 1

    def getTime(self) -> int:
        return self.time


class Agent:
    def __init__(self, name: str, simulation: Simulation) -> None:
        self.name = name
        self.simulation = simulation
        self.alive = True
        self.mainLedger = Ledger(self)
        self.mailbox = Mailbox(self)

    def add(self, contract) -> None:
        if (contract.getAssetParty() == self):
            # This contract is an asset for me.
            self.mainLedger.addAsset(contract)
        elif (contract.getLiabilityParty() == self):
            # This contract is a liability for me
            self.mainLedger.addLiability(contract)

    def getName(self) -> str:
        return self.name

    def getTime(self) -> int:
        return self.simulation.getTime()

    def getSimulation(self) -> Simulation:
        return self.simulation

    def isAlive(self) -> bool:
        return self.alive

    def addCash(self, amount: np.longdouble) -> None:
        self.mainLedger.addCash(amount)

    def getCash_(self) -> np.longdouble:
        return self.mainLedger.inventory.getCash()

    def getMainLedger(self) -> Ledger:
        return self.mainLedger

    def step(self) -> None:
        self.mailbox.step()

    def sendObligation(self, recipient, obligation) -> None:
        if isinstance(obligation, Obligation):
            recipient.receiveObligation(obligation)
            self.mailbox.addToObligationOutbox(obligation)
        else:
            msg = ObligationMessage(self, obligation)
            recipient.receiveMessage(msg)

    def receiveObligation(self, obligation: Obligation) -> None:
        self.mailbox.receiveObligation(obligation)

    def receiveMessage(self, msg: ObligationMessage) -> None:
        self.mailbox.receiveMessage(msg)

    def receiveGoodMessage(self, good_message) -> None:
        self.mailbox.receiveGoodMessage(good_message)

    def printMailbox(self) -> None:
        self.mailbox.printMailbox()

    def get_obligation_inbox(self) -> List[Obligation]:
        return self.mailbox.getObligation_inbox()

    def get_obligation_outbox(self) -> List[Obligation]:
        return self.mailbox.getObligation_outbox()


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

    def getSimulation(self) -> Simulation:
        return self.me.getSimulation()


class Trade(Agent):
    def __init__(self, name: str, simulation: Simulation) -> None:
        super().__init__(name, simulation)

    # Trade good one against good two
    def barter(self, trade_partner, name_get, amount_get, value_get, name_give,
               amount_give, value_give) -> None:
        raise NotImplementedError

    def give(self, recipient: Agent, good_name: str, amount_give: np.longdouble) -> None:
        value = self.getMainLedger().getPhysicalThingValue(good_name)
        self.getMainLedger().destroy(good_name, amount_give)
        good_message = GoodMessage(good_name, amount_give, value)
        recipient.receiveGoodMessage(good_message)


class Message:
    def __init__(self, sender: Agent, topic: str, message) -> None:
        self.sender = sender
        self.message = message
        self.topic = topic

    def getSender(self) -> Agent:
        return self.sender

    def getMessage(self):
        return self.message

    def getTopic(self) -> str:
        return self.topic


class GoodMessage:
    def __init__(self, good_name: str, amount: np.longdouble, value: np.longdouble) -> None:
        self.good_name = good_name
        self.amount = np.longdouble(amount)
        self.value = value


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
