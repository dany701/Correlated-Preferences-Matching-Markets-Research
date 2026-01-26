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
    """return list of (policy_name, policy_func) tuples - 3 well-separated policies"""
    from math import ceil, log, sqrt
    policies = []
    # Wide range: logarithmic, sublinear (sqrt), linear
    policies.append(('d=ln(n)', lambda n: ceil(log(n))))
    policies.append(('d=√n', lambda n: ceil(sqrt(n))))
    policies.append(('d=n/2', lambda n: ceil(n / 2)))
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
        rank = proposer.get_rank(r_id)
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
    import time
    m = round(n * (1 + alpha))
    
    start_time = time.time()
    
    # initial trials
    results = []
    print(f'    → Running {initial_trials} initial trials...', end='', flush=True)
    for t in range(initial_trials):
        if t > 0 and t % 10 == 0:
            elapsed = time.time() - start_time
            rate = t / elapsed
            print(f' [{t}/{initial_trials}, {rate:.1f} tr/s]', end='', flush=True)
        seed = base_seed + t
        res = run_single_trial(m, n, d, seed)
        results.append(res)
    elapsed = time.time() - start_time
    print(f' ✓ {elapsed:.2f}s', flush=True)
    
    # check if we're in phase transition region
    perfect_rate = np.mean([r['perfect_flag'] for r in results])
    avg_time_per_trial = elapsed / initial_trials
    print(f'    → Perfect rate: {perfect_rate:.3f} | Avg time/trial: {avg_time_per_trial*1000:.1f}ms', flush=True)
    
    # adaptive: add more trials if near threshold
    if 0.2 <= perfect_rate <= 0.8:
        additional = 70  # bring total to 100
        print(f'    → Phase transition! Running {additional} more trials...', end='', flush=True)
        for t in range(additional):
            if t > 0 and t % 20 == 0:
                elapsed = time.time() - start_time
                total_done = initial_trials + t
                rate = total_done / elapsed
                print(f' [{t}/{additional}, {rate:.1f} tr/s]', end='', flush=True)
            seed = base_seed + initial_trials + t
            res = run_single_trial(m, n, d, seed)
            results.append(res)
        elapsed = time.time() - start_time
        print(f' ✓ {elapsed:.2f}s total', flush=True)
    
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
    import time
    results = []
    
    n_values = config['n_values']
    alpha_values = config['alpha_values']
    d_policies = get_d_policies()
    master_seed = config['seed']
    
    master_rng = np.random.default_rng(master_seed)
    
    total = len(n_values) * len(alpha_values) * len(d_policies)
    current = 0
    sweep_start = time.time()
    
    for n in n_values:
        for alpha in alpha_values:
            m = round(n * (1 + alpha))
            
            for d_policy_name, d_policy_func in d_policies:
                current += 1
                d = d_policy_func(n)
                
                config_start = time.time()
                print(f'\n[{current}/{total}] n={n}, α={alpha:.1f}, d={d} ({d_policy_name}), m={m}')
                
                # unique seed per configuration
                base_seed = master_rng.integers(0, 2**32 - 1)
                
                metrics = run_experiments(n, alpha, d, d_policy_name, base_seed)
                
                config_time = time.time() - config_start
                elapsed_total = time.time() - sweep_start
                avg_time_per_config = elapsed_total / current
                eta_seconds = avg_time_per_config * (total - current)
                
                print(f'    → Config completed in {config_time:.2f}s | '
                      f'Total elapsed: {elapsed_total/60:.1f}min | '
                      f'ETA: {eta_seconds/60:.1f}min')
                
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
    
    # Final summary
    total_time = time.time() - sweep_start
    print(f'\n{"="*70}')
    print(f'SWEEP COMPLETED')
    print(f'{"="*70}')
    print(f'Total configurations: {total}')
    print(f'Total time: {total_time/60:.2f} minutes ({total_time:.1f}s)')
    print(f'Average time per config: {total_time/total:.2f}s')
    print()
    print('Scaling Analysis (avg runtime per trial):')
    for n in n_values:
        n_results = [r for r in results if r['n'] == n]
        if n_results:
            avg_runtime = np.mean([r['runtime_mean'] for r in n_results])
            print(f'  n={n:5d}: {avg_runtime*1000:7.2f}ms')
    print()
    
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
    # imbalanced market regimes (alpha > 1 required for strong imbalance)
    # Small imbalance: alpha in [1-2] → m/n in [2-3]
    # Medium imbalance: alpha in [4-7] → m/n in [5-8]
    # Large imbalance: alpha in [11-19] → m/n in [12-20]
    
    # TEST CONFIGURATION (3×4×3 design, well-separated values)
    config = {
        'n_values': [100, 500, 1500, 5000],   # small, medium, large, very large markets
        'alpha_values': [2.0, 7.0, 15.0],     # one per regime, well-separated
        'seed': 42
    }
    
    print('='*60)
    print('STRONGLY IMBALANCED MATCHING MARKETS EXPERIMENT')
    print('='*60)
    print('*** TEST CONFIGURATION (4 n-values × 3 α × 3 d-policies) ***')
    print(f'n_values (receivers): {config["n_values"]}')
    print(f'alpha_values (imbalance): {config["alpha_values"]}')
    print(f'd_policies: d=ln(n), d=√n, d=n/2 [WIDE RANGE: log, sublinear, linear]')
    print(f'Total configurations: {len(config["n_values"]) * len(config["alpha_values"]) * 3} = 36')
    print()
    print('Design:')
    print('  n=100    (small market)')
    print('  n=500    (medium market)')
    print('  n=1500   (large market)')
    print('  n=5000   (very large market)')
    print()
    print('  α=2.0   (small imbalance, m/n=3)')
    print('  α=7.0   (medium imbalance, m/n=8)')
    print('  α=15.0  (large imbalance, m/n=16)')
    print('='*60)
    print()
    
    results = parameter_sweep(config)
    
    save_results_csv(results)
    
    print('\n' + '='*60)
    print('SWEEP COMPLETE')
    print('='*60)
    print(f'Total configurations tested: {len(results)}')
    print('Results saved to: results/sweep_results.csv')
    print()
    print('Next step: python plots.py to generate visualizations')
    print('='*60)
