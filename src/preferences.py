import numpy as np

def generate_uniform_preferences(n_agents, n_choices, seed=None):
    rng = np.random.default_rng(seed)
    return [rng.permutation(n_choices).tolist() for _ in range(n_agents)]

