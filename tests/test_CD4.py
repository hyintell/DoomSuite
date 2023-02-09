import time
from argparse import ArgumentParser, Namespace

from doomlab.envs.utils import create_env, get_tasks_by_sequence


def get_args():
    parser = ArgumentParser()
    parser.add_argument('--sequence', type=str, default='CD4', choices=['CD4', 'CO4', 'CD8', 'CO8'],
                        help='Continual Learning sequence abbreviation')
    parser.add_argument('--n_episodes', type=int, default=1, help='Number of episodes to run per task')
    parser.add_argument('--render', type=bool, default=True, help='Whether to render the environment')
    parser.add_argument('--render_sleep', type=float, default=0.05, help='Time to sleep between rendering')
    parser.add_argument('--reward_scaler_traversal', type=float, default=0.001, help='Time to sleep between rendering')
    return parser.parse_args()


def run(args: Namespace) -> None:
    tasks = get_tasks_by_sequence(args.sequence)
    for scenario in tasks:
        for env_name in tasks[scenario]:
            env = create_env(scenario, env_name, True)
            args.state_shape = env.observation_space
            args.action_shape = env.action_space.shape or env.action_space.n
            print("Observation space:", env.observation_space.shape)
            print("Action space:", env.action_space)

            for ep in range(args.n_episodes):
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
