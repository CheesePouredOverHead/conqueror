import torch
import gym
from gym.envs.registration import register
import numpy as np
from sheepenv import SheepEnv
from dqn import DQN

register(
    id="SheepEnv-v0",
    entry_point="sheepenv:SheepEnv",
    max_episode_steps=1000,
    reward_threshold=200,
)
# 创建你的环境
env = SheepEnv()  # 请替换为你的环境的实际创建语句


# 加载模型
model = DQN(32767,180)  # 请替换为你的模型类的实际创建语句

# 加载状态字典
state_dict = torch.load("model_parameters.pth")
model.load_state_dict(state_dict)

# 获取一个观察值
observation = env.reset()  # 请替换为你的观察值获取语句
part1 = torch.tensor(observation["card_num"])  # 请替换 'key1' 为你需要的键
part2 = torch.tensor(observation["movable_cards"])  # 请替换 'key2' 为你需要的键
part3 = torch.tensor(observation["relation"])
part4 = torch.tensor(observation["stack_positions"])
part3 = part3.view(-1)
# 将多个部分合并成一个张量
observation_tensor = torch.cat([part1, part2,part3,part4], dim=-1)
observation_tensor=observation_tensor.float()

action_probs = model(observation_tensor)

# 选择概率最高的动作
action = torch.argmax(action_probs).item()

print(action)