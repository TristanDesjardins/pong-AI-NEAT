# Prong game AI - NEAT genetic algorithm
Pong AIs using Neuroevolution of augmenting topologies aka NEAT (with neat library and pygame) \
Project done in my free time as a challenge 

## Preview 
**training phase** <br/> AI vs. AI            |   <img src="https://user-images.githubusercontent.com/62900180/188200339-c6165305-17d7-4f1e-8640-089a623e577f.gif" width="500"/>
:-------------------------:|:-------------------------:
 **After training <br/> AI vs. AI** | <img src="https://user-images.githubusercontent.com/62900180/188200362-09725b05-5a96-4d21-97f6-175df65fdc23.gif" width="500"/>


## General Idea 
Here's how I adapted NEAT for my case: 
  - We generate N pong players and associate them N randomly initialized neural networks
  - We make them all play against eachother or 'all-play-all' (2 out of N possibilities)
  - I've decided to define fitness of a genome as the number of wins of a player
  - We can then take the best players (players with most fitness), mutate them, and start over with a new population. 

We repeat this process (called a generation) until players are good enough. 

Check NEAT algo for more info. 

## Main files :
- pontneat.py : to run NEAT algo and save best model 
- pong.py : 3 modes ['multi', 'solo', 'ai']
    - multi : play against your friend (arrow keys and 'z', 's' keys) 
    - solo : play against AI 
    - ai : AI playing against itself 

## Installation 
- Python 3.9.12
- [pygame 2.1.2](https://www.pygame.org/news) : for the game engine 
- [neat 0.4.1](https://neat-python.readthedocs.io/en/latest/installation.html) : for the AI 


