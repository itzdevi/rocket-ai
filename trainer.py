import torch
from constants import *
import app
import ai_agent
import wandb
import os

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
if os.path.exists(CHECKPOINT_LOAD_PATH):
    agent.model.load_state_dict(torch.load(CHECKPOINT_LOAD_PATH, weights_only=False))
    print(f"Loaded checkpoint from {CHECKPOINT_LOAD_PATH}")
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

    terminal_stats = {
        "successes": 0,
        "crashes": 0,
        "timeouts": 0,
        "terminal_angles": [],
        "terminal_h_speeds": [],
        "terminal_v_speeds": [],
        "terminal_x_dists": [],
        "terminal_y_dists": []
    }

    while len(obs_buf) < ROLLOUT_SIZE:
        with torch.no_grad():
            dist_cont, value = agent.model.forward(state)
            action = dist_cont.sample()
            logp = dist_cont.log_prob(action).sum(-1)

        agent.next_action = ai_agent.action.Action(action[0].item(), action[1].item())
        a.tick()
        a.draw()
        next_state = torch.from_numpy(a.env.get_state()()).float().cuda()
        reward = torch.tensor(a.env.get_reward(), dtype=torch.float32, device='cuda')
        done = torch.tensor(a.env.get_done(), dtype=torch.float32, device='cuda')

        obs_buf.append(state)
        act_buf.append(action)
        logp_buf.append(logp)
        rew_buf.append(reward)
        val_buf.append(value)
        done_buf.append(done)

        if not done.item():
            state = next_state
        else:
            terminal = next_state.detach().cpu().numpy()
            terminal_angle = abs(terminal[2]) * 180.0
            terminal_h_speed = abs(terminal[3] * 50.0)
            terminal_v_speed = abs(terminal[4] * 50.0)
            terminal_x_dist = abs(terminal[0]) * 800.0
            terminal_y_dist = abs(terminal[1]) * 1500.0

            terminal_stats["terminal_angles"].append(terminal_angle)
            terminal_stats["terminal_h_speeds"].append(terminal_h_speed)
            terminal_stats["terminal_v_speeds"].append(terminal_v_speed)
            terminal_stats["terminal_x_dists"].append(terminal_x_dist)
            terminal_stats["terminal_y_dists"].append(terminal_y_dist)

            if terminal_x_dist < 4.0 and terminal_v_speed < 3.0 and terminal_angle < 15.0 and terminal_h_speed < 3.0:
                terminal_stats["successes"] += 1
            elif terminal_y_dist < 20.0:
                terminal_stats["crashes"] += 1
            else:
                terminal_stats["timeouts"] += 1

            a.env.reset_environment()
            state = torch.from_numpy(a.env.get_state()()).float().cuda()

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
            
            loss = policy_loss + 0.5 * value_loss - 0.005 * entropy

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(agent.model.parameters(), 0.5)
            optimizer.step()

            mean_distance_error = torch.hypot(obs_batch[:, 0] * 300, obs_batch[:, 1] * 600).mean()
            total_terminals = terminal_stats["successes"] + terminal_stats["crashes"] + terminal_stats["timeouts"]
            run.log({
                "total_loss": loss.item(),
                "value_loss": value_loss.item(),
                "policy_loss": policy_loss.item(),
                "entropy": entropy.item(),
                "returns": returns.mean().item(),
                "rewards": rewards.mean().item(),
                "mean_distance_error": mean_distance_error.item(),
                "mean_abs_rotation": obs_batch[:, 2].abs().mean().item(),
                "mean_abs_ang_velocity": obs_batch[:, 5].abs().mean().item(),
                "mean_abs_roll": obs_batch[:, 7].abs().mean().item(),
                "mean_throttle": obs_batch[:, 6].mean().item(),
                "success_rate": terminal_stats["successes"] / max(1, total_terminals),
                "terminal_angle_mean": sum(terminal_stats["terminal_angles"]) / max(1, len(terminal_stats["terminal_angles"])),
                "terminal_h_speed_mean": sum(terminal_stats["terminal_h_speeds"]) / max(1, len(terminal_stats["terminal_h_speeds"])),
                "terminal_v_speed_mean": sum(terminal_stats["terminal_v_speeds"]) / max(1, len(terminal_stats["terminal_v_speeds"])),
                "terminal_x_dist_mean": sum(terminal_stats["terminal_x_dists"]) / max(1, len(terminal_stats["terminal_x_dists"])),
                "terminal_y_dist_mean": sum(terminal_stats["terminal_y_dists"]) / max(1, len(terminal_stats["terminal_y_dists"])),
                "terminal_successes": terminal_stats["successes"],
                "terminal_crashes": terminal_stats["crashes"],
                "terminal_timeouts": terminal_stats["timeouts"]
            })

    if update % CHECKPOINT_INTERVAL == 0:
        print("saving checkpoint")
        torch.save(agent.model.state_dict(), CHECKPOINT_SAVE_PATH)