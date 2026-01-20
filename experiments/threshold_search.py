"""
Threshold Search Experiment: Find minimal d* for perfect matching.

Goal: For each (n, α) pair, find the smallest d such that 
      Pr(perfect matching) ≥ 0.8 using binary search.
"""

import os
import sys
import time
import csv
import numpy as np
from math import log, ceil, floor, sqrt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from gale_shapley import DeferredAcceptanceMarket

# ============================================================================
# PARAMETERS
# ============================================================================

N_VALUES = [500, 1000, 2000, 5000]
ALPHA_REGIMES = {
    'Small': 1.5,
    'Medium': 7.0,
    'Large': 15.0
}
P0_TARGET = 0.8  # Probability threshold for "success" (configurable)
MASTER_SEED = 42
TIMEOUT_PER_TRIAL = 30  # seconds
FINAL_CONFIRMATION_TRIALS = 100  # Final confirmation trials (increased from 50)

# ============================================================================
# CORE SUBROUTINE: PERFECT MATCHING TEST
# ============================================================================

def estimate_perfect_rate(n, alpha, d, trials, seed, verbose=False):
    """
    Estimate probability of perfect matching for given (n, alpha, d).
    
    Returns:
        (perfect_rate, trials_used, early_stop, timeouts)
    """
    m = round(n * (1 + alpha))
    rng = np.random.default_rng(seed)
    
    successes = 0
    trials_used = 0
    timeouts = 0  # Track timeout occurrences
    start_time = time.time()
    last_print = start_time
    
    for t in range(trials):
        trial_seed = rng.integers(0, 2**31)
        
        # Run DA with timeout protection
        trial_start = time.time()
        try:
            market = DeferredAcceptanceMarket(m, n, d, trial_seed)
            matching = market.run()
            matched_receivers = len(set(matching.values()))
            
            if matched_receivers == n:
                successes += 1
            
            trials_used = t + 1
            
            # Progress printing (every ~10% or 5 seconds)
            if verbose and (t % max(1, trials // 10) == 0 or time.time() - last_print > 5):
                elapsed = time.time() - start_time
                rate = trials_used / elapsed if elapsed > 0 else 0
                print(f"      trials: {100*trials_used/trials:.0f}% complete | "
                      f"{trials_used}/{trials} | {elapsed:.1f}s | {rate:.2f} trials/sec")
                last_print = time.time()
            
            # Timeout check
            if time.time() - trial_start > TIMEOUT_PER_TRIAL:
                print(f"      TIMEOUT: trial {t} exceeded {TIMEOUT_PER_TRIAL}s")
                timeouts += 1
                break
                
        except Exception as e:
            print(f"      ERROR in trial {t}: {e}")
            continue
        
        # Early stopping logic
        if trials_used >= 10:
            current_rate = successes / trials_used
            
            # Clearly above threshold
            if current_rate > 0.9 and successes >= 9:
                if verbose:
                    print(f"      early stop: clearly above threshold ({current_rate:.2f})")
                return current_rate, trials_used, True, timeouts
            
            # Clearly below threshold
            if current_rate < 0.3 and trials_used >= 10:
                if verbose:
                    print(f"      early stop: clearly below threshold ({current_rate:.2f})")
                return current_rate, trials_used, True, timeouts
    
    perfect_rate = successes / trials_used if trials_used > 0 else 0.0
    return perfect_rate, trials_used, False, timeouts

# ============================================================================
# BRACKETING: FIND INITIAL [d_low, d_high]
# ============================================================================

def find_brackets(n, alpha, seed, verbose=False):
    """
    Quickly find [d_low, d_high] bracket around threshold.
    """
    if verbose:
        print(f"    [bracketing] finding initial bounds...")
    
    # Test candidate d values in increasing order
    candidates = [
        max(1, ceil(log(n))),
        max(1, ceil(log(n)**2)),
        max(1, ceil(sqrt(n))),
        max(1, ceil(n / 2)),
        n
    ]
    
    # Remove duplicates and sort
    candidates = sorted(set(candidates))
    
    d_low = 1
    d_high = n
    
    for i, d in enumerate(candidates):
        if verbose:
            print(f"    [bracketing] testing d={d} ({i+1}/{len(candidates)})")
        
        rate, trials, early, _ = estimate_perfect_rate(n, alpha, d, trials=10, 
                                                       seed=seed+d, verbose=False)
        
        if verbose:
            print(f"      → rate={rate:.2f}")
        
        if rate >= P0_TARGET:
            d_high = d
            if i > 0:
                d_low = candidates[i-1]
            if verbose:
                print(f"    [bracketing] found bounds: [{d_low}, {d_high}]")
            return d_low, d_high
    
    # If we get here, even n didn't work
    if verbose:
        print(f"    [bracketing] WARNING: d=n insufficient! Using [{n//2}, {n}]")
    return n // 2, n

# ============================================================================
# BINARY SEARCH FOR d*
# ============================================================================

def binary_search_threshold(n, alpha, d_low, d_high, seed, verbose=False):
    """
    Binary search for minimal d such that Pr(perfect) ≥ P0_TARGET.
    
    Returns:
        (d_star, final_rate, total_trials)
    """
    if verbose:
        print(f"    [d-search] binary search in [{d_low}, {d_high}]")
    
    total_trials = 0
    total_timeouts = 0
    step = 0
    
    while d_low < d_high:
        step += 1
        mid = (d_low + d_high) // 2
        
        max_steps = ceil(log(d_high - d_low + 1, 2)) + 1
        if verbose:
            print(f"    [d-search] step {step}/{max_steps} | testing d={mid}")
        
        # Start with 10 trials, increase if ambiguous
        rate, trials, early, timeouts = estimate_perfect_rate(n, alpha, mid, trials=10,
                                                               seed=seed+mid*1000, verbose=verbose)
        total_trials += trials
        total_timeouts += timeouts
        
        # If ambiguous (near threshold), run more trials
        if not early and 0.4 <= rate <= 0.95:
            if verbose:
                print(f"      ambiguous result, running 30 more trials...")
            rate2, trials2, _, timeouts2 = estimate_perfect_rate(n, alpha, mid, trials=30,
                                                                  seed=seed+mid*1000+1000, verbose=verbose)
            rate = (rate * trials + rate2 * trials2) / (trials + trials2)
            total_trials += trials2
            total_timeouts += timeouts2
        
        if verbose:
            print(f"      final rate={rate:.3f} (target={P0_TARGET})")
        
        if rate >= P0_TARGET:
            d_high = mid
        else:
            d_low = mid + 1
    
    d_star = d_low
    
    # Final confirmation with 100 trials (as per spec)
    if verbose:
        print(f"    [d-search] confirming d*={d_star} with {FINAL_CONFIRMATION_TRIALS} trials...")
    final_rate, trials, _, timeouts = estimate_perfect_rate(
        n, alpha, d_star, trials=FINAL_CONFIRMATION_TRIALS,
        seed=seed+d_star*10000, verbose=verbose
    )
    total_trials += trials
    total_timeouts += timeouts
    
    return d_star, final_rate, total_trials, total_timeouts

# ============================================================================
# MAIN EXPERIMENT LOOP
# ============================================================================

def run_threshold_experiment():
    """
    Main experiment: Find d* for each (n, α) combination.
    """
    results = []
    master_rng = np.random.default_rng(MASTER_SEED)
    
    alpha_items = list(ALPHA_REGIMES.items())
    
    print('='*70)
    print('THRESHOLD SEARCH EXPERIMENT: Finding Minimal d* for Perfect Matching')
    print('='*70)
    print(f'Target probability: {P0_TARGET}')
    print(f'Market sizes: {N_VALUES}')
    print(f'Regimes: {list(ALPHA_REGIMES.keys())}')
    print('='*70)
    print()
    
    for regime_idx, (regime_name, alpha) in enumerate(alpha_items):
        print(f'\n[ALPHA {alpha:.1f} | REGIME: {regime_name.upper()}] ({regime_idx+1}/{len(alpha_items)})')
        print('-'*70)
        
        d_prev = None  # For warm start
        
        for n_idx, n in enumerate(N_VALUES):
            m = round(n * (1 + alpha))
            
            print(f'  n = {n} ({n_idx+1}/{len(N_VALUES)}) | m = {m}')
            
            seed = master_rng.integers(0, 2**31)
            
            # Warm start: use previous d* if available
            if d_prev is not None:
                d_low = max(1, floor(0.7 * d_prev))
                d_high = min(n, ceil(1.5 * d_prev))
                print(f"    [warm start] using bounds [{d_low}, {d_high}] from d*={d_prev}")
            else:
                # Find initial brackets
                d_low, d_high = find_brackets(n, alpha, seed, verbose=True)
            
            # Binary search for d*
            start_time = time.time()
            d_star, final_rate, total_trials, total_timeouts = binary_search_threshold(
                n, alpha, d_low, d_high, seed, verbose=True
            )
            elapsed = time.time() - start_time
            
            timeout_msg = f' | timeouts={total_timeouts}' if total_timeouts > 0 else ''
            print(f'  ✓ RESULT: d* = {d_star} | rate = {final_rate:.3f} | '
                  f'trials = {total_trials} | time = {elapsed:.1f}s{timeout_msg}')
            print()
            
            # Store result (matches spec: n, alpha, m, d_star, p0, trials_used)
            results.append({
                'regime': regime_name,
                'alpha': alpha,
                'n': n,
                'm': m,
                'd_star': d_star,
                'p0_target': P0_TARGET,  # Target probability threshold
                'perfect_rate': final_rate,  # Achieved rate
                'trials_used': total_trials,  # Total trials used
                'timeouts': total_timeouts,  # Timeout occurrences
                'time_seconds': elapsed
            })
            
            # Save after each (n, α) pair
            save_results(results)
            
            # Update for warm start
            d_prev = d_star
    
    print('='*70)
    print('EXPERIMENT COMPLETE')
    print('='*70)
    print(f'Total configurations tested: {len(results)}')
    print('Results saved to: results/threshold_results.csv')
    
    return results

# ============================================================================
# OUTPUT
# ============================================================================

def save_results(results, filename='../results/threshold_results.csv'):
    """Save results to CSV after each configuration."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'regime', 'alpha', 'n', 'm', 'd_star', 'p0_target',
            'perfect_rate', 'trials_used', 'timeouts', 'time_seconds'
        ])
        writer.writeheader()
        writer.writerows(results)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = run_threshold_experiment()
    print('\n✓ Run plot_threshold.py to visualize results')

