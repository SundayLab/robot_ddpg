# core modules
import logging.config
import math
import random

# 3rd party modules
from gym import spaces
import gym
import numpy as np

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import threading
import json


def get_chance(x):
    """Get probability that a banana will be sold at price x."""
    e = math.exp(1)
    return (1.0 + e) / (1. + math.exp(x + 1))


class UnityRobotEnv(gym.Env):
    """
    Defining a simple environment for working with Unity based simulation
    """

    def on_message(self, ws, message):

       # self.observation = message.decode("utf-8")
        print("observation empfangen")
        self.observation = json.loads(message.decode("utf-8"))

        if type(self.observation) is dict:
           self.receivedObs = True

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        def run(*args):
            for i in range(3):
                time.sleep(1)
                ws.send("Hello %d" % i)
            time.sleep(1)
            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, ())

    def __init__(self):
        self.__version__ = "0.0.1"
        logging.info("Starting websocketclient")

        self.ws = websocket.WebSocketApp("ws://192.168.178.80:8080", on_message=self.on_message, on_close=self.on_close)
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()

        logging.info("UnityRobotEnv - Version {}".format(self.__version__))
        print("UnityRobotEnv - Version {}".format(self.__version__));

        # General variables defining the environment
        self.TOTAL_TIME_STEPS = 2
        self.curr_step = -1
        self.seeTarget = False
        self.receivedObs = False
        self.observation = {}

        # What the agent can do
        # 1: move forward
        # 2: move backward
        # 3: move left
        # 4: move right
        # 5: stop
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Discrete(3)

        # Store what the agent tried
        self.curr_episode = -1
        self.action_episode_memory = []

    def step(self, action):

        """
        The agent takes a step in the environment.
        Parameters
        ----------
        action : int
        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """

        if self.seeTarget:
            raise RuntimeError("Episode is done")
        self.curr_step += 1

        self._take_action(action.argmax())  #send action to unity and wait for response


        while not self.receivedObs: #wait for observation
          time.sleep(0.000001)

        ob = self._get_state()  # get observation from unity

        reward = self._get_reward()

        self.receivedObs = False

        return ob, reward, self.seeTarget, {}


    def _take_action(self, action):

        self.action_episode_memory[self.curr_episode].append(action)

        if action == 0:
            self.ws.send("forward")
        if action == 1:
            self.ws.send("backward")
        if action == 2:
            self.ws.send("left")
        if action == 3:
            self.ws.send("right")
        if action == 4:
            self.ws.send("stop")

    def _get_reward(self):
        """Reward is given for centering a target."""
        if len(self.observation) > 0 and self.observation["seeTarget"] == 0 and self.observation["isInCollision"] == 1:
            return -1.0
        elif len(self.observation) > 0 and self.observation["seeTarget"] == 1 and self.observation["isInCollision"] == 0:
            return 1/self.observation["targetDistance"]
        elif len(self.observation) > 0 and self.observation["targetDistance"] < 0.90 and self.observation["seeTarget"] == 0 :
            return -1.0
        else:
            return 0.0

    def reset(self):
        """
        Reset the state of the environment and returns an initial observation.
        Returns
        -------
        observation (object): the initial observation of the space.
        """
        self.curr_step = -1
        self.curr_episode += 1
        self.action_episode_memory.append([])
        self.seeTarget = False
        return self._get_state()

    def _render(self, mode='human', close=False):
        return

    def _get_state(self):
        if len(self.observation) > 0:
            return [self.observation["seeTarget"],self.observation["targetDistance"],self.observation["isInCollision"]]
        else:
            return[0,0,0]


    def seed(self, seed):
        random.seed(seed)
        np.random.seed