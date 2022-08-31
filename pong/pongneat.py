# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 15:42:50 2022

@author: X2029440
"""

import neat 
import pickle
from player import Player, Color 
from ball import Ball 
import pygame  
import itertools 
import sys 
import numpy as np 
import time 
import sys 
import datetime 
import random 


#class to 'train' using NEAT algo 

#generation : make all players play against all other players (all combinations of 2 players, 1vs1)
#each generation, keep players of our population with best fitness, mutate best players and start over with new population 
#fitness : number of wins in a generation 

class PongNeat : 
  
  def __init__(self, window_width, window_height, nb_gens) : 
    
    
    self.window_width, self.window_height = window_width, window_height
    
    self.players = []
    self.players_pairs = [] #list of tuples (all possibles 2 players combinations, all possible 1vs1)
    
    #currently playing players 
    self.player1 = None #right player 
    self.player2 = None #left player
    self.game_over = False 
    
    self.time = 0 #datetime object (to display time while training)
    
    #playing player's numbers
    self.playing_players = [None, None] #[int, int] -> left_player_number, right_player_number
    
    self.slow_down = False #slow down learning process
    
    self.game_length = 0 #length of last game (stop training process if 2 AIs've been playing for too long)
    
    self.ball = Ball(400, 250)
    
    self.nb_gens = nb_gens #number of generations 
    self.current_gen = 1 #current generation
    
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
    
    my_font2 = pygame.font.SysFont('Calibri', 30, bold=True)
    nb_gens = my_font2.render('GEN : ' + str(self.current_gen) + '/' + str(self.nb_gens), False, Color.RED.value)
    
    game_length = my_font2.render('GAME LENGTH : ' + str(self.game_length), False, Color.RED.value)
    playing_players = my_font2.render('P' + str(self.playing_players[0]) + ' VS ' + 'P' + str(self.playing_players[1]), 
                                      False, Color.RED.value)
    
    time = my_font2.render(str(self.time), False, Color.RED.value)

    self.display.blit(score1, (450,0))
    self.display.blit(score2, (350 - score2.get_width(), 0))
    
    self.display.blit(nb_gens, (20,0))
    self.display.blit(game_length, (20,30))
    self.display.blit(playing_players, (20,60))
    self.display.blit(time, (770 - time.get_width(), 10))
    
    
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
    


  #update game variables and ui at each frame 
  def update(self, net1, net2) : 
    
    #draw
    self.draw_map()
    self.draw_scores()
    
    self.ball.draw_ball(self.display)
    self.draw_states()
  
    self.player1.draw_paddle(self.display)
    self.player2.draw_paddle(self.display)
    
    #move
    self.ball.move()
    
    #let's pass the gamestate through our neat's networks
    output1 = net1.activate(self.player1.get_game_state(self.ball, False)) 
    output2 = net2.activate(self.player2.get_game_state(self.ball, True)) 
    
    #actions     
    action1 = np.argmax(output1) 
    action2 = np.argmax(output2)
    
    self.player1.move_neat(action1, False, dt=10)
    self.player2.move_neat(action2, True, dt=10)
    
    #collisions (player, ball), (ball, up and down borders), (ball, left and right borders
    #collision with up and down borders
    if self.nb_loops - self.last_collision > 2 : #to avoid multiple collisions in a row 
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
        if self.ball.x > 400 : self.player2.score += 1; self.player2.nb_wins +=1; self.game_over = True 
        else : self.player1.score += 1; self.player1.nb_wins +=1; self.game_over = True 

    pygame.display.update()  


  #if you want to run the game and play yourself
  def run_game(self, net1, net2):

    next_update = 0  #time of next update 
    dt_updates = 1/np.inf #time btw two updates
    
    while not self.game_over : #game loop 

      current_time = pygame.time.get_ticks()/1000 #in seconds 
      
      #update ui 
      if  current_time >= next_update :  #update game only every 'FPS' seconds
        next_update = current_time + dt_updates

        self.nb_loops += 1 
        self.game_length += 1
        
        self.update(net1, net2)

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
        time.sleep(0.01)
          
          
  
  #this function loops everytime it comes to its end 
  #every loop, new population (new genomes and networks) is made out of the best players (players with best fitness)
  def eval_genomes(self, genomes, config) : 
    
    try : 
      
      #nets : neural networks attached to each player 
      #ge : genome object attached to each player (for fitness) 
      nets, ge = [], [] 
      self.players = []
  
      for genome_id, genome in genomes : 
        genome.fitness = 0 #initialize fitness 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        ge.append(genome)
        self.players.append(Player())
  
      #we make all possible 1vs1
      self.players_pairs = [list(item) for item in itertools.combinations(self.players, 2)] #all possible 1vs1 (2 out of n)
      players_pairs_nb = [list(item) for item in itertools.combinations(range(len(self.players)), 2)] #pairs of numbers (all possible VS)
      nets_pairs = [list(item) for item in itertools.combinations(nets, 2)] #all possible pairs of nets
      
      for i, (player1, player2) in enumerate(self.players_pairs) :
        
        seconds = int(pygame.time.get_ticks()/1000)
        self.time = datetime.timedelta(seconds=seconds)
  
        self.playing_players = players_pairs_nb[i][::-1] #left player, right player
    
        self.game_length = 0 
         
        self.ball = Ball(400, 250) #new ball for each game 
        
        self.game_over = False 
        
        #we reinitialize each player (which may already have played before)
        player1.score = 0 
        player2.score = 0 
        
        player1.x = 785 #right player 
        player2.x = 5 #left player 
        
        player1.y = 190 
        player2.y = 190 
        
        self.player1 = player1 
        self.player2 = player2 
        
        net1 = nets_pairs[i][0]
        net2 = nets_pairs[i][1]
        
        self.run_game(net1, net2) #make player1 play against player 2
        
        #dict with : player's nb - nb of wins
        print('wins:', dict(zip(range(len(self.players)), [player.nb_wins for player in self.players]))) 
        
      #update fitness
      for i, genome in enumerate(ge) :#fitness is the player's number of wins 
        genome.fitness = self.players[i].nb_wins
        
      self.current_gen += 1 
    
    finally : #in case we stop the program before the end, we save best player so far (most wins)
      
      lst_wins = [player.nb_wins for player in self.players] #number of wins for each player
      max_idx = lst_wins.index(max(lst_wins)) #index of best player
      with open('model.pkl', 'wb') as f:
          pickle.dump(nets[max_idx], f)
          print('model saved')
    
    
  #to run neat algo using eval_genomes function in which we define what to do during one generation
  def run(self, config_file, nb_gens):

    
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    winner = p.run(self.eval_genomes, nb_gens) #eval_genomes(genomes, config) function where we treat our genomes (doesn't return anythign)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
    #save best player's network (most wins)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    with open('model.pkl', 'wb') as f:
        pickle.dump(winner_net, f)
        print("winner's model saved")
          

  

          
if __name__ == "__main__":
  
  window_width = 800
  window_height = 500
  
  nb_gens = 50 #number of generations 
  game = PongNeat(window_width, window_height, nb_gens)
  
  config_path = r"C:\Users\X2029440\OneDrive - RATP SMART SYSTEMS\Bureau\pong\config-feedforward.txt"
  
  #train AIs with neat algorithm
  #you can slow down process using mousewheel 
  game.run(config_path, nb_gens)