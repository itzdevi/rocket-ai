import torch
from constants import *
import app
import ai_agent
import wandb

def get_advantage_gae(rewards, values, dones, last_val):
        adv = torch.zeros_like(rewards)
        gae = 0
        vals = torch.cat([values, last_val.unsqueeze(0)])
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + GAMMA * vals[t + 1] * (1 - dones[t]) - vals[t]
            gae = delta + GAMMA * LAMBDA * (1 - dones[t]) * gae
            adv[t] = gae
        return adv

class TrainerAgent(ai_agent.AIAgent):
    def __init__(self):
        super().__init__()
        self.next_action = None

    def get_action(self, state):
        if self.next_action:
            a = self.next_action
            self.next_action = None
            return a
        return super().get_action(state)

agent = TrainerAgent()
agent.model.cuda()
optimizer = torch.optim.Adam(agent.model.parameters(), lr=LEARNING_RATE)
a = app.App(agent)
run = wandb.init(
    entity="ronshan4u-openai",
    project="rocket",
)

MAX_ITERATIONS = 1000000
CHECKPOINT_INTERVAL = 10
for update in range(MAX_ITERATIONS):
    obs_buf, act_buf, logp_buf = [], [], []
    rew_buf, val_buf, done_buf = [], [], []

    state = torch.from_numpy(a.env.get_state()()).cuda()

    while len(obs_buf) < ROLLOUT_SIZE:
        with torch.no_grad():
            dist_cont, value = agent.model.forward(state)
            action = dist_cont.sample()
            logp = dist_cont.log_prob(action).sum(-1)

        agent.next_action = ai_agent.action.Action(action[0].item(), action[1].item())
        a.tick()
        # a.draw()
        next_state = torch.from_numpy(a.env.get_state()()).cuda()
        reward = torch.tensor(a.env.get_reward())
        done = torch.tensor(a.env.get_done())

        obs_buf.append(state)
        act_buf.append(action)
        logp_buf.append(logp)
        rew_buf.append(reward)
        val_buf.append(value)
        done_buf.append(done)

        # if len(obs_buf) % 100 == 0:
        #     print(f"rollout size: {len(obs_buf)}")

        if not done:
            state = next_state
        else:
            a.env.reset_environment()
            state = torch.from_numpy(a.env.get_state()()).cuda()

    with torch.no_grad():
        _, last_val = agent.model.forward(state)

    rewards = torch.stack(rew_buf).cuda()
    values = torch.stack(val_buf).cuda()
    dones = torch.stack(done_buf).float().cuda()
    advantages = get_advantage_gae(rewards, values, dones, last_val).cuda()
    returns = advantages + values
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    obs_batch = torch.stack(obs_buf).cuda()
    old_logp = torch.stack(logp_buf).cuda()

    cont_actions = torch.stack(act_buf).cuda()

    # shuffle
    batch_size = obs_batch.size(0)

    for epoch in range(EPOCHS):
        indices = torch.randperm(batch_size)
        for start in range(0, batch_size, MINIBATCH_SIZE):
            end = start + MINIBATCH_SIZE
            mb_idx = indices[start:end]

            dist_cont, value = agent.model.forward(obs_batch[mb_idx])

            cont_logp = dist_cont.log_prob(cont_actions[mb_idx]).sum(-1)
            logp = cont_logp

            ratio = torch.exp(logp - old_logp[mb_idx])
            surr1 = ratio * advantages[mb_idx]
            surr2 = torch.clamp(ratio, 1 - CLIP_EPSILON, 1 + CLIP_EPSILON) * advantages[mb_idx]
            policy_loss = -torch.min(surr1, surr2).mean()

            value_loss = (returns[mb_idx] - value).pow(2).mean()

            entropy = (
                dist_cont.entropy().sum(-1).mean()
            )
            
            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            mean_distance_error = torch.hypot(obs_batch[:, 0] * 300, obs_batch[:, 1] * 600).mean()
            run.log({ "total_loss": loss.item(), "value_loss": value_loss.item(), "policy_loss": policy_loss.item(), "entropy": entropy.item(), "returns": returns.mean().item(), "rewards": rewards.mean().item(), "mean_distance_error": mean_distance_error.item() })

    if update % CHECKPOINT_INTERVAL == 0:
        print("saving checkpoint")
        torch.save(agent.model.state_dict(), "./model/model.pt")