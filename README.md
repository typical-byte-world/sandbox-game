# Alien spaceships
*The project is going to consist of 3 main components:*
##### 1. The game - (player can move the spaceship, shoot enemies, collect data in automatic way)  
  
> The game is the core of the project. In the game, a player can play in two modes:  
> by himself or by NN. When a player plays on his own the game can collect the data  
> (screenshot for every pressed button). In the future, the game will be able to retrain  
> a NN after a data collection process.

##### 2. A neural network that is going to be a self-driving spaceship

> The neural network is going to be written in Pytorch.  
> As input it gets a screenshot of the game and output  
> will be a 5 classes - up, down, left, right or shoot.

##### 3. Neural network explainer in time.
> Part of the game's screen is going to be dedicated to autopilot.
> It will show the smth similar to SHAP value

Things to do now:
- add different enemies and obstacles
- refactor the project
- collect data, process it
- NN: train, evaluate, etc.