import state
import action

class Agent:
    def get_action(self, state: state.State) -> action.Action:
        ...