from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from economicsl import Agent


# Used for Mypy typing purpose
class AbstractMessage:
    pass


class Message(AbstractMessage):
    __slots__ = "sender", "message", "topic"

    def __init__(self, sender: "Agent", topic: str, message) -> None:
        self.sender = sender
        self.message = message
        self.topic = topic


class GoodMessage(AbstractMessage):
    __slots__ = "good_name", "amount", "valuation"

    def __init__(self, good_name: str, amount: float, valuation: float) -> None:
        self.good_name = good_name
        self.amount = float(amount)
        self.valuation = valuation


class Obligation(AbstractMessage):
    __slots__ = (
        "amount",
        "from_",
        "to",
        "time_to_open",
        "time_to_pay",
        "time_to_receive",
        "simulation",
        "fulfilled",
    )

    def __init__(self, contract, amount: float, timeLeftToPay: int) -> None:
        self.amount = float(amount)

        self.from_ = contract.get_liability_party()
        self.to = contract.get_asset_party()

        # there is only one simulation shared by all agents
        self.simulation = self.from_.get_simulation()
        self.time_to_open = self.simulation.get_time() + 1
        self.time_to_pay = self.simulation.get_time() + timeLeftToPay
        self.time_to_receive = self.time_to_pay + 1

        assert self.time_to_pay >= self.time_to_open

        self.fulfilled = False

    def fulfil(self):
        pass

    def get_amount(self) -> float:
        return self.amount

    def is_fulfilled(self) -> bool:
        return self.fulfilled

    def has_arrived(self) -> bool:
        return self.simulation.get_time() == self.time_to_open

    def is_due(self) -> bool:
        return self.simulation.get_time() == self.time_to_pay

    def get_from(self):
        return self.from_

    def get_to(self):
        return self.to

    def set_fulfilled(self) -> None:
        self.fulfilled = True

    def set_amount(self, amount) -> None:
        self.amount = amount

    def get_time_to_pay(self) -> int:
        return self.time_to_pay

    def get_time_to_receive(self) -> int:
        return self.time_to_receive

    def print_obligation(self) -> None:
        print(
            "Obligation from ",
            self.get_from().get_name(),
            " to pay ",
            self.get_to().get_name(),
            " an amount ",
            self.get_amount(),
            " on timestep ",
            self.get_time_to_pay(),
            " to arrive by timestep ",
            self.get_time_to_receive(),
        )
