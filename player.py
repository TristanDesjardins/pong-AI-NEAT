# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:16:06 2022

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
  
  GREEN = (41, 163, 41)
  DARK_GREEN = (0,110,0)
  YELLOW = (255, 204, 0)
  
  
#class to define the paddle 
class Player : 
  
  
  def __init__(self, x = 0, y = 190, length=120, width=10) : 
    
  
    #coords of the top left corner of the paddle
    self.x = x 
    self.y = y
    
    self.y_vel = 1.5

    #size of the paddle 
    self.length = length
    self.width = width
    
    self.paddle = pygame.Rect(self.x, self.y, self.width, self.length) 
    
    self.score = 0 
    
    self.nb_wins = 0 #useful for neat's fitness (our fitness is the number of wins)
    
    
    
  def draw_paddle(self, display) : 
    
    self.paddle.topleft = self.x, self.y
    pygame.draw.rect(display, Color.BLACK.value, self.paddle, 5, 10)
    
  
  #up and down arrow keys for player 1
  #z and s keys for player 2 
  def move(self, use_arrow_keys, dt = 10) : 
    
    values = [pygame.K_DOWN, pygame.K_UP] if use_arrow_keys else \
             [pygame.K_s, pygame.K_z]
           
    keys = pygame.key.get_pressed()
    
    if keys[values[0]] and self.y < 500 - self.length : self.y += self.y_vel*dt #move down 
    elif keys[values[1]] and self.y > 0 : self.y -= self.y_vel*dt #move up 
    
    
    
  #move but without key events
  #function for the neat module (using output of our neural net)
  #output of neural net : [x,y,z] = [move_left, stand_still, move_right]
  #action : vector of size 3 -> np.argmax(output_nn) = 0,1 or 2
  #left player : whether player is on the left or not 
  def move_neat(self, action, left_player, dt=10) : 
    if action == 0 :
      if left_player and self.y < 500 - self.length: self.y += self.y_vel*dt
      elif not left_player and self.y > 0: self.y -= self.y_vel*dt  
    if action == 2 : 
      if left_player and self.y > 0 : self.y -= self.y_vel*dt
      elif not left_player and self.y < 500 - self.length: self.y += self.y_vel*dt

    
    
    
  #get game state of our player (input of our neural network for neat)
  #vector of size 3 : 
  # - dx (player, ball)
  # - dy (player, ball)
  # - theta (direction of the ball relative to the paddle)

  #left_plater : boolean indicating if we're calculating the game state of the left player 
  #(because we obiously take into account the symmetry)
  def get_game_state(self, ball, left_player) : 
    
    x_paddle, y_paddle = self.paddle.center #paddle's center coords
    
    #dx
    if left_player : dx = ball.x - x_paddle
    else : dx = x_paddle - ball.x
    
    #dy 
    if left_player : dy = ball.y - y_paddle
    else : dy = y_paddle - ball.y
    
    #theta 
    if left_player : theta = (ball.direction - 90)%360
    else : theta = (ball.direction + 90)%360 
    
    game_state = [dx, dy, theta]
    return game_state
    
    
    
    
  
  
  
  
  
  