import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import matplotlib.pyplot as plt
from gale_shapley import DeferredAcceptanceMarket

# params: m proposers (long side), n receivers (short side), d = list length
m = 100
n = 80
d = 30
trials = 300
seed = 0

def run_demo():
    all_ranks = []
    total_matched = 0
    
    for t in range(trials):
        market = DeferredAcceptanceMarket(m, n, d, seed + t)
        matching = market.run()
        
        # compute ranks for this trial
        for p_id, r_id in matching.items():
            p = market.proposers[p_id]
            rank = p.proposals_order.index(r_id) + 1
            all_ranks.append(rank)
        
        total_matched += len(matching)
    
    # aggregate stats
    avg_matched = total_matched / trials
    frac_matched = avg_matched / m
    
    print(f"\navg matched proposers: {avg_matched:.1f} / {m}")
    print(f"avg unmatched proposers: {m - avg_matched:.1f}")
    print(f"fraction matched: {frac_matched:.2f}")
    print(f"mean proposer rank: {np.mean(all_ranks):.2f}")
    
    # plot
    os.makedirs('../results', exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.hist(all_ranks, bins=range(1, d+2), edgecolor='black', alpha=0.7)
    plt.axvline(np.mean(all_ranks), color='red', linestyle='--', linewidth=2,
                label=f'mean={np.mean(all_ranks):.1f}')
    plt.xlabel('proposer rank')
    plt.ylabel('frequency')
    plt.title(f'on-demand DA (m={m}, n={n}, d={d}, trials={trials})')
    plt.legend()
    plt.tight_layout()
    plt.savefig('../results/on_demand_baseline.png', dpi=150)
    print("saved plot\n")

if __name__ == "__main__":
    run_demo()

