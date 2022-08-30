# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 21:21:17 2022

@author: X2029440
"""

from player import Color 
from player import Player 
import pygame 
import sys 
import numpy as np
from agent import Agent
import random
import itertools  


#LEFT PLAYER (BLUE) MUST USE Q,Z,D,S TO MOVE 
# PLAYER (RED) MUST USE ARROW KEYS TO MOVE 

#CLASS THAT DEFINES OUR TRON GAME 
class TronGame : 
  

  '''
  fps : speed of the game (nb of frames per sec)
  map_size : number of squares horizontally (or vertically) of our map 
  solo_mode : if True, you (RED) play against AI (BLUE), else multiplayer
  '''
  def __init__(self, window_size, map_size, fps, draw_grid, max_size, solo_mode = False) : 
    
    self.window_size = window_size 
    self.map_size = map_size 
    self.block_size = self.window_size // self.map_size
    self.fps = fps 

    self.solo_mode = solo_mode
    
    self.draw_grid = draw_grid
    self.max_size = max_size
    
    self.display = pygame.display.set_mode((self.window_size, self.window_size), 0, 32)
    pygame.init()
    pygame.display.set_caption('TRON')
    
    self.blue_player_score = 0 
    self.red_player_score = 0 

    blue_player_pos = (0, self.map_size // 2)
    red_player_pos = (self.map_size - 1, self.map_size // 2)
    
    if not self.solo_mode : 
      self.blue_player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, blue_player_pos, None, self.max_size) #no direction in the beginning, static 
    else : 
      self.blue_player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, blue_player_pos, 'RIGHT', self.max_size) #no direction in the beginning, static 
      self.blue_agent = Agent(self.blue_player) #create our AI  
      self.blue_agent.set_model('model_' + str(self.map_size) + '.pth')
  
    self.red_player = Player(Color.RED.value, Color.LIGHT_RED.value, red_player_pos, None, self.max_size) #no direction in the beginning, static 
      
      
    self.walls = [(x,-1) for x in range(self.map_size)] + \
                 [(x,self.map_size) for x in range(self.map_size)] + \
                 [(-1,y) for y in range(self.map_size)] + \
                 [(self.map_size,y) for y in range(self.map_size)] #coord of the walls squares 
                 
    #coord of map (points inside walls )           
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
    self.blue_player.update_position()
    self.red_player.update_position()
    
    #redraw them 
    self.blue_player.draw_player(self.display, self.block_size)
    self.red_player.draw_player(self.display, self.block_size)
    
    
    
  def check_collisions(self) : 

    #check for blue player collision
    blue_collision = any([self.blue_player.is_colliding_itself(), 
                          self.blue_player.is_colliding_player_trail(self.red_player),
                          self.blue_player.is_colliding_player_moto(self.red_player), 
                          self.blue_player.is_colliding_wall(self.map_size)]) 
    
    #check for red player collision 
    red_collision = any([self.red_player.is_colliding_itself(), 
                         self.red_player.is_colliding_player_trail(self.blue_player),
                         self.red_player.is_colliding_player_moto(self.blue_player), 
                         self.red_player.is_colliding_wall(self.map_size)]) 
    
    if blue_collision and red_collision : print('NO ONE WINS') ; self.reset_game() #both died at the same time
    elif blue_collision: print('RED WINS') ; self.reset_game() ; self.red_player_score += 1 #blue died + update score 
    elif red_collision: print('BLUE WINS') ; self.reset_game() ; self.blue_player_score += 1 #red died + update score 
    
    
  #update game every 1/fps sec
  def update_game(self) : 
    
    self.draw_map() #redraw game map 
    self.draw_scores() #display both players' scores
    
    self.update_players() #update players positions + redraw them 
    self.check_collisions()
    
    
  
    
  def reset_game(self) : 
    
    self.draw_map()
    
    blue_player_pos = (0, self.map_size // 2)
    red_player_pos = (self.map_size - 1, self.map_size // 2)
    
    if not solo_mode : 
      self.blue_player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, blue_player_pos, None, self.max_size) #no direction in the beginning, static 
    else: 
      self.blue_player = Player(Color.BLUE.value, Color.LIGHT_BLUE.value, 
                                      blue_player_pos, 'RIGHT', self.max_size) #random direction in the beginning
      self.blue_agent.player = self.blue_player
      
    self.red_player = Player(Color.RED.value, Color.LIGHT_RED.value, red_player_pos, None, self.max_size) #no direction in the beginning, static 


  #game loop 
  def run_game(self):

    next_render_time = 0  #in seconds
    while True : #game loop 
    
      

      current_time = pygame.time.get_ticks()/1000 #in seconds
      

      #if not solo_mode : listen to key events 
      if not self.solo_mode : self.blue_player.update_direction(False) #q,z,d,s
      
        
      #key events 
      self.red_player.update_direction(True) #arrow keys


      #timer to update ui 
      if  current_time >= next_render_time :  #update game only every 'FPS' seconds
        
        if self.solo_mode : #AI mode
          game_state = self.blue_agent.get_game_state(self, self.red_player) #get game state
          action = self.blue_agent.get_action(game_state, 0, explore=False)  #get  action from game state
          self.blue_agent.update_direction(np.argmax(action)) #perform action
          print(self.blue_agent.player.direction)
      
        self.update_game()    
        pygame.display.update()
        next_render_time = current_time + 1 / self.fps
        
      #quit window
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
          
        
          
if __name__ == "__main__":
  
  window_size = 700
  map_size = 30
  fps = 12
  draw_grid = False #whether or notc to draw grid with white lines 
  max_size = np.inf
  solo_mode = True
  
  
  game = TronGame(window_size, map_size, fps, draw_grid, max_size, solo_mode)
  game.run_game()
  
        
        
        
        
        
        
        
        
        
        
        
        
    