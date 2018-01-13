import economicsl


class MessageAgent(economicsl.Agent):
    def __init__(self, name, friend, odd_or_even, simulation):
        super().__init__(name, simulation)
        self.name = name
        self.odd_or_even = odd_or_even
        self.friend = friend

    def say(self):
        pass
        # self.message(self.friend, "hello", self.odd_or_even)

    def hear(self):
        pass
        # for msg in self.get_messages():
        #     print(msg.getMessage())

    def set_friend(self, friend):
        self.friend = friend
