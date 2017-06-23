class Obligation:
    def __init__(self, contract, amount, timeLeftToPay, simulation):
        self.amount = amount

        self.from_ = contract.getLiabilityParty()
        self.to = contract.getAssetParty()

        self.timeToOpen = simulation.getTime() + 1
        self.timeToPay = simulation.getTime() + timeLeftToPay
        self.timeToReceive = self.timeToPay + 1
        self.simulation = simulation

        assert self.timeToPay >= self.timeToOpen

        self.fulfilled = False

    def fulfil(self):
        pass

    def getAmount(self):
        return self.amount

    def isFulfilled(self):
        return self.fulfilled

    def hasArrived(self):
        return self.simulation.getTime() == self.timeToOpen

    def isDue(self):
        return self.simulation.getTime() == self.timeToPay

    def getFrom(self):
        return self.from_

    def getTo(self):
        return self.to

    def setFulfilled(self):
        self.fulfilled = True

    def setAmount(self, amount):
        self.amount = amount

    def getTimeToPay(self):
        return self.timeToPay

    def getTimeToReceive(self):
        return self.timeToReceive

    def printObligation(self):
        print("Obligation from ", self.getFrom().getName(), " to pay ",
              self.getTo().getName(), " an amount ", self.getAmount(),
              " on timestep ", self.getTimeToPay(), " to arrive by timestep ",
              self.getTimeToReceive())


class ObligationMessage:
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message
        self._is_read = False

    def getSender(self):
        return self.sender

    def getMessage(self):
        self._is_read = True
        return self.message

    def is_read(self):
        return self._is_read


class ObligationsAndGoodsMailbox:
    def __init__(self):
        self.obligation_unopened = []
        self.obligation_outbox = []
        self.obligation_inbox = []
        self.obligationMessage_unopened = []
        self.obligationMessage_inbox = []
        self.goods_inbox = []

    def receiveObligation(self, obligation):
        self.obligation_unopened.append(obligation)

        print("Obligation sent. ", obligation.getFrom().getName(),
              " must pay ", obligation.getAmount(), " to ",
              obligation.getTo().getName(),
              " on timestep ", obligation.getTimeToPay())

    def receiveMessage(self, msg):
        self.obligationMessage_unopened.append(msg)
        # print("ObligationMessage sent. " + msg.getSender().getName() +
        #        " message: " + msg.getMessage());

    def receiveGoodMessage(self, good_message):
        print(good_message)
        self.goods_inbox.append(good_message)
        # print("ObligationMessage sent. " + msg.getSender().getName() +
        #        " message: " + msg.getMessage());

    def addToObligationOutbox(self, obligation):
        self.obligation_outbox.append(obligation)

    def getMaturedObligations(self):
        return sum([o.getAmount() for o in self.obligation_inbox if o.isDue() and not o.isFulfilled()])

    def getAllPendingObligations(self):
        return sum([o.getAmount() for o in self.obligation_inbox if not o.isFulfilled()])

    def getPendingPaymentsToMe(self):
        return sum([o.getAmount() for o in self.obligation_outbox if o.isFulfilled()])

    def fulfilAllRequests(self):
        for o in self.obligation_inbox:
            if not o.isFulfilled():
                o.fulfil()

    def fulfilMaturedRequests(self):
        for o in self.obligation_inbox:
            if o.isDue() and not o.isFulfilled():
                o.fulfil()

    def step(self):
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

    def printMailbox(self):
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
