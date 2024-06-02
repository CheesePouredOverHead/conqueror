import gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from tqdm import tqdm
import random
from collections import deque
from gym.envs.registration import register
import matplotlib.pyplot as plt
import rl_utils
from model2 import SheepModel

register(
    id="SheepEnv-v0",
    entry_point="sheepenv6:SheepEnv",
    max_episode_steps=1000,
    reward_threshold=200,
)

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        """
        初始化DQN模型。

        参数：
        - state_size：状态空间的大小。
        - action_size：动作空间的大小。
        """
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, x):
        """
        前向传播函数。

        参数：
        - x：输入张量。

        返回：
        - 输出张量。
        """
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class Agent:
    def __init__(self, state_size, action_size):
        """
        初始化智能体对象。

        参数:
        - state_size (int): 状态空间的维度大小。
        - action_size (int): 动作空间的维度大小。
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=5000)
        self.gamma = 0.9
        self.epsilon = 0.9
        self.epsilon_min = 0.0001
        self.epsilon_decay = 0.995
        self.model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)

    def remember(self, state, action, reward, next_state, done):
        """
        将经验存储到记忆中。

        参数:
        - state (object): 当前状态。
        - action (int): 执行的动作。
        - reward (float): 执行动作后的奖励。
        - next_state (object): 下一个状态。
        - done (bool): 是否达到终止状态。
        """
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        """
        根据当前状态选择动作。

        参数:
        - state (object): 当前状态。

        返回:
        - action (int): 选择的动作。
        """
        # 获取合法动作列表
        legal_actions = [i for i in range(self.action_size) if state['movable_cards'][i] == 1]

        if len(legal_actions) == 0:
            return None
        if np.random.rand() <= self.epsilon:
            return random.choice(legal_actions)
        state_vector = np.concatenate([state["card_num"].flatten(), state['movable_cards'], state["relation"].flatten(), state['stack_positions']])
        state_vector = torch.FloatTensor(state_vector)
        with torch.no_grad():
            act_values = self.model(state_vector)
        act_values_legal = act_values.clone().detach()
        act_values_legal[[i for i in range(self.action_size) if i not in legal_actions]] = float('-inf')
        return torch.argmax(act_values_legal).item()

    def replay(self, batch_size):
        """
        从记忆中随机抽取一批经验进行训练。

        参数:
        - batch_size (int): 批次大小。
        """
        minibatch = random.sample(self.memory, batch_size)

        for state, action, reward, next_state, done in minibatch:
            state = np.concatenate([state["card_num"].flatten(), state['movable_cards'], state["relation"].flatten(), state['stack_positions']])
            state = torch.FloatTensor(state)
            next_state = np.concatenate([next_state["card_num"].flatten(), next_state['movable_cards'], next_state["relation"].flatten(), next_state['stack_positions']])
            next_state = torch.FloatTensor(next_state)
            reward = torch.FloatTensor([reward])
            if done:
                target = reward
            else:
                target = reward + self.gamma * torch.max(self.model(next_state))
            predicted = self.model(state)[action]
            loss = F.mse_loss(predicted, target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

if __name__=='__main__':
    env = gym.make('SheepEnv-v0',floor=4)
    state_size = np.prod(env.observation_space.spaces["movable_cards"].shape) + np.prod(env.observation_space.spaces["stack_positions"].shape) + np.prod(env.observation_space.spaces["card_num"].shape) + np.prod(env.observation_space.spaces["relation"].shape)
    # print(state_size)
    action_size = env.action_space.n
    print(state_size, action_size)
    
    agent = Agent(state_size, action_size)
    # agent.model.load_state_dict(torch.load('model_parameters3.pth'))

    EPISODES = 500
    all_rewards = []
    state = env.reset()
    for e in range(20):
        return_list = []
        with tqdm(total=int(EPISODES / 10), desc='Iteration %d' % e) as pbar:
            # state = env.reset()
            for time in range(int(EPISODES / 10)):
                action = agent.choose_action(state)
                # print(action)
                next_state, reward, done, _ = env.step(action)
                # reward = reward if not done else -10
                # print(reward)
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                return_list.append(reward)
                if done:
                    
                    # print(return_list)
                    # return_list = []
                    state = env.reset()
                if len(agent.memory) > 32:
                    agent.replay(32)

                if (time + 1) % 10 == 0:
                    pbar.set_postfix({
                        'episode':
                        '%d' % (EPISODES / 10 * e + EPISODES + 1),
                        'return':
                        '%.3f' % np.mean(return_list[-10:])
                    })
                pbar.update(1)
        all_rewards+=return_list

        torch.save(agent.model.state_dict(), 'model_with_env6.pth')
        
    episodes_list = list(range(len(all_rewards)))
    plt.plot(episodes_list, all_rewards)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format('SheepEnv-v0'))
    plt.show()

    mv_return = rl_utils.moving_average(all_rewards, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format('SheepEnv-v0'))
    plt.show()