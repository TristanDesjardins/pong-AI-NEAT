# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:52:46 2022

@author: X2029440
"""

import pygame 
from player import Color
import random 
import numpy as np 
import math 

class Ball : 
  
  
 def __init__(self, x = 0, y = 0, radius=15) : 
   
 
   #coords of the center of the ball
   self.x = x 
   self.y = y
   
   self.x_vel = 0
   self.y_vel = 0 
 
   #radius of the ball 
   self.radius = radius
   
   
   #initial direction of the ball
   #angle in degrees (clockwise direction, 0 is horizontal)
   self.direction = random.uniform(*random.choice([[-40,40],[140,220]]))%360
   
   
 def draw_ball(self, display) : 
   
   pygame.draw.circle(display, Color.BLACK.value, (self.x, self.y), self.radius, 5)
   pygame.draw.circle(display, Color.YELLOW.value, (self.x, self.y), self.radius-5)
   
 
 #up and down arrow keys for player 1
 #z and s keys for player 2 
 def move(self, dt = 15) : 
   
   self.x_vel = np.cos(math.radians(self.direction%360))
   self.y_vel = np.sin(math.radians(self.direction%360))
   
   self.x += self.x_vel * dt
   self.y += self.y_vel * dt 
 

 #check for collision with up and down borders of the screen (+ update ball's direction)
 #update direction accordingly
 def collision_up_down_borders(self) : 
   if self.y - self.radius < 0 or self.y + self.radius > 500 : 
     self.update_direction(True) 
     return True 
   return False 
   
 
 #check for collision with left or right borders (then one of the player loses)
 def collision_left_right_borders(self) : 
   if self.x < 0 or self.x > 800 :
     self.update_direction(False) #in case we want to make the ball bounce instead of resetting the game
     return True 
   return False 
   
 
 #update the direction symetrically on collision with up and down border
 #horizontal : boolean, sense of the symmetry 
 def update_direction(self, horizontal) : 
   if horizontal :
     self.direction = (360 - self.direction)%360
   else : 
     self.direction = (180 - self.direction)%360
     
     
 #collision with paddle's player 
 #update direction aswell (with some randomness)
 def collision_paddle(self, player) : 
   ball_rect = pygame.Rect(self.x-self.radius, self.y-self.radius, 
                          self.radius*2, self.radius*2) #we approximate ball with a rectangle
   if ball_rect.colliderect(player.paddle) : #collision between both rectangles (ball and paddle)
     if (self.direction > 270 and self.direction <= 360) \
     or (self.direction >= 0 and self.direction < 90) : #update direction with some randomness
       self.direction = random.uniform(135,225)%360
     else : 
       self.direction = random.uniform(-45,45)%360
     return True 
  
   

 