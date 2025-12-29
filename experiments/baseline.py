import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import matplotlib.pyplot as plt

from gale_shapley import gale_shapley, is_stable_matching
from preferences import generate_uniform_preferences


# constants
N = 100  # number of proposers
M = 100  # number of receivers
TRIALS = 300
SEED = 0


def run_baseline():
    """
    Run the baseline experiment with uniform random preferences.
    """
    all_proposer_ranks = []
    perfect_count = 0
    total_matched = 0

    # run small stability checks for first 3 trials
    for t in range(TRIALS):
        trial_seed = SEED + t

        # generate preferences
        proposers_prefs = generate_uniform_preferences(N, M, seed=trial_seed)
        receivers_prefs = generate_uniform_preferences(M, N, seed=trial_seed + 10_000)

        # run matching
        matching = gale_shapley(proposers_prefs, receivers_prefs)

        # stability check for first 3 trials on small size
        if t < 3:
            small_n, small_m = 8, 8
            small_proposers = generate_uniform_preferences(small_n, small_m, seed=trial_seed)
            small_receivers = generate_uniform_preferences(small_m, small_n, seed=trial_seed + 10_000)
            small_matching = gale_shapley(small_proposers, small_receivers)
            assert is_stable_matching(small_proposers, small_receivers, small_matching), \
                f"Stability check failed for trial {t}"
            if t == 0:
                print("✓ Stability checks passed for first 3 trials (N=8, M=8)")

        # compute proposer rank statistics
        trial_ranks = []
        for p in range(N):
            if p in matching:
                r = matching[p]
                # find 1-indexed rank (add 1 to 0-indexed position)
                rank = proposers_prefs[p].index(r) + 1
                trial_ranks.append(rank)

        all_proposer_ranks.extend(trial_ranks)

        # check if perfect matching
        if len(matching) == N:
            perfect_count += 1

        total_matched += len(matching)

    # compute statistics
    mean_rank = np.mean(all_proposer_ranks)
    fraction_perfect = perfect_count / TRIALS
    avg_matched = total_matched / TRIALS

    # print results
    print(f"\n{'='*60}")
    print("BASELINE EXPERIMENT RESULTS")
    print(f"{'='*60}")
    print(f"Mean proposer rank (1-indexed): {mean_rank:.3f}")
    print(f"Fraction perfect matchings: {fraction_perfect:.3f}")
    print(f"Average matched proposers: {avg_matched:.1f} / {N}")
    print(f"{'='*60}\n")

    # generate plot
    results_dir = os.path.join(os.path.dirname(__file__), '../results')
    os.makedirs(results_dir, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.hist(all_proposer_ranks, bins=range(1, M + 2), edgecolor='black', alpha=0.7)
    plt.xlabel('Proposer Rank of Matched Receiver (1 = best)')
    plt.ylabel('Frequency')
    plt.title('Uniform Preferences Baseline (Proposer Ranks)')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    plot_path = os.path.join(results_dir, 'baseline_plot.png')
    plt.savefig(plot_path, dpi=150)
    print(f"✓ Plot saved to {plot_path}\n")


if __name__ == "__main__":
    run_baseline()

