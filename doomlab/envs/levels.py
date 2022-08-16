from argparse import Namespace
from typing import Dict

from doomlab.envs.core import DoomEnv


class DefendTheCenter(DoomEnv):
    """
    In this scenario, the agent is spawned in the center of a circular room. Enemies are spawned at fixed positions
    alongside the wall of the area. The enemies do not possess a projectile attack and therefore have to make their way
    within melee range to inflict damage. The agent is rendered immobile, but equipped with a weapon and limited
    ammunition to fend off the encroaching enemies. Once the enemies are killed, they respawn at their original location
    after a fixed time delay. The objective of the agent is to survive as long as possible. The agent is rewarded for
    each enemy killed.
    """

    def __init__(self, scenario: str, task = None, map_pathes = None):
        super().__init__(scenario, task, map_pathes)
        self.kill_reward = 1.0

    def get_available_actions(self):
        actions = []
        attack = [[0.0], [1.0]]
        t_left_right = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
        for t in t_left_right:
            for a in attack:
                actions.append(t + a)
        return actions

    def calc_reward(self) -> float:
        reward = 0.0
        current_vars = self.game_variable_buffer[-1]
        previous_vars = self.game_variable_buffer[-2]

        if current_vars[0] > previous_vars[0]:
            reward += self.kill_reward  # Elimination of an enemy

        return reward

class DefendTheCenterV1(DefendTheCenter):

    def __init__(self, scenario: str, task = None, map_pathes = None):
        super().__init__(scenario, task, map_pathes)
        self.health_loss_penalty = 0.1
        self.ammo_used_penalty = 0.1

    def calc_reward(self) -> float:
        current_vars = self.game_variable_buffer[-1]
        previous_vars = self.game_variable_buffer[-2]

        reward = super().calc_reward()

        if current_vars[1] < previous_vars[1]:
            reward -= self.health_loss_penalty  # Loss of health
        if current_vars[2] < previous_vars[2]:
            reward -= self.ammo_used_penalty  # Use of ammunition

        return reward

    def get_statistics(self) -> Dict[str, float]:
        variables = self.game_variable_buffer[-1]
        return {'kills': variables[0], 'ammo': variables[2]}