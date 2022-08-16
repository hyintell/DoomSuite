import time
from argparse import ArgumentParser, Namespace

from doomlab.envs.utils import create_env
from doomlab.envs.utils import get_tasks_by_level


def get_args():
    parser = ArgumentParser()
    parser.add_argument('--scenario', type=str, default='DefendTheCenter', help='Scenario to use')
    parser.add_argument('--level', type=int, default=0, help='Game level')
    parser.add_argument('--max_episodes', type=int, default=1, help='Number of episodes to run')
    parser.add_argument('--render', type=bool, default=True, help='Whether to render the environment')
    parser.add_argument('--render_sleep', type=float, default=0.05, help='Time to sleep between rendering')
    return parser.parse_args()


def run(args: Namespace) -> None:
    envs = get_tasks_by_level("DefendTheCenter", args.level)
    scenario = args.scenario
    for env_n in envs:
        task = env_n
        env = create_env(scenario, task, "DefendTheCenter")
        args.state_shape = env.observation_space
        args.action_shape = env.action_space.shape or env.action_space.n
        print("Observation space:", env.observation_space.shape)
        print("Action space:", env.action_space)

        for ep in range(args.max_episodes):
            env.reset()
            done = False
            steps = 0
            rewards = []
            while not done:
                state, reward, done, info = env.step(env.action_space.sample())
                steps += 1
                rewards.append(reward)
                if args.render:
                    env.render()
                    time.sleep(args.render_sleep)
            print(f"Episode {ep + 1} reward: {sum(rewards)}, steps: {steps}")
    env.close()

if __name__ == '__main__':
    run(get_args())
