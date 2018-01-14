from typing import List, Union
import numpy as np

from .accounting import Ledger
from .obligations import Obligation, Mailbox
from .accounting import AccountType  # NOQA
from .abce import NotEnoughGoods  # NOQA


class Simulation:
    def __init__(self) -> None:
        self.time = 0

    def advance_time(self) -> None:
        self.time += 1

    def get_time(self) -> int:
        return self.time


class Agent:
    def __init__(self, name: str, simulation: Simulation) -> None:
        self.name = name
        self.simulation = simulation
        self.alive = True
        self.main_ledger = Ledger(self)
        self.mailbox = Mailbox(self)

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

    def send_obligation(self, recipient, obligation: Obligation) -> None:
        recipient.receive_message(obligation)
        self.mailbox.add_to_obligation_outbox(obligation)

    def receive_message(self, message: Union[Obligation, 'GoodMessage']) -> None:
        self.mailbox.receive_message(message)

    def print_mailbox(self) -> None:
        self.mailbox.print_mailbox()

    def get_obligation_inbox(self) -> List[Obligation]:
        return self.mailbox.get_obligation_inbox()

    def get_obligation_outbox(self) -> List[Obligation]:
        return self.mailbox.get_obligation_outbox()


class Action:
    def __init__(self, me: Agent) -> None:
        self.me = me
        self.amount = np.longdouble(0.0)

    def perform(self) -> None:
        print("Model.actionsRecorder.recordAction(this); not called because deleted")

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
        recipient.receive_message(good_message)


class Message:
    def __init__(self, sender: Agent, topic: str, message) -> None:
        self.sender = sender
        self.message = message
        self.topic = topic
        self._is_read = False

    def get_sender(self) -> Agent:
        return self.sender

    def get_message(self):
        self._is_read = True
        return self.message

    def get_topic(self) -> str:
        return self.topic

    def is_read(self) -> bool:
        return self._is_read


class GoodMessage:
    def __init__(self, good_name: str, amount: np.longdouble, value: np.longdouble) -> None:
        self.good_name = good_name
        self.amount = np.longdouble(amount)
        self.value = value


class Contract:
    def get_asset_party(self):
        pass

    def get_liability_party(self):
        pass

    def get_value(self, me):
        pass

    def get_available_actions(self, me):
        pass

    def get_name(self, me):
        pass


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
