# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 13:29:27 2022

@author: X2029440
"""

from player import Color 
from player import Player 
import pygame 
import sys 
from agent import Agent 
import datetime 
from point import Point
import random 
import time 
import numpy as np 
import itertools 



#CLASS THAT DEFINES OUR TRON GAME WITH AIs

'''
simplified version of trongameai
 
Here we give the reward at the end of the game, we consider that the reward of each action of the
game has a unique value that we only know once the game is finished

Thus, we do not train after each ation but at the end of each game 
'''
class TronGameAI : 
  
  # REWARDS = [-10,-10,-10,-10,10,10,10,0] #values of the rewards, check comment underneath 

  def __init__(self, window_size, map_size, draw_grid, max_size) : #fps : speed of the game, map_size : size of the grid
    
    self.nb_games = 0  #nb of games 
    self.slow_down = False #slow down learning process to better see 
    
    self.window_size = window_size 
    self.map_size = map_size 
    self.block_size = self.window_size // self.map_size
    
    self.draw_grid = draw_grid
    self.max_size = max_size
    
    self.display = pygame.display.set_mode((self.window_size, self.window_size), 0, 32)
    pygame.init()
    pygame.display.set_caption('TRON AI')
    
    self.blue_player_score = 0 
    self.red_player_score = 0 

    blue_player_pos = (0, self.map_size // 2)
    red_player_pos = (self.map_size - 1, self.map_size // 2)
    
    blue_player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, 
                               blue_player_pos, 'RIGHT', self.max_size) #no direction in the beginning  
    red_player = Player(Color.RED.value, Color.LIGHT_RED.value, 
                              red_player_pos, 'LEFT', self.max_size) #no direction in the beginning 
    
    self.blue_agent = Agent(blue_player) #blue ai associated with player blue 
    self.red_agent = Agent(red_player) #red ai associatde with player red 
    
    self.walls = [(x,-1) for x in range(self.map_size)] + \
                 [(x,self.map_size) for x in range(self.map_size)] + \
                 [(-1,y) for y in range(self.map_size)] + \
                 [(self.map_size,y) for y in range(self.map_size)] #coord of the walls squares 
    
    self.map = [(x,y) for x,y in itertools.product(range(self.map_size),range(self.map_size))]
    
    
  #draw map
  def draw_map(self):
    self.display.fill(Color.BLACK.value)
    for x in range(0, self.window_size, self.block_size):
      for y in range(0, self.window_size, self.block_size):
        rect = pygame.Rect(x, y, self.block_size, self.block_size)
        
        if self.draw_grid : 
          pygame.draw.rect(self.display, Color.WHITE.value, rect, 1)
          
          
  def draw_scores(self) : 
    
    pygame.font.init() 
    my_font = pygame.font.SysFont('Calibri', 20, bold=True)
    
    score_blue = my_font.render('SCORE : ' + str(self.blue_player_score), False, Color.LIGHT_BLUE.value)
    score_red = my_font.render('SCORE : ' + str(self.red_player_score), False, Color.LIGHT_RED.value)
    
    self.display.blit(score_blue, (0,0))
    self.display.blit(score_red, (self.window_size - score_red.get_width(), 0))
      
        
  
  def update_players(self) : 

    #update positions of players 
    self.blue_agent.player.update_position()
    self.red_agent.player.update_position()
    
    #redraw them 
    self.blue_agent.player.draw_player(self.display, self.block_size)
    self.red_agent.player.draw_player(self.display, self.block_size)
    
    

  #returns tuple (collision:bool, reward)
  def get_reward(self, agent1, agent2) :
    reward, reward_neg, reward_pos = 0,0,0
    collisions = [agent1.player.is_colliding_itself(), 
                  agent1.player.is_colliding_player_trail(agent2.player),
                  agent1.player.is_colliding_player_moto(agent2.player), 
                  agent1.player.is_colliding_wall(self.map_size)] 
    if collisions[0] : reward_neg = -25 #collision with itself 
    elif collisions[1] : reward_neg = -20 #collision with other player's trail 
    elif collisions[2] : reward_neg = -5 #collision with other player's moto 
    elif collisions[3] : reward_neg = -15 #collision with wall
    
    #if the other player hit the beginning of the trail (meaning player1 blocked him and made player2 die)
    if agent2.player.is_colliding_beginning_player_trail(agent1.player, self.map_size // 4) : 
      reward_pos += 25
    elif agent2.player.is_colliding_player_trail(agent1.player) : 
      reward_pos += 10
    elif agent2.player.is_colliding_itself() : 
      reward_pos += 5
    elif agent2.player.is_colliding_wall(self.map_size) : 
      reward_pos += 5
      
    reward = reward_neg + reward_pos
     
    collision = any(collisions)
    
    return collision, reward
    
  
  def check_collisions(self) :
    
    game_over = False 

    #check for blue player collision
    blue_collision, blue_reward = self.get_reward(self.blue_agent, self.red_agent)
    red_collision, red_reward = self.get_reward(self.red_agent, self.blue_agent)

    if blue_collision and red_collision : 
      print('NO ONE WINS') ; self.reset_game() #both died at the same time
      game_over = True 
    elif blue_collision: 
      print('RED WINS') ; self.reset_game() ; self.red_player_score += 1 #blue died + update score 
      game_over = True 
    elif red_collision: 
      print('BLUE WINS') ; self.reset_game() ; self.blue_player_score += 1 #red died + update score 
      game_over = True
    return game_over, blue_reward, red_reward
     
     
     
     
   #update game every 1/fps sec
  def update_game(self) : 
     
     self.draw_map() #redraw game map 
     self.draw_scores() #display both players' scores
     
     self.update_players() #update players positions + redraw them 
     game_over, blue_reward, red_reward = self.check_collisions()
     
     return game_over, blue_reward, red_reward
    

    
  def reset_game(self) : 
    
    self.draw_map()
    
    blue_player_pos = (0, self.map_size // 2)
    red_player_pos = (self.map_size - 1, self.map_size // 2)
    
    self.blue_agent.player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, 
                               blue_player_pos, 'RIGHT', self.max_size) #random direction in the beginning  
    self.red_agent.player = Player(Color.RED.value, Color.LIGHT_RED.value, 
                              red_player_pos, 'LEFT', self.max_size) #random direction in the beginning 

  
  
  
  def get_mouse_wheel_events(self) : 
    for event in pygame.event.get():
      if event.type == pygame.MOUSEWHEEL:
        if event.y == 1 : self.slow_down = False 
        if event.y == -1 : self.slow_down = True
    if self.slow_down : 
      time.sleep(0.2)
      
      
  #to close window  
  def get_close_window_event(self) : 
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
        pygame.quit()
        sys.exit()
        

  #train the agent on a game 
  def train_agents(self) :
    
    try : 
    
      first_loop = True 
      
      blue_last_game = [] #tuples (state, reward, next_state, action ...) of each game (to train our qnetwork)
      red_last_game = [] #tuples (state, reward, next_state, action ...) of each game (to train our qnetwork)
  
      #training 
      while True :
        
        if first_loop : self.update_game() ; first_loop = False  
        
        seconds = int(pygame.time.get_ticks()/1000)
        print("AIs have been training for:", datetime.timedelta(seconds=seconds))
        print("AIs have played", self.nb_games,'games')
        
        #get states 
        blue_current_state = self.blue_agent.get_game_state(self, self.red_agent.player)
        red_current_state = self.red_agent.get_game_state(self, self.blue_agent.player)
  
        #get actions 
        blue_action = self.blue_agent.get_action(blue_current_state, self.nb_games)
        red_action = self.red_agent.get_action(red_current_state, self.nb_games)
        
        #perform actions (update directions)
        self.blue_agent.update_direction(np.argmax(blue_action))
        self.red_agent.update_direction(np.argmax(red_action))
        
        #update players and ui 
        game_over, blue_reward, red_reward = self.update_game()
        pygame.display.update() #update ui 
  
        #get next state 
        blue_next_state = self.blue_agent.get_game_state(self, self.red_agent.player)  
        red_next_state = self.red_agent.get_game_state(self, self.blue_agent.player)
  
        #remember (for normal training once the game is done)
        blue_last_game.append((blue_current_state, blue_action, blue_reward, blue_next_state, game_over))
        red_last_game.append((red_current_state, red_action, red_reward, red_next_state, game_over))
  
        #remember (for experience replay, train_batch())
        self.blue_agent.remember(blue_current_state, blue_action, blue_reward, blue_next_state, game_over) #remember tuple to retrain whole qnetwork later 
        self.red_agent.remember(red_current_state, red_action, red_reward, red_next_state, game_over) #remember tuple to retrain whole qnetwork later
        
        
        #At the end of each game we finally know the value of the blue rewards and red rewards (-1,0,1)
        #we can now train the agents on the data 
        #here it's a specific type of q learning where we don't train after each action but rather at the end of each game 
        #that's because our rewards are based on the final outcome of the game and not the outcome of each action
        if game_over : 
          
          print(blue_reward, red_reward)
          
          self.nb_games += 1 
          
          #unzip 
          blue_states, blue_actions, blue_rewards, blue_next_states, game_overs = zip(*blue_last_game)
          red_states, red_actions, red_rewards, red_next_states, game_overs = zip(*red_last_game)
          
          #we empty both lists
          blue_last_game = [] 
          red_last_game = []
          
          #set reward values now that we know the outcome
          blue_rewards = (blue_reward,) * len(blue_rewards) #(-1,-1,-1, ...) ou (0,0,0, ...) ou (1,1,1, ...)
          red_rewards = (red_reward,) * len(red_rewards) #(-1,-1,-1, ...) ou (0,0,0, ...) ou (1,1,1, ...)
          
          #normal train after each game 
          self.blue_agent.qtrainer.train(blue_states, blue_actions, blue_rewards, blue_next_states, game_overs)
          self.red_agent.qtrainer.train(red_states, red_actions, red_rewards, red_next_states, game_overs)
          
          #experience replay 
          # self.blue_agent.train_batch() 
          # self.red_agent.train_batch()
          
        self.get_mouse_wheel_events() #to speed or slow the learning process 
        self.get_close_window_event() #to close window 
        
    finally : #save best AI's qnetwork 
    
      if self.blue_player_score >= self.red_player_score : self.blue_agent.save_model('model_' + str(self.map_size) + '.pth')
      else : self.red_agent.save_model('model_' + str(self.map_size) + '.pth')
      
      
  #make already trained agents play against eachother
  def play_from_trained_agents(self) : 
    
    self.blue_agent.set_model(TronGameAI.BLUE_MODEL_PATH)
    self.red_agent.set_model(TronGameAI.RED_MODEL_PATH)
    
    first_loop = True 

    #training 
    while True :
      
      if first_loop : self.update_game() ; first_loop = False  

      #get states 
      blue_current_state = self.blue_agent.get_game_state(self, self.red_agent.player)
      red_current_state = self.red_agent.get_game_state(self, self.blue_agent.player)

      #get actions 
      blue_action = self.blue_agent.get_action(blue_current_state, self.nb_games)
      red_action = self.red_agent.get_action(red_current_state, self.nb_games)
      
      #perform actions (update directions)
      self.blue_agent.update_direction(np.argmax(blue_action))
      self.red_agent.update_direction(np.argmax(red_action))
      
      #update players
      game_over, blue_reward, red_reward = self.update_game()
      pygame.display.update() #update ui 
      
      time.sleep(0.2)
      
      

      
if __name__ == "__main__":
  
  window_size = 700
  map_size = 30
  draw_grid = False #whether or notc to draw grid with white lines 
  max_size = np.inf
  
  game = TronGameAI(window_size, map_size, draw_grid, max_size)
  game.train_agents() #train agents
  # game.play_from_trained_agents() #make already trained agents play
        
        
        
        
        
        
        
        
        
        
        
        
    