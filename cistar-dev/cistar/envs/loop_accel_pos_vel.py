from cistar.envs.loop import LoopEnvironment

from rllab.spaces import Box

import traci

import numpy as np
from rllab.spaces import Product
import pdb


"""
Fully functional environment. Takes in an *acceleration* as an action. Reward function is negative norm of the
difference between the velocities of each vehicle, and the target velocity. State function is a vector of the
velocities and positions for each vehicle.
"""
class ExtendedAccelerationEnvironment(LoopEnvironment):


    @property
    def action_space(self):
        """
        Actions are a set of accelerations from 0 to 15m/s
        :return:
        """
        #TODO: max and min are parameters
        return Box(low=self.env_params["max-deacc"], high=self.env_params["max-acc"], shape=(self.scenario.num_rl_vehicles, ))

    @property
    def observation_space(self):
        """
        See parent class
        An observation is an array the velocities for each vehicle
        """
        num_cars = self.scenario.num_vehicles
        ypos = Box(low=0., high=np.inf, shape=(num_cars, ))
        vel = Box(low=0., high=np.inf, shape=(num_cars, ))
        self.obs_var_labels = ["Velocity", "Distance"]
        return Product([vel, ypos])

    def apply_action(self, car_id, action):
        """
        See parent class (base_env)
         Given an acceleration, set instantaneous velocity given that acceleration.
        """
        thisSpeed = self.vehicles[car_id]['speed']
        nextVel = thisSpeed + action * self.time_step
        nextVel = max(0, nextVel)
        # if we're being completely mathematically correct, 1 should be replaced by int(self.time_step * 1000)
        # but it shouldn't matter too much, because 1 is always going to be less than int(self.time_step * 1000)
        traci.vehicle.slowDown(car_id, nextVel, 1)

    def compute_reward(self, state):
        """
        See parent class
        """
        return -np.linalg.norm(state[0] - self.env_params["target_velocity"])

    def getState(self):
        """
       See parent class
       The state is an array of velocities and distance for each vehicle
       :return: an array of vehicle speed and distance for each vehicle
       """
        return np.array([[self.vehicles[veh_id]["speed"], \
                        self.get_headway(veh_id)] for veh_id in self.vehicles]).T

    def render(self):
        print('current state/velocity:', self._state)