# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:14:35 2022

@author: X2029440
"""


import pygame 
import sys 
import pickle 
import numpy as np 
import time 
from player import Color, Player 
from ball import Ball 


#main class
class Pong :

  

  def __init__(self, window_width, window_height, mode, fps) : 
    
    self.window_width, self.window_height = window_width, window_height
    self.fps = fps #frame per sec (game speed)
    
    self.player1 = Player(x=785) #right player 
    self.player2 = Player(x=5) #left player 
    
    self.ball = Ball(400, 250)
    self.slow_down = True #to speed or slow down the process when AIs are playing together (using mousewheel)
    
    self.mode = mode 
    self.model = None #in case mode = 'ai' or mode = 'solo' in run_game(), then this is the model of our AI 
    
    #those two variables are useful to avoid many collisions in a row 
    self.nb_loops = 0 #number of loops 
    self.last_collision = 0 #nb loops when last collision 
    
    self.game_started = False 
    
    self.display = pygame.display.set_mode((self.window_width, self.window_height), 0, 32)
    pygame.init()
    pygame.display.set_caption('PONG')
    
    
    
    
  def draw_map(self) : 
    
    self.display.fill(Color.WHITE.value)
    pygame.draw.line(self.display, Color.BLACK.value, (400,0), (400,500), 5)
    pygame.draw.circle(self.display, Color.BLACK.value, (400,250), 100, 5)
    
    
  def draw_scores(self) : 
    
    pygame.font.init() 
    my_font = pygame.font.SysFont('Calibri', 100, bold=True)
    
    score1 = my_font.render(str(self.player1.score), False, Color.BLACK.value) #right player score
    score2 = my_font.render(str(self.player2.score), False, Color.BLACK.value) #left player score
    
    self.display.blit(score1, (450,0))
    self.display.blit(score2, (350 - score2.get_width(), 0))
    
    
    
  #draw game state (not mandatory)
  #in case we want to check live game states values of both paddles
  def draw_states(self) : 
    
    pygame.font.init() 
    my_font = pygame.font.SysFont('Calibri', 30, bold=True)
    
    game_state1 = self.player1.get_game_state(self.ball, False)
    game_state2 = self.player2.get_game_state(self.ball, True)
    
    #rounding for better lisibility 
    game_state1 = [round(x) for x in game_state1]
    game_state2 = [round(x) for x in game_state2]
    
    state1 = my_font.render(str(game_state1), False, Color.RED.value)
    state2 = my_font.render(str(game_state2), False, Color.RED.value)
    
    self.display.blit(state1, (440,450)) #right player
    self.display.blit(state2, (200,450)) #left player
    
    
  
  def reset(self) : 
    
    if self.mode != 'ai' : self.game_started = False 
    self.player1.y = 190
    self.player2.y = 190
    
    self.ball = Ball(400, 250)
    
    

  #update game variables and ui at each frame 
  #mode = 'solo', 'multi' ou 'ai'
  # - multi : play against your friend (no AI)
  # - solo : play against AI (you on the right, ai is on the left)
  # - ai : watch AI play against itself 
  def update(self) : 
    
    #draw
    self.draw_map()
    self.draw_scores()
    
    self.ball.draw_ball(self.display)
    self.draw_states()
  
    self.player1.draw_paddle(self.display)
    self.player2.draw_paddle(self.display)
    
    if self.game_started : 
      #move
      self.ball.move()
      
      if self.mode == 'multi' : self.player1.move(True); self.player2.move(False)
      
      elif self.mode == 'solo' : 
        
        self.player1.move(True)
        
        output = self.model.activate(self.player2.get_game_state(self.ball, True))
        action = np.argmax(output) 
        self.player2.move_neat(action, True, dt=10)
        
      elif self.mode == 'ai' : 
        
        output1 = self.model.activate(self.player1.get_game_state(self.ball, False))
        output2 = self.model.activate(self.player2.get_game_state(self.ball, True))
        
        action1 = np.argmax(output1) 
        action2 = np.argmax(output2)
        
        self.player1.move_neat(action1, False, dt=10)
        self.player2.move_neat(action2, True, dt=10)
      
      #collisions (player, ball), (ball, up and down borders), (ball, left and right borders
      #collision with up and down borders
      if self.nb_loops - self.last_collision > 2 : 
        if self.ball.collision_up_down_borders():
          self.last_collision = self.nb_loops
          print('collision ball - borders')
          
        #if collision with paddle
        if self.ball.collision_paddle(self.player1) or self.ball.collision_paddle(self.player2) : 
          self.last_collision = self.nb_loops
          print('collision ball - player')
          
        #if collision with lateral borders, reset the game 
        if self.ball.collision_left_right_borders() : 
          self.last_collision = self.nb_loops
          if self.ball.x > 400 : self.player2.score += 1 
          else : self.player1.score += 1 
          self.reset()
    
    
    pygame.display.update()
    
    

  #to run the game 
  #mode = 'solo', 'multi' ou 'ai'
  # - multi : play against your friend (no AI)
  # - solo : play against AI (you on the right, ai is on the left)
  # - ai : watch AI play against itself 
  def run_game(self, model_path = 'best_model.pkl'):
    
    if self.mode == 'solo' or self.mode == 'ai' : #load model 
      with open(model_path, 'rb') as f:
        self.model = pickle.load(f)
        
    if self.mode == 'ai' : self.game_started = True 

    next_update = 0  #time of next update 
    dt_updates = 1/self.fps if self.mode != 'ai' else 1/np.inf #time btw two updates

    while True : #game loop 

      current_time = pygame.time.get_ticks()/1000 #in seconds 
      
      #update ui 
      if  current_time >= next_update :  #update game only every 'FPS' seconds
        next_update = current_time + dt_updates

        self.nb_loops += 1 
        
        self.update()
      
      
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN : 
          self.game_started = True
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if event.type == pygame.MOUSEWHEEL:
          if event.y == 1 : self.slow_down = False 
          if event.y == -1 : self.slow_down = True
          
      if self.slow_down : 
        time.sleep(1/self.fps)
          
          

          
if __name__ == "__main__":
  
  window_width = 800
  window_height = 500
    
  modes = ['multi', 'solo', 'ai']
  fps = 100
  
  game = Pong(window_width, window_height, modes[2], fps)
  game.run_game()
  
  
  
