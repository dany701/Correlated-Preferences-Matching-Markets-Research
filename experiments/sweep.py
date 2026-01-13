import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

import numpy as np
import csv
import time
from gale_shapley import DeferredAcceptanceMarket

def theoretical_lower_bound(d, n, alpha):
    """compute theorem 3 lower bound on expected proposer rank"""
    if alpha <= 0:
        return 1.0
    numerator = 1 + alpha
    denominator = alpha + 1 / (n * (1 + alpha))
    return d / np.log(numerator / denominator)

def run_single_trial(m, n, d, seed):
    """run one trial and return metrics"""
    start_time = time.time()
    market = DeferredAcceptanceMarket(m, n, d, seed)
    matching = market.run()
    runtime = time.time() - start_time
    
    # matched receivers
    matched_receivers = len(set(matching.values()))
    perfect = (matched_receivers == n)
    
    # proposer ranks
    ranks = []
    for p_id, r_id in matching.items():
        p = market.proposers[p_id]
        rank = p.proposals_order.index(r_id) + 1
        ranks.append(rank)
    
    avg_rank = np.mean(ranks) if ranks else np.nan
    
    return {
        'avg_rank': avg_rank,
        'perfect': perfect,
        'runtime': runtime,
        'num_matched': len(matching)
    }

def parameter_sweep(config):
    """run full parameter sweep"""
    results = []
    
    n_values = config['n_values']
    alpha_values = config['alpha_values']
    d_values = config['d_values']
    trials = config['trials']
    seed = config['seed']
    
    total = len(n_values) * len(alpha_values) * len(d_values)
    count = 0
    
    for n in n_values:
        for alpha in alpha_values:
            m = int(n * (1 + alpha))
            for d in d_values:
                count += 1
                print(f"[{count}/{total}] n={n}, alpha={alpha:.3f}, d={d}, m={m}")
                
                # run trials
                trial_results = []
                for t in range(trials):
                    result = run_single_trial(m, n, d, seed + count * 1000 + t)
                    trial_results.append(result)
                
                # aggregate
                avg_ranks = [r['avg_rank'] for r in trial_results if not np.isnan(r['avg_rank'])]
                mean_rank = np.mean(avg_ranks) if avg_ranks else np.nan
                perfect_rate = np.mean([r['perfect'] for r in trial_results])
                mean_runtime = np.mean([r['runtime'] for r in trial_results])
                
                # theoretical bound
                lb = theoretical_lower_bound(d, n, alpha)
                gap = mean_rank - lb if not np.isnan(mean_rank) else np.nan
                ratio = mean_rank / lb if not np.isnan(mean_rank) and lb > 0 else np.nan
                
                results.append({
                    'n': n,
                    'm': m,
                    'alpha': alpha,
                    'd': d,
                    'avg_rank': mean_rank,
                    'lb': lb,
                    'gap': gap,
                    'ratio': ratio,
                    'perfect_rate': perfect_rate,
                    'runtime': mean_runtime
                })
    
    return results

def save_results(results, filename='../results/sweep_results.csv'):
    """save results to csv"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    fieldnames = ['n', 'm', 'alpha', 'd', 'avg_rank', 'lb', 'gap', 'ratio', 
                  'perfect_rate', 'runtime']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nsaved results to {filename}")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from plots import (plot_perfect_matching_threshold, plot_rank_vs_bound, 
                       plot_heatmaps)
    
    # configuration
    config = {
        'n_values': [80, 120, 160, 200, 240],
        'alpha_values': [0.05, 0.1, 0.25, 0.5, 0.75, 1.0],
        'd_values': [10, 20, 30],
        'trials': 50,
        'seed': 0
    }
    
    print("starting parameter sweep...")
    results = parameter_sweep(config)
    
    print("\ngenerating plots...")
    plot_perfect_matching_threshold(results)
    plot_rank_vs_bound(results)
    plot_heatmaps(results)
    
    print("\nsweep complete")

