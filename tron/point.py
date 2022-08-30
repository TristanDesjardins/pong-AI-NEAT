# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 17:18:43 2022

@author: X2029440
"""

import numpy as np 


#class used for game states 
#gives information of one point's position relative to another one 
class Point : 

  
    #rotate n times a list 
    @staticmethod
    def rotate(l, n):
        return l[n:] + l[:n]


    #get position of pt2 relative to pt1
    #return vector with 0s and 1 in the right place
    #[N, NE, E, SE, S, SO, O, NO] #clockwise (S:sud, N:nord, E:est, O:ouest)
    #ex : [0,1,0,0,0,0,0,0] signifie que pt2 est au nord est de pt1 (on suppose que pt1 fait face vers le haut)
    @staticmethod
    def get_relative_position(pt1, pt2) : 

        relative_position = [0 for k in range(8)] 
        diff = (pt2[0] - pt1[0], pt2[1] - pt1[1])

        if diff[0] == 0 and diff[1] < 0 : relative_position[0] = 1 
        elif diff[0] == 0 and diff[1] > 0 : relative_position[4] = 1 
        elif diff[0] > 0 and diff[1] == 0 : relative_position[2] = 1
        elif diff[0] < 0 and diff[1] == 0 : relative_position[6] = 1

        elif diff[0] < 0 and diff[1] < 0 : relative_position[7] = 1
        elif diff[0] > 0 and diff[1] > 0 : relative_position[3] = 1
        elif diff[0] < 0 and diff[1] > 0 : relative_position[5] = 1
        elif diff[0] > 0 and diff[1] < 0 : relative_position[1] = 1

        return relative_position


    @staticmethod  
    #idem get_relative_position() mais on prend en compte la direction vers laquelle pointe pt1
    #direction : direction de pt1 
    # par exemple, si pt2 est à droite de pt1 et que pt1 est dirigé vers la droite, alors pt2 est en fait au nord de pt1 
    #ex : [0,1,0,0,0,0,0,0] signifie que pt2 est au nord est de pt1 (en prenant en compte la direction de pt1)
    def get_relative_position_with_direction(pt1, pt2, direction) :  
        if direction == 'UP' : return Point.rotate(Point.get_relative_position(pt1, pt2),0)
        elif direction == 'RIGHT' : return Point.rotate(Point.get_relative_position(pt1, pt2),2)
        elif direction == 'DOWN' : return Point.rotate(Point.get_relative_position(pt1, pt2),4)
        elif direction == 'LEFT' : return Point.rotate(Point.get_relative_position(pt1, pt2),6)



    #renvoie un vecteur de taille 4  [N,E,S,O]
    #met un 1 à l'endroit ou se trouve pt2 par rapport à pt1 (uniquement s'ils se touchent !)
    # ex : [1,0,0,0] signifie que pt2 est au nord de pt1 et qu'ils se touchent
    #[0,0,0,0] signifie qu'ils ne se touchent pas 
    @staticmethod
    def get_relative_position_and_is_touching(pt1, pt2, direction) : 
        relative_position_with_direction = Point.get_relative_position_with_direction(pt1, pt2, direction)[::2] #on ne récupère que N,E,S,O
        #first check if pts are touching
        def are_touching(pt1, pt2) : 
            diff = (np.abs(pt1[0] - pt2[0]), np.abs(pt1[1] - pt2[1]))
            if 0 in diff and 1 in diff : return True 
            return False 
        return relative_position_with_direction if are_touching(pt1, pt2) else [0 for k in range(4)]
      
    @staticmethod
    def rotate_clockwise_n(x,y,ptn,n) : #n : number of rotations of 90 degrees around point ptn
      for k in range(n) : 
          x,y = y-ptn[1]+ptn[0], -(x-ptn[0])+ptn[1]
      return x,y
    

    