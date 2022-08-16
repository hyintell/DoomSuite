import os
import importlib
import yaml


LEV_CONFIG = None
with open(os.path.join(os.path.dirname(__file__), "config/levels.yaml"), "r") as f:
    try:
        LEV_CONFIG = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        assert False, "levels.yaml error: {}".format(exc)

def create_env(scenario_name, task_name = None, env_name = None):
    if env_name == None:
        scenario =  getattr(importlib.import_module("doomlab.envs.levels"), scenario_name)
    else:
        scenario =  getattr(importlib.import_module("doomlab.envs.levels"), env_name)
    map_pathes = {}
    map_pathes["cfg"] = os.path.join(os.path.dirname(__file__), f"maps/{scenario_name}/{scenario_name}.cfg")
    map_pathes["wad"] = os.path.join(os.path.dirname(__file__), f"maps/{scenario_name}/{task_name}.wad")
    env = scenario(scenario_name, task_name, map_pathes)
    return env

def get_tasks_by_level(scenario_name, level):
    level = "Level"+str(level)
    return LEV_CONFIG[scenario_name][level]