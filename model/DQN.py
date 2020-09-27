import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

from config import Config
'''
TODO: add DEBUG mode config
'''
DEBUG = False


def train(model,
          state,
          q_target,
          learningRate,
          batch_size,
          epochs=1,
          verbose=1):
    if DEBUG:
        print("state.shape:{}, q_target.shape:{}".format(
            state.shape, q_target.shape))
        print("batchsize:{}".format(batch_size))

    loss_fc = nn.MSELoss().cuda()
    # loss_fc = nn.CrossEntropyLoss().cuda()
    optimizer = torch.optim.SGD(model.parameters(),
                                lr=learningRate,
                                momentum=0.9)

    total_loss = 0
    for epoch in range(epochs):
        optimizer.zero_grad()
        result = model(state)
        loss = loss_fc(result, q_target)
        total_loss += loss
        loss.backward()
        optimizer.step()

        if verbose:
            message = "[in train] epoch{}, loss:{}".format(epoch, loss)
            print(message)

    return total_loss


class ResNet(nn.Module):
    def __init__(self, state_size, n_actions):
        super(ResNet, self).__init__()
        self.h1 = nn.Linear(state_size, 64)
        self.h2 = nn.Linear(64, 64)
        self.h3 = nn.Linear(64, 64)
        self.h4 = nn.Linear(64, 64)
        self.h5 = nn.Linear(64, 64)
        self.h6 = nn.Linear(64, 64)
        self.out = nn.Linear(64, n_actions)

    def forward(self, x):
        h1 = F.relu(self.h1(x))
        h2 = F.relu(self.h2(h1))

        h3 = F.relu(self.h3(h2))
        h4 = F.relu(self.h4(h3)) + h2

        h5 = F.relu(self.h5(h4))
        h6 = F.relu(self.h6(h5)) + h4

        return self.out(h6)


class DQN(nn.Module):
    def __init__(self):

        super(DQN, self).__init__()
        cfg = Config()
        self.state_size = cfg.state_size
        self.n_actions = cfg.n_actions
        # self.n_nodes = cfg.n_nodes
        self.memory_size = cfg.memory_size
        self.replace_target_iter = cfg.replace_target_iter
        self.batch_size = cfg.batch_size
        self.learning_rate = cfg.learning_rate
        self.gamma = cfg.gamma
        self.epsilon = cfg.epsilon
        self.epsilon_min = cfg.epsilon_min
        self.epsilon_decay = cfg.epsilon_decay
        self.loadModel = cfg.loadModel
        self.lossHitory = []

        # self.memory = torch.zeros(self.memory_size, self.state_size*2+2)
        self.memory = np.zeros((self.memory_size, self.state_size * 2 + 2))
        self.learn_step_counter = 0
        self.memory_couter = 0

        self.model = ResNet(self.state_size, self.n_actions).cuda()
        self.target_model = ResNet(self.state_size, self.n_actions).cuda()
        self.decisionCount = 0
        self.maxRandomDecisionCount = cfg.maxRandomDecisionCount

    def choose_action(self, state):
        state = state[np.newaxis, :]
        self.decisionCount += 1
        if not self.loadModel:
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(self.epsilon_min, self.epsilon)
            # if np.random.random() < self.epsilon:
            #     return np.random.randint(0, 2)
            if self.decisionCount < self.maxRandomDecisionCount:
                return np.random.randint(0, 2)

        state = Variable(torch.from_numpy(state.astype(float))).float().cuda()
        action_values = self.model(state)
        # print("state:{}, state.shape:{}".format(state, state.shape))
        # print("action :", action_values)
        return torch.argmax(action_values)

    def forward(self):
        batch_memory = self.memory
        state = batch_memory[:, :self.state_size]
        action = batch_memory[:, self.state_size].astype(int)
        reward = batch_memory[:, self.state_size + 1]
        next_state = batch_memory[:, -self.state_size:]

        q_eval = self.model.forward(state)
        q_next = self.target_model.forward(state)

        q_target = reward + self.gamma * torch.max(q_next, axis=1)
        return (q_eval, q_target)

    def store_transition(self, s, a, r, s_):  # s_: next_state
        if not hasattr(self, 'memory_couter'):
            self.memory_couter = 0
        transition = np.concatenate((s, [a, r], s_))
        index = self.memory_couter % self.memory_size

        self.memory[index, :] = transition
        self.memory_couter += 1

    def pretrain_learn(self, state):
        state = state[np.newaxis, :]
        init_value = 0.5 / (1 - self.gamma)
        q_target = np.ones(3) * init_value
        q_target = q_target[np.newaxis, :]

        train(self.model,
              state,
              q_target,
              self.learning_rate,
              self.batch_size,
              epochs=1,
              verbose=0)

    def repalce_target_parameters(self):
        model_state_dict = self.model.state_dict()
        self.target_model.load_state_dict(model_state_dict)

    def learn(self):
        # check to update target netowrk parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.repalce_target_parameters()  # iterative target model
        self.learn_step_counter += 1

        # sample batch memory from all memory
        if self.memory_couter > self.memory_size:
            sample_index = np.random.choice(self.memory_size,
                                            size=self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_couter,
                                            size=self.batch_size)
        batch_memory = self.memory[sample_index, :]

        # batch memory row: [s, a, r1, r2, s_]
        # number of batch memory: batch size
        # extract state, action, reward, reward2, next_state from batch memory
        state = batch_memory[:, :self.state_size]
        action = batch_memory[:, self.state_size].astype(int)  # float -> int
        reward = batch_memory[:, self.state_size + 1]
        next_state = batch_memory[:, -self.state_size:]

        state = Variable(torch.from_numpy(state.astype(int))).float().cuda()
        next_state = Variable(torch.from_numpy(
            next_state.astype(int))).float().cuda()

        q_eval = self.model(state)  # state
        q_next = self.target_model(next_state)  # next state
        # q_target = q_eval.cpu().detach().numpy()
        q_target = q_eval.clone()

        batch_index = np.arange(self.batch_size, dtype=np.int32)
        q_target[batch_index, action] = torch.from_numpy(reward).float().cuda()\
            + self.gamma * torch.max(q_next, axis=1)[0].float()

        loss = train(self.model,
                     state,
                     q_target,
                     self.learning_rate,
                     self.batch_size,
                     epochs=1,
                     verbose=0)
        self.lossHitory.append(loss)

    def save_model(self, fn):
        print("==> saving model")
        torch.save({"model_state_dict": self.model.state_dict()}, fn)
