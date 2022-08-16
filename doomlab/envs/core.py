import os
from argparse import Namespace
from collections import deque
from typing import Dict, Tuple, Any, List
import gym
import numpy as np
import vizdoom as vzd
from vizdoom import ScreenResolution


class DoomEnv(gym.Env):

    def __init__(self, scenario: str, task = None, map_pathes = None, visible = True, variable_queue_len = 5, frame_skip = 4, screen_resolution = ScreenResolution.RES_800X600):
        super().__init__()
        self.scenario = scenario
        if task == None:
            task = "default"
        self.task = task
        self.frame_skip = frame_skip

        # Create the Doom game instance
        self.game = vzd.DoomGame()
        if map_pathes == None:
            map_pathes = {}
            map_pathes["cfg"] = os.path.join(os.path.dirname(__file__), f"maps/{self.scenario}/{self.scenario}.cfg")
            map_pathes["wad"] = os.path.join(os.path.dirname(__file__), f"maps/{self.scenario}/{self.task}.wad")
        
        self.cfg_path = map_pathes["cfg"]
        self.wad_path = map_pathes["wad"]
        self.game.load_config(self.cfg_path)
        self.game.set_doom_scenario_path(self.wad_path)
        self.visible = visible
        self.game.set_window_visible(self.visible)
        if self.visible:  # Use a higher resolution for watching gameplay
            self.game.set_screen_resolution(screen_resolution)
        self.game.init()

        # Initialize and fill the game variable queue
        self.variable_queue_len = variable_queue_len
        self.game_variable_buffer = deque(maxlen=self.variable_queue_len)
        for _ in range(self.variable_queue_len):
            self.game_variable_buffer.append(self.game.get_state().game_variables)

        # Define the observation space
        self.game_res = (self.game.get_screen_height(), self.game.get_screen_width())
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=self.game_res, dtype=np.uint8
        )

        # Define the action space
        self.available_actions = self.get_available_actions()
        self.action_num = len(self.available_actions)
        self.action_space = gym.spaces.Discrete(self.action_num)

        self.extra_statistics = ['kills', 'health', 'ammo', 'movement', 'kits_obtained', 'hits_taken']
        self.spec = gym.envs.registration.EnvSpec(f'{task}-v0')
        self.count = 0

    def reset(self) -> np.ndarray:
        self.game.new_episode()
        self.count += 1
        self.clear_episode_statistics()
        return self.game.get_state().screen_buffer

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        action = self.available_actions[action]
        self.game.set_action(action)
        self.game.advance_action(self.frame_skip)

        state = self.game.get_state()
        reward = self.calc_reward()
        done = self.game.is_player_dead() or self.game.is_episode_finished() or not state
        info = self.get_statistics()

        observation = state.screen_buffer if state else np.zeros(self.game_res)
        if not done:
            self.game_variable_buffer.append(state.game_variables)
        return observation, reward, done, info

    def calc_reward(self) -> float:
        raise NotImplementedError

    def get_available_actions(self) -> List[List[float]]:
        raise NotImplementedError

    def get_statistics(self) -> Dict[str, float]:
        return {}

    def render(self, mode="human"):
        pass

    def clear_episode_statistics(self) -> None:
        pass

    def close(self):
        self.game.close()
