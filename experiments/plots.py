import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def load_results(filename='../results/sweep_results.csv'):
    """load sweep results from csv"""
    results = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'n': int(row['n']),
                'm': int(row['m']),
                'alpha': float(row['alpha']),
                'd': int(row['d']),
                'avg_rank': float(row['avg_rank']),
                'lb': float(row['lb']),
                'gap': float(row['gap']),
                'ratio': float(row['ratio']),
                'perfect_rate': float(row['perfect_rate']),
                'runtime': float(row['runtime'])
            })
    return results

def plot_perfect_matching_threshold(results):
    """plot perfect matching rate vs d for fixed n, alpha"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # group by n and alpha
    grouped = defaultdict(lambda: defaultdict(list))
    for r in results:
        grouped[r['n']][r['alpha']].append((r['d'], r['perfect_rate']))
    
    for idx, n in enumerate(sorted(grouped.keys())[:2]):
        ax = axes[idx]
        for alpha in sorted(grouped[n].keys())[:3]:
            data = sorted(grouped[n][alpha])
            if data:
                d_vals, perfect_vals = zip(*data)
                ax.plot(d_vals, perfect_vals, 'o-', label=f'α={alpha:.2f}')
        
        ax.set_xlabel('d (list length)')
        ax.set_ylabel('perfect matching rate')
        ax.set_title(f'perfect matching threshold (n={n})')
        ax.legend()
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/perfect_matching_threshold.png', dpi=150)
    print("saved perfect_matching_threshold.png")

def plot_rank_vs_bound(results):
    """plot avg rank and lower bound vs alpha"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # group by n and d
    grouped = defaultdict(lambda: defaultdict(list))
    for r in results:
        grouped[r['n']][r['d']].append((r['alpha'], r['avg_rank'], r['lb'], r['ratio']))
    
    # plot for first n, d combination
    n = sorted(grouped.keys())[0]
    d = sorted(grouped[n].keys())[0]
    
    data = sorted(grouped[n][d])
    if data:
        alphas, ranks, lbs, ratios = zip(*data)
        
        # left: rank and bound
        ax1.plot(alphas, ranks, 'o-', label='empirical avg rank', linewidth=2)
        ax1.plot(alphas, lbs, 's--', label='theoretical lower bound', linewidth=2)
        ax1.set_xlabel('imbalance (α = m/n - 1)')
        ax1.set_ylabel('proposer rank')
        ax1.set_title(f'rank vs lower bound (n={n}, d={d})')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # right: ratio
        ax2.plot(alphas, ratios, 'o-', linewidth=2, color='green')
        ax2.axhline(1.0, color='red', linestyle='--', label='optimal (ratio=1)')
        ax2.set_xlabel('imbalance (α = m/n - 1)')
        ax2.set_ylabel('empirical / lower bound')
        ax2.set_title(f'approximation ratio (n={n}, d={d})')
        ax2.legend()
        ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/rank_vs_bound.png', dpi=150)
    print("saved rank_vs_bound.png")

def plot_heatmaps(results):
    """create heatmaps for different metrics"""
    # filter to specific d
    d_target = 30
    data = [r for r in results if r['d'] == d_target]
    
    if not data:
        print(f"no data for d={d_target}")
        return
    
    # create grid
    n_vals = sorted(set(r['n'] for r in data))
    alpha_vals = sorted(set(r['alpha'] for r in data))
    
    # initialize grids
    rank_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
    ratio_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
    perfect_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
    
    # fill grids
    for r in data:
        i = alpha_vals.index(r['alpha'])
        j = n_vals.index(r['n'])
        rank_grid[i, j] = r['avg_rank']
        ratio_grid[i, j] = r['ratio']
        perfect_grid[i, j] = r['perfect_rate']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # rank heatmap
    im1 = axes[0].imshow(rank_grid, aspect='auto', cmap='viridis')
    axes[0].set_xticks(range(len(n_vals)))
    axes[0].set_xticklabels(n_vals)
    axes[0].set_yticks(range(len(alpha_vals)))
    axes[0].set_yticklabels([f'{a:.2f}' for a in alpha_vals])
    axes[0].set_xlabel('n')
    axes[0].set_ylabel('α')
    axes[0].set_title(f'avg proposer rank (d={d_target})')
    plt.colorbar(im1, ax=axes[0])
    
    # ratio heatmap
    im2 = axes[1].imshow(ratio_grid, aspect='auto', cmap='RdYlGn_r', vmin=0.8, vmax=1.5)
    axes[1].set_xticks(range(len(n_vals)))
    axes[1].set_xticklabels(n_vals)
    axes[1].set_yticks(range(len(alpha_vals)))
    axes[1].set_yticklabels([f'{a:.2f}' for a in alpha_vals])
    axes[1].set_xlabel('n')
    axes[1].set_ylabel('α')
    axes[1].set_title(f'ratio to lower bound (d={d_target})')
    plt.colorbar(im2, ax=axes[1])
    
    # perfect rate heatmap
    im3 = axes[2].imshow(perfect_grid, aspect='auto', cmap='coolwarm', vmin=0, vmax=1)
    axes[2].set_xticks(range(len(n_vals)))
    axes[2].set_xticklabels(n_vals)
    axes[2].set_yticks(range(len(alpha_vals)))
    axes[2].set_yticklabels([f'{a:.2f}' for a in alpha_vals])
    axes[2].set_xlabel('n')
    axes[2].set_ylabel('α')
    axes[2].set_title(f'perfect matching rate (d={d_target})')
    plt.colorbar(im3, ax=axes[2])
    
    plt.tight_layout()
    plt.savefig('../results/heatmaps.png', dpi=150)
    print("saved heatmaps.png")

if __name__ == "__main__":
    print("loading results...")
    results = load_results()
    
    print("generating plots...")
    plot_perfect_matching_threshold(results)
    plot_rank_vs_bound(results)
    plot_heatmaps(results)
    
    print("all plots generated")

