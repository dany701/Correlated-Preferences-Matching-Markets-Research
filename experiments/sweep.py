import os
import sys
import time
import csv
import numpy as np
from collections import defaultdict
from math import log, ceil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from gale_shapley import DeferredAcceptanceMarket

def compute_d0(n, alpha):
    """threshold quantity for perfect matching (theorem 2)"""
    if alpha <= 0 or n <= 0:
        return float('inf')
    term = (1 + alpha) / (alpha + 1 / (n * (1 + alpha)))
    if term <= 1:
        return float('inf')
    return log(n) * log(term)

def compute_lb_rank(n, alpha, d):
    """theoretical lower bound on expected proposer rank (theorem 3)"""
    if alpha <= 0 or n <= 0 or d <= 0:
        return float('inf')
    term = (1 + alpha) / (alpha + 1 / (n * (1 + alpha)))
    if term <= 1:
        return float('inf')
    log_term = log(term)
    if log_term <= 0:
        return float('inf')
    return d / log_term

def d_policy_log(n, c):
    """d = ceil(c * ln(n))"""
    return max(1, min(n, ceil(c * log(n))))

def d_policy_logsq(n, c):
    """d = ceil(c * (ln(n))^2)"""
    return max(1, min(n, ceil(c * log(n)**2)))

def get_d_policies():
    """return list of (policy_name, policy_func) tuples"""
    policies = []
    for c in [2, 4, 6]:
        policies.append((f'log_c{c}', lambda n, c=c: d_policy_log(n, c)))
    for c in [0.5, 1.0, 1.5]:
        policies.append((f'logsq_c{c}', lambda n, c=c: d_policy_logsq(n, c)))
    return policies

def run_single_trial(m, n, d, seed):
    """run one market trial, return metrics"""
    start = time.perf_counter()
    market = DeferredAcceptanceMarket(m, n, d, seed)
    matching = market.run()
    runtime = time.perf_counter() - start
    
    matched_receivers = len(set(matching.values()))
    perfect_flag = (matched_receivers == n)
    
    ranks = []
    for p_id, r_id in matching.items():
        proposer = market.proposers[p_id]
        rank = proposer.proposals_order.index(r_id) + 1
        ranks.append(rank)
    
    return {
        'matched_receivers': matched_receivers,
        'perfect_flag': perfect_flag,
        'ranks': ranks,
        'runtime': runtime,
        'matched_proposers': len(matching)
    }

def run_experiments(n, alpha, d, d_policy_name, base_seed, initial_trials=30):
    """run adaptive trials for (n, alpha, d)"""
    m = round(n * (1 + alpha))
    
    # initial trials
    results = []
    for t in range(initial_trials):
        seed = base_seed + t
        res = run_single_trial(m, n, d, seed)
        results.append(res)
    
    # check if we're in phase transition region
    perfect_rate = np.mean([r['perfect_flag'] for r in results])
    
    # adaptive: add more trials if near threshold
    if 0.2 <= perfect_rate <= 0.8:
        additional = 70  # bring total to 100
        for t in range(additional):
            seed = base_seed + initial_trials + t
            res = run_single_trial(m, n, d, seed)
            results.append(res)
    
    # aggregate
    all_ranks = [r for res in results for r in res['ranks']]
    
    return {
        'trials': len(results),
        'perfect_rate': np.mean([r['perfect_flag'] for r in results]),
        'matched_proposer_fraction': np.mean([r['matched_proposers'] / m for r in results]),
        'avg_proposer_rank': np.mean(all_ranks) if all_ranks else float('nan'),
        'std_proposer_rank': np.std(all_ranks) if all_ranks else float('nan'),
        'runtime_mean': np.mean([r['runtime'] for r in results])
    }

def parameter_sweep(config):
    """run full sweep with functional d-policies"""
    results = []
    
    n_values = config['n_values']
    alpha_values = config['alpha_values']
    d_policies = get_d_policies()
    master_seed = config['seed']
    
    master_rng = np.random.default_rng(master_seed)
    
    total = len(n_values) * len(alpha_values) * len(d_policies)
    current = 0
    
    for n in n_values:
        for alpha in alpha_values:
            m = round(n * (1 + alpha))
            
            for d_policy_name, d_policy_func in d_policies:
                current += 1
                d = d_policy_func(n)
                
                print(f'[{current}/{total}] n={n}, alpha={alpha:.2f}, d={d} ({d_policy_name}), m={m}')
                
                # unique seed per configuration
                base_seed = master_rng.integers(0, 2**32 - 1)
                
                metrics = run_experiments(n, alpha, d, d_policy_name, base_seed)
                
                # compute theoretical quantities
                d0_val = compute_d0(n, alpha)
                lb_rank = compute_lb_rank(n, alpha, d)
                
                gap = metrics['avg_proposer_rank'] - lb_rank
                ratio = metrics['avg_proposer_rank'] / lb_rank if lb_rank != 0 else float('inf')
                
                results.append({
                    'n': n,
                    'm': m,
                    'alpha': alpha,
                    'd': d,
                    'd0': d0_val,
                    'd_policy_name': d_policy_name,
                    'trials': metrics['trials'],
                    'perfect_rate': metrics['perfect_rate'],
                    'matched_proposer_fraction': metrics['matched_proposer_fraction'],
                    'avg_proposer_rank': metrics['avg_proposer_rank'],
                    'std_proposer_rank': metrics['std_proposer_rank'],
                    'lb_rank': lb_rank,
                    'gap': gap,
                    'ratio': ratio,
                    'runtime_mean': metrics['runtime_mean']
                })
                
                print(f"  perfect_rate={metrics['perfect_rate']:.2f}, avg_rank={metrics['avg_proposer_rank']:.2f}, trials={metrics['trials']}")
    
    return results

def save_results_csv(results, filename='../results/sweep_results.csv'):
    """save results to csv"""
    if not results:
        return
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'n', 'm', 'alpha', 'd', 'd0', 'd_policy_name', 'trials',
            'perfect_rate', 'matched_proposer_fraction',
            'avg_proposer_rank', 'std_proposer_rank',
            'lb_rank', 'gap', 'ratio', 'runtime_mean'
        ])
        writer.writeheader()
        writer.writerows(results)
    
    print(f'\nsaved results to {filename}')

if __name__ == "__main__":
    # imbalanced market regimes (alpha > 1 required)
    config = {
        'n_values': [500, 1000, 2000],
        'alpha_values': [1.5, 2, 5, 7, 12, 19],  # small [1-2], medium [4-7], large [11-19]
        'seed': 0
    }
    
    print('starting parameter sweep with functional d-policies...')
    print(f'n_values: {config["n_values"]}')
    print(f'alpha_values: {config["alpha_values"]}')
    print(f'd_policies: log (c=2,4,6), logsq (c=0.5,1.0,1.5)')
    print()
    
    results = parameter_sweep(config)
    
    save_results_csv(results)
    
    print('\nsweep complete - run plots.py to generate visualizations')
