# robot_ddpg
this ddpagent is based on keras_rl. When it comes to "envs" OpenAI is the way to go. Keras_rl works with the gyms out of the box. Here we have a custom env that communicates via websockets with a unity based so called RobotSimulation :) 

## Getting Started

just start the robot_ddpgagent.py and let it happen....

### Prerequisites

In order to work you need a websocket server that spreads all incoming messages.

### Installing

You do need a small number of libraries.

  - keras_rl
  - numpy
  - gym
 
## Acknowledgments

This solution works perfectly in combination with some stuff i've built and is a nice demonstrator for a distributed machine learning pipleline.
