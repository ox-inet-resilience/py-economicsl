from typing import List
from .accounting import Ledger
from .obligations import ObligationMessage, ObligationsAndGoodsMailbox

from .obligations import Obligation
from .accounting import doubleEntry, AccountType
from .abce import NotEnoughGoods


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
        self.mailbox = Mailbox()
        self.mainLedger = Ledger(self)
        self.obligationsAndGoodsMailbox = ObligationsAndGoodsMailbox()

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

    def addCash(self, amount) -> None:
        self.mainLedger.addCash(amount)

    def getCash_(self) -> float:
        return self.mainLedger.inventory.getCash()

    def getTotalCash(self) -> float:
        return self.mainLedger.getCash()

    def getMainLedger(self) -> Ledger:
        return self.mainLedger

    def step(self) -> None:
        for good_message in self.obligationsAndGoodsMailbox.goods_inbox:
            self.getMainLedger().create(good_message.good_name, good_message.amount, good_message.value)
        self.obligationsAndGoodsMailbox.goods_inbox.clear()
        self.obligationsAndGoodsMailbox.step()
        self.mailbox.step()

    def sendObligation(self, recipient, obligation: Obligation) -> None:
        if isinstance(obligation, ObligationMessage):
            recipient.receiveObligation(obligation)
            self.obligationsAndGoodsMailbox.addToObligationOutbox(obligation)
        else:
            msg = ObligationMessage(self, obligation)
            recipient.receiveMessage(msg)

    def receiveObligation(self, obligation: Obligation) -> None:
        self.obligationsAndGoodsMailbox.receiveObligation(obligation)

    def receiveMessage(self, msg: ObligationMessage) -> None:
        if isinstance(msg, ObligationMessage):
            self.obligationsAndGoodsMailbox.receiveMessage(msg)
        else:
            self.mailbox.receiveMessage(msg)

    def receiveGoodMessage(self, good_message) -> None:
        self.obligationsAndGoodsMailbox.receiveGoodMessage(good_message)

    def printMailbox(self) -> None:
        self.obligationsAndGoodsMailbox.printMailbox()

    def message(self, receiver, topic, content):
        message = Message(self, topic, content)
        receiver.receiveMessage(message)
        return message

    def get_messages(self, topic=None):
        return self.mailbox.get_messages(topic)

    def get_obligation_inbox(self) -> List[Obligation]:
        return self.obligationsAndGoodsMailbox.getObligation_inbox()

    def get_obligation_outbox(self) -> List[Obligation]:
        return self.obligationsAndGoodsMailbox.getObligation_outbox()


class Action:
    def __init__(self, me: Agent) -> None:
        self.me = me
        self.amount = 0.0

    def perform(self) -> None:
        print("Model.actionsRecorder.recordAction(this); not called because deleted")

    def getAmount(self):
        return self.amount

    def setAmount(self, amount: float):
        self.amount = amount

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

    def give(self, recipient: Agent, good_name: str, amount_give: float) -> None:
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


class Mailbox:
    def __init__(self) -> None:
        self.message_unopened = []
        self.message_inbox = []

    def receiveMessage(self, msg) -> None:
        self.message_unopened.append(msg)
        # print("ObligationMessage sent. " + msg.getSender().getName() +
        #        " message: " + msg.getMessage());

    def step(self) -> None:
        # Move all messages in the obligation_unopened to the obligation_inbox
        self.message_inbox += list(self.message_unopened)

        self.message_unopened = []

        # Move all messages in the obligation_unopened to the obligation_inbox

    def get_messages(self, topic=None) -> List[Message]:
        messages = []
        if not topic:
            messages = self.message_inbox
            self.message_inbox = []
        else:
            # TODO this is probably fucking inefficient
            for message in list(self.message_inbox):
                if message.getTopic() == topic:
                    messages.append(message)
                    self.message_inbox.remove(message)
        return messages


class GoodMessage:
    def __init__(self, good_name: str, amount: float, value: float) -> None:
        self.good_name = good_name
        self.amount = amount
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
    def bankersRounding(self, value: float) -> int:
        s = int(value)
        t = abs(value - s)

        if ((t < 0.5) or (t == 0.5 and s % 2 == 0)):
            return s
        else:
            if (value < 0):
                return s - 1
            else:
                return s + 1
