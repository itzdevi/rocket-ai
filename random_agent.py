import agent
import random
import action

class RandomAgent(agent.Agent):
    def get_action(self, state):
        return action.Action(random.random(), random.random() * 2 - 1)