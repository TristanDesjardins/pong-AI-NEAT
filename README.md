# pong-AI-NEAT
Pong AIs using NEAT (Neuroevolution of augmenting topologies).
Lil' project done in my free time as a challenge :blush: 

## General Idea 
Here's how I adapted NEAT for my case: 
  - We generate N pong players and associate them N randomly initialized neural networks
  - We make them all play against eachother or 'all-play-all' (2 out of N possibilities)
  - I've decided to define fitness of a genome as the number of wins of a player
  - We can then take the best players (players with most fitness), mutate them, and start over with a new population. 

We repeat this process (called a generation) until players are good enough. 

Check NEAT algo for more info. 

## Preview 

Just run 'pongneat.py' to see NEAT algo in action! :blush:
First generation : 
<img src='https://user-images.githubusercontent.com/62900180/187650832-4fc3fb0b-dc8f-4e9f-bbb5-a9b00ce1af38.gif' height="400">

<br/>

After just one generation, players are already better than you would ever be! :stuck_out_tongue:

<img src='https://user-images.githubusercontent.com/62900180/187650848-0e8fd93f-3dd1-4586-ad00-0784526c3705.gif' height="400">

<br/>

## Main files :
- pontneat.py : to run NEAT algo and save best model 
- pong.py : 3 modes ['multi', 'solo', 'ai']
    - multi : play against your friend (arrow keys and 'z', 's' keys) 
    - solo : play against AI 
    - ai : AI playing against itself 

## Installation 
- Python 3.9.12


