# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:59:27 2022

@author: X2029440
"""

from enum import Enum
import pygame 


class Color(Enum) :

  WHITE = (255, 255, 255)  # r,g,b
  BLACK = (0, 0, 0)
  
  RED = (255, 0, 0)
  BLUE = (0, 0, 255)
  
  LIGHT_RED = (255, 114, 118)
  LIGHT_BLUE = (0, 191, 255)
  
  
  
  
#CLASS THAT DEFINES OUR PLAYERS (MOTO)
class Player : 
  
  #position : tuple (x,y) initial position of the moto 
  #direction : initial direction 
  
  def __init__(self, color_moto, color_trail, position, direction, max_size) : 
    
    self.color_moto = color_moto
    self.color_trail = color_trail 
    
    self.max_size = max_size #maximum length of a player and its trail 
    
    self.position = position
    self.direction = direction
    
    self.moto = position #positon of the moto 
    self.trail = [position] #position des of the moto + trail 
    
    
    
  def draw_player(self, display, block_size):
    
    #draw trail 
    for square in self.trail[:-1] : #draw each square of the trail
      rect = pygame.Rect(square[0] * block_size, square[1] * block_size,
                         block_size, block_size)
      pygame.draw.rect(display, self.color_trail, rect, block_size)
    
    #draw moto 
    moto_rect = pygame.Rect(self.moto[0] * block_size, self.moto[1] * block_size,
                       block_size, block_size)
    pygame.draw.rect(display, self.color_moto, moto_rect, block_size)
      
    
      
  #update trail + moto position 
  def update_position(self) : 
    
    if self.direction == 'UP' :
      self.trail.append((self.moto[0], self.moto[1]-1))
    elif self.direction == 'DOWN' :
      self.trail.append((self.moto[0], self.moto[1]+1))
    elif self.direction == 'RIGHT' :
      self.trail.append((self.moto[0]+1, self.moto[1]))
    elif self.direction == 'LEFT' :
      self.trail.append((self.moto[0]-1, self.moto[1])) #right direction
      
    self.moto = self.trail[-1][0], self.trail[-1][1]
    
    if len(self.trail) > self.max_size : self.trail.pop(0)
    
    
    
    
  # check if the moto collided with the trail of another player 
  def is_colliding_player_trail(self, player) : 
    if self.is_colliding_player_moto(player) : return False #moto collision takes over 
    if self.moto in player.trail[:-1] : return True 
    return False  
  
  
  #chck if both moto collided
  def is_colliding_player_moto(self, player) :
    #case where both moto have same position
    bool1 = self.moto == player.moto 
    
    #case where both moto went through eachother
    if len(self.trail) > 1 and len(player.trail) > 1 : 
      bool2 = self.moto in player.trail and player.moto in self.trail
    else : bool2 = False
    
    return bool1 or bool2 
  
  
  #check if player's moto collided with its own trail 
  def is_colliding_itself(self):
    if self.moto in self.trail[:-1] : return True
    return False 
  
  
  
  
  #check if player collided with surrounding walls 
  #map_size (size of the game's grid)
  def is_colliding_wall(self, map_size) : 
    
    return (self.moto[0] >= map_size or self.moto[1] >= map_size or \
           self.moto[0] < 0 or self.moto[1] < 0) 
  
  
  #check if player collided with the first n squares (the beginning) of the other player's trail
  #n : first n squares of the trail to consider 
  def is_colliding_beginning_player_trail(self, player, n) : 
    if self.is_colliding_player_moto(player) : return False #moto collision takes over
    if self.moto in player.trail[-n:-1] : return True
    return False  
           
  
  
  
  #key events 
  #use_arrow_keys : wether to use arrow keys or (q,z,d,s) keys
  def update_direction(self, use_arrow_keys) : 
    
    
    values = [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT] if use_arrow_keys else \
           [pygame.K_s, pygame.K_z, pygame.K_q, pygame.K_d]
           
    keys = pygame.key.get_pressed()
    
    #in the beginning, cannot go into the wall directly
    can_go_left = True if use_arrow_keys else self.direction != None
    can_go_right = True if not use_arrow_keys else self.direction != None

    if keys[values[0]] and self.direction != 'UP': self.direction = 'DOWN'
    elif keys[values[1]] and self.direction != 'DOWN': self.direction = 'UP'
    elif keys[values[2]] and self.direction != 'RIGHT' and can_go_left : self.direction = 'LEFT'
    elif keys[values[3]] and self.direction != 'LEFT' and can_go_right : self.direction = 'RIGHT'
    
    
    
    
      
    
    
    
  
  
  
  
  