"""
find minimal d* for perfect matching using binary search.
for each (n, α) pair, find smallest d where P(perfect matching) >= 0.8
"""

import os
import sys
import time
import csv
import numpy as np
from math import log, ceil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from gale_shapley import DeferredAcceptanceMarket

# experiment parameters
N_VALUES = [500, 1000, 2000, 5000]
ALPHA_REGIMES = {'Small': 1.5, 'Medium': 7.0, 'Large': 15.0}
TARGET_PROB = 0.8  # we want at least 80% perfect matching rate
SEED = 42


def test_d(n, alpha, d, num_trials, seed):
    """
    run num_trials experiments and return the fraction that got perfect matching.
    """
    # compute number of proposers from imbalance ratio
    m = round(n * (1 + alpha))
    rng = np.random.default_rng(seed)
    
    successes = 0
    for _ in range(num_trials):
        # run one deferred acceptance trial
        trial_seed = rng.integers(0, 2**31)
        market = DeferredAcceptanceMarket(m, n, d, trial_seed)
        matching = market.run()
        
        # perfect matching means all n receivers got matched
        if len(set(matching.values())) == n:
            successes += 1
    
    return successes / num_trials


def find_d_star(n, alpha, seed):
    """
    binary search to find minimal d where perfect matching rate >= TARGET_PROB.
    returns (d_star, final_rate).
    """
    # start with a reasonable search range
    # d must be at least 1, and at most n (full preferences)
    d_low = 1
    d_high = max(1, ceil(log(n) ** 2))  # start small, expand if needed
    
    # if our initial upper bound doesn't work, expand it
    while test_d(n, alpha, d_high, 10, seed) < TARGET_PROB:
        d_high *= 2
        if d_high > n:
            d_high = n
            break
    
    # binary search for minimal d
    while d_low < d_high:
        mid = (d_low + d_high) // 2
        rate = test_d(n, alpha, mid, 20, seed + mid)
        
        if rate >= TARGET_PROB:
            d_high = mid  # mid works, try smaller
        else:
            d_low = mid + 1  # mid too small, try larger
    
    # confirm with more trials
    d_star = d_low
    final_rate = test_d(n, alpha, d_star, 100, seed + d_star * 100)
    
    return d_star, final_rate


def run_experiment():
    """
    main experiment loop: find d* for each (n, alpha) combination.
    """
    results = []
    rng = np.random.default_rng(SEED)
    
    print(f"finding minimal d* for perfect matching (target: {TARGET_PROB*100:.0f}%)")
    print(f"market sizes: {N_VALUES}")
    print(f"regimes: {list(ALPHA_REGIMES.keys())}")
    print("-" * 50)
    
    for regime, alpha in ALPHA_REGIMES.items():
        print(f"\n{regime} regime (α={alpha}):")
        
        for n in N_VALUES:
            m = round(n * (1 + alpha))
            seed = rng.integers(0, 2**31)
            
            start = time.time()
            d_star, rate = find_d_star(n, alpha, seed)
            elapsed = time.time() - start
            
            print(f"  n={n:4d}, m={m:5d} → d*={d_star}, rate={rate:.2f}, time={elapsed:.1f}s")
            
            results.append({
                'regime': regime,
                'alpha': alpha,
                'n': n,
                'm': m,
                'd_star': d_star,
                'perfect_rate': rate,
                'trials_total': 100,
                'time_seconds': elapsed
            })
            
            # save after each run in case of crash
            save_results(results)
    
    print("-" * 50)
    print(f"done! results saved to results/threshold_results.csv")
    return results


def save_results(results):
    """write results to csv file."""
    os.makedirs('../results', exist_ok=True)
    with open('../results/threshold_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'regime', 'alpha', 'n', 'm', 'd_star', 'perfect_rate', 'trials_total', 'time_seconds'
        ])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    run_experiment()
