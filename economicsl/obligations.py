import numpy as np


class Obligation:
    def __init__(self, contract, amount: np.longdouble, timeLeftToPay: int) -> None:
        self.amount = np.longdouble(amount)

        self.from_ = contract.getLiabilityParty()
        self.to = contract.getAssetParty()

        # there is only one simulation shared by all agents
        self.simulation = self.from_.getSimulation()
        self.timeToOpen = self.simulation.getTime() + 1
        self.timeToPay = self.simulation.getTime() + timeLeftToPay
        self.timeToReceive = self.timeToPay + 1

        assert self.timeToPay >= self.timeToOpen

        self.fulfilled = False

    def fulfil(self):
        pass

    def getAmount(self) -> np.longdouble:
        return self.amount

    def isFulfilled(self) -> bool:
        return self.fulfilled

    def hasArrived(self) -> bool:
        return self.simulation.getTime() == self.timeToOpen

    def isDue(self) -> bool:
        return self.simulation.getTime() == self.timeToPay

    def getFrom(self):
        return self.from_

    def getTo(self):
        return self.to

    def setFulfilled(self) -> None:
        self.fulfilled = True

    def setAmount(self, amount) -> None:
        self.amount = amount

    def getTimeToPay(self) -> int:
        return self.timeToPay

    def getTimeToReceive(self) -> int:
        return self.timeToReceive

    def printObligation(self) -> None:
        print("Obligation from ", self.getFrom().getName(), " to pay ",
              self.getTo().getName(), " an amount ", self.getAmount(),
              " on timestep ", self.getTimeToPay(), " to arrive by timestep ",
              self.getTimeToReceive())


class ObligationMessage:
    def __init__(self, sender, message) -> None:
        self.sender = sender
        self.message = message
        self._is_read = False

    def getSender(self):
        return self.sender

    def getMessage(self):
        self._is_read = True
        return self.message

    def is_read(self) -> bool:
        return self._is_read


class ObligationsAndGoodsMailbox:
    def __init__(self, owner) -> None:
        self.obligation_unopened = []
        self.obligation_outbox = []
        self.obligation_inbox = []
        self.obligationMessage_unopened = []
        self.obligationMessage_inbox = []
        self.goods_inbox = []
        self.owner = owner


    def addToObligationOutbox(self, obligation) -> None:
        self.obligation_outbox.append(obligation)

    def getMaturedObligations(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_inbox if o.isDue() and not o.isFulfilled()])

    def getAllPendingObligations(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_inbox if not o.isFulfilled()])

    def getPendingPaymentsToMe(self) -> np.longdouble:
        return sum([o.getAmount() for o in self.obligation_outbox if o.isFulfilled()])

    def fulfilAllRequests(self) -> None:
        for o in self.obligation_inbox:
            if not o.isFulfilled():
                o.fulfil()

    def fulfilMaturedRequests(self) -> None:
        for o in self.obligation_inbox:
            if o.isDue() and not o.isFulfilled():
                o.fulfil()

    def step(self) -> None:
        self.obligation_inbox.extend(self.owner.get_messages('!oblmsg'))
        # Remove all fulfilled requests
        self.obligation_inbox = [o for o in self.obligation_inbox if not o.isFulfilled()]
        self.obligation_outbox = [o for o in self.obligation_outbox if not o.isFulfilled()]

        # Remove all requests from agents who have defaulted.
        # TODO should be in model not in the library
        self.obligation_outbox = [o for o in self.obligation_outbox if o.getFrom().isAlive()]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.obligation_inbox += [o for o in self.obligation_unopened if o.hasArrived()]
        self.obligation_unopened = [o for o in self.obligation_unopened if not o.hasArrived()]

        # Remove all fulfilled requests
        self.obligationMessage_inbox = [o for o in self.obligationMessage_inbox if not o.is_read()]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.obligationMessage_inbox += list(self.obligationMessage_unopened)
        self.obligationMessage_unopened = []

        # Remove all fulfilled requests
        assert not self.goods_inbox

        # Move all messages in the obligation_unopened to the obligation_inbox

    def printMailbox(self) -> None:
        if ((not self.obligation_unopened) and (not self.obligation_inbox) and
           (not self.obligation_outbox)):
            print("\nObligationsAndGoodsMailbox is empty.")
        else:
            print("\nObligationsAndGoodsMailbox contents:")
            if not (not self.obligation_unopened):
                print("Unopened messages:")
            for o in self.obligation_unopened:
                o.printObligation()

            if not (not self.obligation_inbox):
                print("Inbox:")
            for o in self.obligation_inbox:
                o.printObligation()

            if not (not self.obligation_outbox):
                print("Outbox:")
            for o in self.obligation_outbox:
                o.printObligation()
            print()

    def getMessageInbox(self):
        return self.obligationMessage_inbox

    def getObligation_outbox(self):
        return self.obligation_outbox

    def getObligation_inbox(self):
        return self.obligation_inbox
