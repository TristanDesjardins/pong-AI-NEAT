# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 00:21:39 2022

@author: X2029440
"""

import torch 
import numpy as np 
import random 
from qnetwork import QNet, QTrainer
from collections import deque
from point import Point
import torch
import itertools

#class that defines an AI player
class Agent : 
  
  BATCH_SIZE = 100_000
  MAX_MEMOMERY = 200
  DIRECTIONS = ['UP', 'LEFT', 'DOWN', 'RIGHT'] #clockwise
  
  
  def __init__(self, player) : 
    
    self.player = player 
    self.qnetwork = QNet(input_size=141, output_size=3) #notre q model 
    self.qtrainer = QTrainer(self.qnetwork, 1e-3, 0.9) #model, lr, gamma
    self.epsilon = 0 #tradeoff between exploration / exploitation 
    self.memory = deque(maxlen=Agent.MAX_MEMOMERY)
    
  
  
  #change moto direction based on the action output buy our qnetwork 
  def update_direction(self, action) : #action : 0, 1 ou 2  
    if action == 0 : 
      index = Agent.DIRECTIONS.index(self.player.direction)
      self.player.direction = Agent.DIRECTIONS[(index + 1)%4]
    elif action == 1 : return #on ne fait rien 
    elif action == 2 : 
      index = Agent.DIRECTIONS.index(self.player.direction)
      self.player.direction = Agent.DIRECTIONS[(index - 1)%4]
      
      
  #what is the action to take given a specific game_state for a game ? 
  #explore : whether or not to explore in the beginning (we may not want that if we use a loaded qnetwork for instance)
  #returns : action, vector of size 3 : ['left', 'straight','right'], ex : [1,0,0] means turning to your left 
  def get_action(self, game_state, nb_games, explore = True) : 
    # random moves: tradeoff exploration / exploitation
    # self.epsilon = 80 - nb_games if explore else 0 
    # action = [0,0,0]

    # if random.randint(0, 200) < self.epsilon and explore: #exploration (mouvement aléatoire)
    #   move = random.randint(0, 2)
    #   action[move] = 1
    
    
    action = [0,0,0]
    
    start_epsilon = 0.5 #(start proba of random)
    end_epsilon = 1 / 10 #(end proba of random)
    nb_games_end_epsilon = 1000 #nb of games to reach end epsilon 
    if nb_games > nb_games_end_epsilon : nb_games = nb_games_end_epsilon
    epsilon = start_epsilon - nb_games * (start_epsilon - end_epsilon) / nb_games_end_epsilon
    if random.uniform(0,1) < epsilon and explore: #exploration (mouvement aléatoire)
      print('exploration')
      move = random.randint(0, 2)
      action[move] = 1
    

    else: #exploitation (we use the qnetwork model) 
      game_state_tensor = torch.tensor(game_state, dtype=torch.float)
      prediction = self.qnetwork(game_state_tensor)
      move = torch.argmax(prediction).item()
      action[move] = 1
    
    return action
    

      
  '''
  vecteur de taille 4
  [N, E, S, O]
  ex : [1,0,0,1] il y a un bout de son propre trail (carré) au nord et et à l'ouest de la moto (nord par rapport à lui)
  '''
  def get_own_trail_state(self) : 
    own_trail_state = [0 for k in range(4)]
    for square in self.player.trail[:-3] : 
      points = Point.get_relative_position_and_is_touching(self.player.moto, square, self.player.direction)
      own_trail_state = [x + y for x, y in zip(own_trail_state, points)]
    return own_trail_state
  
  
    
  '''
  idem get_own_trail_state() for with the trail of the other player 
  '''
  def get_other_trail_state(self, player) : 
    other_trail_state = [0 for k in range(4)]
    for square in player.trail[:-3] : 
      points = Point.get_relative_position_and_is_touching(self.player.moto, square, self.player.direction)
      other_trail_state = [x + y for x, y in zip(other_trail_state, points)]
    return other_trail_state
  
  
  
  '''
  to replace get_own_trail_state, get_other_trail_state and get wall state 
  on trace un carré de rayon 'size' autour de notre moto et on met des 1 si obstacles et 0 sinon
  /!\ prend bien en compte la direction du player
  renvoie un vecteur de taille (size*2+1)^2 
  '''
  def get_trail_and_wall_state(self,game, player, size=5) : 
    
    x,y = self.player.moto
    
    #coords of our square
    coords_square = [(x-size+i, y-size+j) for (i,j) in 
                     list(itertools.product(range(size*2+1),range(size*2+1)))]
    
    #let's put 1 if there is an obstacle, 0 otherwise 
    def convert(coord) : 
      if coord in self.player.trail or coord in player.trail or coord not in game.map : 
        return 1
      return 0 
    
    obstacles = [convert(coord) for coord in coords_square]
    
    #get coords relative to direction 
    if self.player.direction == 'RIGHT' : 
      coords_square = [Point.rotate_clockwise_n(coord[0], coord[1], (x,y), 3) for coord in coords_square]
    elif self.player.direction == 'DOWN' : 
      coords_square = [Point.rotate_clockwise_n(coord[0], coord[1], (x,y), 2) for coord in coords_square]
    elif self.player.direction == 'LEFT' :
      coords_square = [Point.rotate_clockwise_n(coord[0], coord[1], (x,y), 1) for coord in coords_square]
      
    #sort obstacles by sorting coords
    sorted_obstacles = [obstacle for _, obstacle in 
                        sorted(zip(coords_square, obstacles), key=lambda k: (k[0], k[1]))]
    
    return sorted_obstacles #trail and wall state
   

  

  '''
  [N, NE, E, SE, S, SO, O, NO]
  vector of size 8 : ex : [0,1,0,0,0,0,0,0] the moto of the other is NE (relative to the direction)
  '''
  def get_moto_state(self, player) : 
    return Point.get_relative_position_with_direction(self.player.moto, player.moto, self.player.direction)



  '''
  idem trail_state mais pour les murs
  '''
  def get_wall_state(self,game) : 
    wall_state = [0 for k in range(4)]
    for square in game.walls : 
      points = Point.get_relative_position_and_is_touching(self.player.moto, square, self.player.direction)
      wall_state = [x + y for x, y in zip(wall_state, points)]  
    return wall_state
  
  
  '''
  Concatenation of all types of states
  game_state : vector of size 20 (or 57)
  '''
  def get_game_state(self,game,player) : 
    
    moto_state = self.get_moto_state(player) #size 8
    
    own_trail_state = self.get_own_trail_state() #size 4
    other_trail_state = self.get_other_trail_state(player) #size 4 
    wall_state = self.get_wall_state(game) #size 4
    trail_and_wall_state = self.get_trail_and_wall_state(game, player) #size 49
    game_state = moto_state + own_trail_state + other_trail_state + wall_state + trail_and_wall_state

    return game_state #vector of size 20   
  
  
  #remember previous tuples to retrain whole network with them every time the game is over 
  def remember(self, current_state, action, reward, next_state, game_over):
    self.memory.append((current_state, action, reward, next_state, game_over)) # popleft if MAX_MEMORY is reached
    

  #after each gameover, train network on a whole batch 
  def train_batch(self) : 
    
      if len(self.memory) > Agent.BATCH_SIZE: batch = random.sample(self.memory, Agent.BATCH_SIZE) # list of tuples
      else: batch = self.memory
      
      states, actions, rewards, next_states, game_overs = zip(*batch)
      self.qtrainer.train(states, actions, rewards, next_states, game_overs)

      
  #save our qnetwork 
  def save_model(self, model_path) : 
    torch.save(self.qnetwork.state_dict(), model_path)
    print('model saved')
    
  #load and set model of our agent (from an existing trained model for instance)
  def set_model(self,model_path) : 
    self.qnetwork = QNet(input_size=141, output_size=3) 
    self.qnetwork.load_state_dict(torch.load(model_path))
    self.qtrainer = QTrainer(self.qnetwork, 1e-3, 0.9) #model, lr, gamma
      

