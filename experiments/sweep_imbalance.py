import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import matplotlib.pyplot as plt
from gale_shapley import DeferredAcceptanceMarket

# sweep params
n = 80  # receivers (fixed)
alphas = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]  # imbalance ratios m/n
d = 30  # list length
trials = 100
seed = 0

def sweep_imbalance():
    results = []
    
    for alpha in alphas:
        m = int(alpha * n)
        all_ranks = []
        total_matched = 0
        
        print(f"running alpha={alpha:.2f} (m={m}, n={n})...")
        
        for t in range(trials):
            market = DeferredAcceptanceMarket(m, n, d, seed + t)
            matching = market.run()
            
            for p_id, r_id in matching.items():
                p = market.proposers[p_id]
                rank = p.get_rank(r_id)
                all_ranks.append(rank)
            
            total_matched += len(matching)
        
        mean_rank = np.mean(all_ranks) if all_ranks else np.nan
        frac_matched = total_matched / (m * trials)
        
        results.append({
            'alpha': alpha,
            'm': m,
            'mean_rank': mean_rank,
            'frac_matched': frac_matched
        })
        
        print(f"  mean rank: {mean_rank:.2f}, frac matched: {frac_matched:.2f}")
    
    # plot
    os.makedirs('../results', exist_ok=True)
    
    plt.figure(figsize=(8, 5))
    plt.plot([r['alpha'] for r in results], 
             [r['mean_rank'] for r in results], 
             'o-', linewidth=2, markersize=8)
    plt.xlabel('imbalance ratio (α = m/n)')
    plt.ylabel('mean proposer rank')
    plt.title('proposer welfare vs market imbalance')
    plt.grid(alpha=0.3)
    plt.axvline(1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='balanced')
    plt.legend()
    plt.tight_layout()
    plt.savefig('../results/imbalance_sweep.png', dpi=150)
    print("\nsaved plot to results/imbalance_sweep.png")

if __name__ == "__main__":
    sweep_imbalance()

