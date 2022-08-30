# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 23:31:38 2022

@author: X2029440
"""


import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


#CLASS TO DEFINE OUR QMODEL

#input size = game state size (20)
#output size = 3 (turn left, stay, turn right) = (Q_value_action1, Q_value_action2, Q_value_action3)
class QNet(nn.Module):
    def __init__(self, input_size=141, output_size=3):
        super().__init__()
        self.linear1 = nn.Linear(input_size, 64)
        self.linear2 = nn.Linear(64, 32)
        self.linear3 = nn.Linear(32, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x
  



#CLASS THAT DEFINES HOW TO TRAIN OUR QMODEL
class QTrainer:
  
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        
        self.memory_loss = [] #remember loss to be able to plot it real-time 

    def train(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        
        loss = self.criterion(target, pred)
        self.memory_loss.append(loss.item())
        
        loss.backward()

        self.optimizer.step()