import importlib
import os
from collections import deque
from typing import List, Dict

import yaml
from scipy import spatial


def load_conf(conf_name):
    global LEV_CONFIG
    with open(os.path.join(os.path.dirname(__file__), f"config/{conf_name}.yaml"), "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            assert False, f"{conf_name}.yaml error: {exc}"


LEV_CONFIG = load_conf('levels')
CL_CONFIG = load_conf('cl')


def create_env(scenario_name, task_name=None):
    scenario = getattr(importlib.import_module("doomlab.envs.levels"), scenario_name)
    map_paths = {}
    map_paths["cfg"] = os.path.join(os.path.dirname(__file__), f"maps/{scenario_name}/{scenario_name}.cfg")
    map_paths["wad"] = os.path.join(os.path.dirname(__file__), f"maps/{scenario_name}/{task_name}.wad")
    env = scenario(scenario_name, task_name, map_paths)
    return env


def get_tasks_by_level(scenario_name, level):
    level = "Level" + str(level)
    return LEV_CONFIG[scenario_name][level]


def get_tasks_by_sequence(sequence_name: str) -> Dict[str, List[str]]:
    return CL_CONFIG[sequence_name]


def distance_traversed(game_var_buf: deque, x_index: int, y_index: int) -> float:
    coordinates_curr = [game_var_buf[-1][x_index],
                        game_var_buf[-1][y_index]]
    coordinates_past = [game_var_buf[0][x_index],
                        game_var_buf[0][y_index]]
    return spatial.distance.euclidean(coordinates_curr, coordinates_past)
