import unittest
import economicsl

from give_agent import GiveAgent
from message_agent import MessageAgent

NUM_AGENTS = 15
ROUNDS = 16


class End2EndTest(unittest.TestCase):
    def test_give(self):
        simulation = economicsl.Simulation()
        giveandreceives = [GiveAgent(str(i), 1, 0, simulation) for i in range(NUM_AGENTS)]
        giveandreceives[0].getMainLedger().addGoods("ball", 2, 5.5)
        print(giveandreceives[0])

        for time in range(ROUNDS):
            print()
            print("Time step:", time)
            print("^^^^^^^^^^^^^")
            for i in range(NUM_AGENTS):
                quantity = giveandreceives[i].getMainLedger().inventory.getGood("ball")
                if quantity > 0.9:
                    print("%d has ball %d" % (i, quantity))
                if i + 1 < NUM_AGENTS:
                    giveandreceives[i].give(giveandreceives[i + 1])
            for a in giveandreceives:
                a.step()
            simulation.advance_time()

    def test_message(self):
        simulation = economicsl.Simulation()
        agents = [MessageAgent("0", None, 0 % 2, simulation)]
        for i in range(1, NUM_AGENTS):
            agents.append(MessageAgent(str(i), agents[-1], i % 2, simulation))
        agents[0].set_friend(agents[-1])
        for time in range(ROUNDS):
            print()
            print("Time step:", time)
            print("^^^^^^^^^^^^^")
            for child in agents:
                child.say()
            for child in agents:
                child.hear()
            for child in agents:
                child.step()
            simulation.advance_time()
