# rl_engine/agent.py
import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO

class RLDefender:
    def __init__(self, env_id="SecurityGym-v0"):
        self.env = gym.make(env_id)
        self.model = PPO("MlpPolicy", self.env, verbose=1)

    def train(self, timesteps=10_000):
        self.model.learn(total_timesteps=timesteps)
        self.model.save("aegis_rl_defender")

    def predict(self, observation):
        action, _ = self.model.predict(observation, deterministic=True)
        return action