import numpy as np


def generate_uniform_preferences(n_agents, n_choices, seed=None):
    """
    generate independent uniform random preference lists.

    parameters
    ----------
    n_agents : int
        number of agents for which to generate preferences.
    n_choices : int
        number of distinct options each agent ranks (0 .. n_choices-1).
    seed : int or None, optional
        random seed for reproducibility. If None, use global entropy.

    returns
    -------
    list[list[int]]
        a list of length n_agents, where each element is a random
        permutation of range(n_choices).
    """
    rng = np.random.default_rng(seed)
    prefs = []
    base = np.arange(n_choices)
    for _ in range(n_agents):
        prefs.append(rng.permutation(base).tolist())
    return prefs


if __name__ == "__main__":
    # simple sanity check for reproducibility
    p1 = generate_uniform_preferences(3, 4, seed=123)
    p2 = generate_uniform_preferences(3, 4, seed=123)
    assert p1 == p2
    print("✓ Uniform preference generator sanity check passed.")

