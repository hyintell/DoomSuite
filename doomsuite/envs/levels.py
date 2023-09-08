from argparse import Namespace
from collections import deque
from typing import Dict, List

import numpy as np

from doomsuite.envs.core import DoomEnv
from doomsuite.envs.utils import distance_traversed


class DefendTheCenter(DoomEnv):
    """
    In this scenario, the agent is spawned in the center of a circular room. Enemies are spawned at fixed positions
    alongside the wall of the area. The enemies do not possess a projectile attack and therefore have to make their way
    within melee range to inflict damage. The agent is rendered immobile, but equipped with a weapon and limited
    ammunition to fend off the encroaching enemies. Once the enemies are killed, they respawn at their original location
    after a fixed time delay. The objective of the agent is to survive as long as possible. The agent is rewarded for
    each enemy killed.
    """

    def __init__(self, scenario: str, task=None, map_paths=None, visible=False):
        super().__init__(scenario, task, map_paths, visible)
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

    def __init__(self, scenario: str, task=None, map_paths=None, visible=False):
        super().__init__(scenario, task, map_paths, visible)
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


class RunAndGun(DoomEnv):
    """
    In this scenario, the agent is randomly spawned in one of 20 possible locations within a maze-like environment, and
    equipped with a weapon and unlimited ammunition. A fixed number of enemies are spawned at random locations at the
    beginning of an episode. Additional enemies will continually be added at random unoccupied locations after each time
    interval. The enemies are rendered immobile, forcing them to remain at their fixed locations. The goal of the agent
    is to locate and shoot the enemies. The agent can move forward, turn left and right, and shoot. The agent is granted
    a reward for each enemy killed.
    """

    def __init__(self, scenario: str, task=None, map_paths=None, visible=False):
        super().__init__(scenario, task, map_paths, visible)
        self.reward_kill = 1.0

    def get_available_actions(self) -> List[List[float]]:
        actions = []
        t_left_right = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
        m_forward = [[0.0], [1.0]]
        shoot = [[0.0], [1.0]]
        for t in t_left_right:
            for m in m_forward:
                for e in shoot:
                    actions.append(t + m + e)
        return actions

    def calc_reward(self) -> float:
        reward = 0.0
        if len(self.game_variable_buffer) < 2:
            return reward

        current_vars = self.game_variable_buffer[-1]
        previous_vars = self.game_variable_buffer[-2]

        if current_vars[1] > previous_vars[1]:
            reward += self.reward_kill  # Elimination of an enemy

        return reward


class RunAndGunV1(RunAndGun):

    def __init__(self, scenario: str, task=None, map_paths=None, reward_kill=1.0, reward_scaler_traversal=0.001):
        super().__init__(scenario, task, map_paths, reward_kill, reward_scaler_traversal)
        self.reward_scaler_traversal = reward_scaler_traversal
        self.distance_buffer = []
        self.hits_taken = 0
        self.ammo_used = 0

    def calc_reward(self) -> float:
        reward = super().calc_reward()
        # Utilize a dense reward system by encouraging movement
        distance = distance_traversed(self.game_variable_buffer, 3, 4)
        self.distance_buffer.append(distance)
        reward += distance * self.reward_scaler_traversal  # Increase reward linearly

        current_vars = self.game_variable_buffer[-1]
        previous_vars = self.game_variable_buffer[-2]

        if current_vars[0] < previous_vars[0]:
            self.hits_taken += 1
        if current_vars[2] < previous_vars[2]:
            self.ammo_used += 1

        return reward

    def get_statistics(self) -> Dict[str, float]:
        if not self.game_variable_buffer:
            return {}
        variables = self.game_variable_buffer[-1]
        return {f'health': variables[0],
                f'kills': variables[1],
                f'ammo': self.ammo_used,
                f'movement': np.mean(self.distance_buffer).round(3),
                f'hits_taken': self.hits_taken}

    def clear_episode_statistics(self) -> None:
        super().clear_episode_statistics()
        self.distance_buffer.clear()
        self.hits_taken = 0
        self.ammo_used = 0
