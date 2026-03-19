import agent
import ai_model
import action
import torch

class AIAgent(agent.Agent):
    def __init__(self, model_path=None):
        self.model = ai_model.PPOModel()
        if model_path:
            self.model.load_state_dict(torch.load(model_path, weights_only=False))
        self.next_action = None

    def get_action(self, state):
        if self.next_action:
            a = self.next_action
            self.next_action = None
            return a

        tensor_state = torch.from_numpy(state())
        if next(self.model.parameters()).is_cuda:
            tensor_state = tensor_state.cuda()
        dist_cont = self.model.forward(tensor_state)
        vals = dist_cont[0].sample()
        return action.Action(vals[0].item(), vals[1].item())
