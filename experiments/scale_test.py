import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from math import log, ceil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from gale_shapley import DeferredAcceptanceMarket

def d_policy_logsq(n, c=1.0):
    """d = ceil(c * (ln(n))^2)"""
    return max(1, min(n, ceil(c * log(n)**2)))

def run_single_trial(m, n, d, seed):
    """run one market trial"""
    start = time.perf_counter()
    market = DeferredAcceptanceMarket(m, n, d, seed)
    matching = market.run()
    runtime = time.perf_counter() - start
    
    ranks = []
    for p_id, r_id in matching.items():
        proposer = market.proposers[p_id]
        rank = proposer.get_rank(r_id)
        ranks.append(rank)
    
    avg_rank = np.mean(ranks) if ranks else float('nan')
    
    return {
        'runtime': runtime,
        'avg_rank': avg_rank,
        'matched_proposers': len(matching)
    }

def scale_test(alpha, n_values, trials=5, seed=0):
    """test scaling for fixed alpha"""
    results = []
    
    rng = np.random.default_rng(seed)
    
    for n in n_values:
        m = round(n * (1 + alpha))
        d = d_policy_logsq(n, c=1.0)
        
        print(f'testing n={n}, alpha={alpha:.1f}, m={m}, d={d}...')
        
        trial_results = []
        for t in range(trials):
            trial_seed = rng.integers(0, 2**32 - 1)
            res = run_single_trial(m, n, d, trial_seed)
            trial_results.append(res)
        
        avg_runtime = np.mean([r['runtime'] for r in trial_results])
        avg_rank = np.mean([r['avg_rank'] for r in trial_results if not np.isnan(r['avg_rank'])])
        
        results.append({
            'n': n,
            'm': m,
            'alpha': alpha,
            'd': d,
            'runtime': avg_runtime,
            'avg_rank': avg_rank
        })
        
        print(f'  avg runtime: {avg_runtime:.3f}s, avg rank: {avg_rank:.2f}')
    
    return results

def plot_scaling_results(all_results):
    """plot runtime and rank vs n for different alphas"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # group by alpha
    alphas = sorted(set(r['alpha'] for results in all_results for r in results))
    
    colors = ['blue', 'orange', 'green']
    
    for alpha, color in zip(alphas, colors):
        # filter results for this alpha
        alpha_results = [r for results in all_results for r in results if r['alpha'] == alpha]
        alpha_results = sorted(alpha_results, key=lambda x: x['n'])
        
        n_vals = [r['n'] for r in alpha_results]
        runtimes = [r['runtime'] for r in alpha_results]
        ranks = [r['avg_rank'] for r in alpha_results]
        
        # runtime vs n
        axes[0].plot(n_vals, runtimes, 'o-', label=f'α={alpha:.1f}', color=color, linewidth=2)
        
        # rank vs n
        axes[1].plot(n_vals, ranks, 'o-', label=f'α={alpha:.1f}', color=color, linewidth=2)
    
    axes[0].set_xlabel('n (receivers)')
    axes[0].set_ylabel('runtime (seconds)')
    axes[0].set_title('runtime vs market size')
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    axes[1].set_xlabel('n (receivers)')
    axes[1].set_ylabel('avg proposer rank')
    axes[1].set_title('rank vs market size')
    axes[1].set_xscale('log')
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('../results/scaling_test.png', dpi=150)
    print('\nsaved scaling_test.png')

if __name__ == "__main__":
    print('starting scaling test...')
    print('d-policy: logsq with c=1.0')
    print()
    
    # test three regimes
    alphas_to_test = [2, 7, 19]  # small, medium, large imbalance
    n_values = [500, 1000, 2000, 5000]
    
    all_results = []
    
    for alpha in alphas_to_test:
        print(f'\n=== testing alpha={alpha} (regime) ===')
        results = scale_test(alpha, n_values, trials=5, seed=0)
        all_results.append(results)
    
    plot_scaling_results(all_results)
    
    print('\nscaling test complete')

