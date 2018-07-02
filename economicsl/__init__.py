from typing import List, Union
from collections import deque
import numpy as np

from .accounting import Ledger
from .obligations import Obligation
from .accounting import AccountType  # NOQA
from .abce import NotEnoughGoods  # NOQA


class Simulation:
    def __init__(self) -> None:
        self.time = 0
        self.postbox = deque()

    def advance_time(self) -> None:
        self.time += 1

    def process_postbox(self):
        for recipient, msg in self.postbox:
            recipient.receive_message(msg)
        self.postbox.clear()

    def get_time(self) -> int:
        return self.time


class Messenger(object):
    __slots__ = 'mailbox', 'postbox'

    def __init__(self):
        self.mailbox = Mailbox(self)
        self.postbox = None

    def send_obligation(self, recipient, obligation: Obligation) -> None:
        self.postbox.append((recipient, obligation))
        self.mailbox.add_to_obligation_outbox(obligation)

    def receive_message(self, message: Union[Obligation, 'GoodMessage']) -> None:
        self.mailbox.receive_message(message)

    def print_mailbox(self) -> None:
        self.mailbox.print_mailbox()

    def get_obligation_inbox(self) -> List[Obligation]:
        return self.mailbox.get_obligation_inbox()

    def get_obligation_outbox(self) -> List[Obligation]:
        return self.mailbox.get_obligation_outbox()


class Agent(Messenger):
    __slots__ = 'name', 'simulation', 'alive', 'main_ledger'

    def __init__(self, name: str, simulation: Simulation) -> None:
        super().__init__()
        self.name = name
        self.simulation = simulation
        self.postbox = simulation.postbox
        self.alive = True
        self.main_ledger = Ledger(self)

    def add(self, contract) -> None:
        if (contract.get_asset_party() == self):
            # This contract is an asset for me.
            self.main_ledger.add_asset(contract)
        elif (contract.get_liability_party() == self):
            # This contract is a liability for me
            self.main_ledger.add_liability(contract)

    def get_name(self) -> str:
        return self.name

    def get_time(self) -> int:
        return self.simulation.get_time()

    def get_simulation(self) -> Simulation:
        return self.simulation

    def is_alive(self) -> bool:
        return self.alive

    def add_cash(self, amount: np.longdouble) -> None:
        self.main_ledger.add_cash(amount)

    def get_cash_(self) -> np.longdouble:
        return self.main_ledger.inventory.get_cash()

    def get_main_ledger(self) -> Ledger:
        return self.main_ledger

    def step(self) -> None:
        self.mailbox.step()


class Action(object):
    __slots__ = 'me', 'amount'

    def __init__(self, me: Agent) -> None:
        self.me = me
        self.amount = np.longdouble(0.0)

    def perform(self) -> None:
        pass

    def get_amount(self) -> np.longdouble:
        return self.amount

    def set_amount(self, amount: np.longdouble):
        self.amount = np.longdouble(amount)

    def get_time(self) -> int:
        return self.me.get_time()

    def print(self, actions=None) -> None:
        if actions:
            counter = 1
            for action in actions:
                print("Action", counter, "->", action.get_name())
                counter += 1

    def get_agent(self) -> Agent:
        return self.me

    def get_simulation(self) -> Simulation:
        return self.me.get_simulation()


class Trade(Agent):
    def __init__(self, name: str, simulation: Simulation) -> None:
        super().__init__(name, simulation)

    # Trade good one against good two
    def barter(self, trade_partner, name_get, amount_get, value_get, name_give,
               amount_give, value_give) -> None:
        raise NotImplementedError

    def give(self, recipient: Agent, good_name: str, amount_give: np.longdouble) -> None:
        value = self.get_main_ledger().get_physical_thing_value(good_name)
        self.get_main_ledger().destroy(good_name, amount_give)
        good_message = GoodMessage(good_name, amount_give, value)
        self.postbox.append((recipient, good_message))


class Message(object):
    __slots__ = 'sender', 'message', 'topic'

    def __init__(self, sender: Agent, topic: str, message) -> None:
        self.sender = sender
        self.message = message
        self.topic = topic

    def get_sender(self) -> Agent:
        return self.sender

    def get_message(self):
        return self.message

    def get_topic(self) -> str:
        return self.topic


class GoodMessage(object):
    __slots__ = 'good_name', 'amount', 'value'

    def __init__(self, good_name: str, amount: np.longdouble, value: np.longdouble) -> None:
        self.good_name = good_name
        self.amount = np.longdouble(amount)
        self.value = value


class Mailbox(object):
    __slots__ = 'me', 'obligation_unopened', 'obligation_outbox', 'obligation_inbox'

    def __init__(self, me) -> None:
        self.me = me
        self.obligation_unopened = []
        self.obligation_outbox = []
        self.obligation_inbox = []

    def receive_message(self, message) -> None:
        if isinstance(message, Obligation):
            self.obligation_unopened.append(message)

            print("Obligation received. ", message.get_from().get_name(),
                  " must pay ", message.get_amount(), " to ",
                  message.get_to().get_name(),
                  " on timestep ", message.get_time_to_pay())
        elif isinstance(message, GoodMessage):
            # Process goods
            print(message)
            self.me.get_main_ledger().create(message.good_name, message.amount, message.value)
        else:
            # Process cash
            self.me.add_cash(message)

    def add_to_obligation_outbox(self, obligation) -> None:
        self.obligation_outbox.append(obligation)

    def get_matured_obligations(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.obligation_inbox if o.is_due() and
                    not o.is_fulfilled()])

    def get_all_pending_obligations(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.obligation_inbox if not o.is_fulfilled()])

    def get_pending_payments_to_me(self) -> np.longdouble:
        return sum([o.get_amount() for o in self.obligation_outbox if o.is_fulfilled()])

    def fulfil_all_requests(self) -> None:
        for o in self.obligation_inbox:
            if not o.is_fulfilled():
                o.fulfil()

    def fulfil_matured_requests(self) -> None:
        for o in self.obligation_inbox:
            if o.is_due() and not o.is_fulfilled():
                o.fulfil()

    def step(self) -> None:
        # Remove all fulfilled requests
        # and all requests in outbox from agents who have defaulted.
        self.obligation_inbox = [o for o in self.obligation_inbox if not o.fulfilled]
        # PERF o.from_.alive is faster than o.get_from().is_alive()
        self.obligation_outbox = [o for o in self.obligation_outbox if (not o.fulfilled) and o.from_.alive]

        # Move all messages in the obligation_unopened to the obligation_inbox
        self.obligation_inbox += [o for o in self.obligation_unopened if o.has_arrived()]
        self.obligation_unopened = [o for o in self.obligation_unopened if not o.has_arrived()]

    def print_mailbox(self) -> None:
        if ((not self.obligation_unopened) and (not self.obligation_inbox) and
           (not self.obligation_outbox)):
            print("\nObligationsAndGoodsMailbox is empty.")
        else:
            print("\nObligationsAndGoodsMailbox contents:")
            if not (not self.obligation_unopened):
                print("Unopened messages:")
            for o in self.obligation_unopened:
                o.print_obligation()

            if not (not self.obligation_inbox):
                print("Inbox:")
            for o in self.obligation_inbox:
                o.print_obligation()

            if not (not self.obligation_outbox):
                print("Outbox:")
            for o in self.obligation_outbox:
                o.print_obligation()
            print()

    def get_obligation_outbox(self):
        return self.obligation_outbox

    def get_obligation_inbox(self):
        return self.obligation_inbox


class BankersRounding:
    def do_bankers_rounding(self, value: np.longdouble) -> int:
        s = int(value)
        t = abs(value - s)

        if ((t < 0.5) or (t == 0.5 and s % 2 == 0)):
            return s
        else:
            if (value < 0):
                return s - 1
            else:
                return s + 1
