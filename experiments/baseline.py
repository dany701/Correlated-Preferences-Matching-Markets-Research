import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import matplotlib.pyplot as plt
from gale_shapley import gale_shapley
from preferences import generate_uniform_preferences

N = 100
M = 100
TRIALS = 300
SEED = 0

def run_baseline():
    all_ranks = []
    perfect = 0
    
    for t in range(TRIALS):
        seed = SEED + t
        props = generate_uniform_preferences(N, M, seed=seed)
        recvs = generate_uniform_preferences(M, N, seed=seed + 10000)
        
        matching = gale_shapley(props, recvs)
        
        for p in range(N):
            if p in matching:
                rank = props[p].index(matching[p]) + 1
                all_ranks.append(rank)
        
        if len(matching) == N:
            perfect += 1
    
    print(f"\nmean rank: {np.mean(all_ranks):.2f}")
    print(f"perfect matchings: {perfect}/{TRIALS}")
    
    # save plot
    os.makedirs('../results', exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.hist(all_ranks, bins=range(1, M+2), edgecolor='black', alpha=0.7)
    plt.xlabel('rank')
    plt.ylabel('frequency')
    plt.title('uniform random preferences')
    plt.tight_layout()
    plt.savefig('../results/baseline_plot.png', dpi=150)
    print("saved plot\n")

if __name__ == "__main__":
    run_baseline()

