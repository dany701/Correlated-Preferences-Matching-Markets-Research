import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def load_results(filename='../results/sweep_results.csv'):
    """load sweep results from csv"""
    return pd.read_csv(filename)

def plot_perfect_matching_threshold(df):
    """plot perfect matching rate vs d/d0 (normalized threshold)"""
    plt.figure(figsize=(12, 5))
    
    # pick a few (n, alpha) combinations to show
    selected = [
        (500, 1.5),
        (500, 7),
        (1000, 12),
    ]
    
    for idx, (n_val, alpha_val) in enumerate(selected):
        plt.subplot(1, 3, idx + 1)
        
        subset = df[(df['n'] == n_val) & (df['alpha'] == alpha_val)].copy()
        if subset.empty:
            continue
        
        # compute normalized d
        subset['d_normalized'] = subset['d'] / subset['d0']
        subset = subset.sort_values('d_normalized')
        
        plt.plot(subset['d_normalized'], subset['perfect_rate'], 'o-', linewidth=2)
        plt.axvline(1.0, color='red', linestyle='--', alpha=0.5, label='d=d0')
        plt.xlabel('d / d0')
        plt.ylabel('perfect matching rate')
        plt.title(f'n={n_val}, α={alpha_val}')
        plt.grid(alpha=0.3)
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('../results/perfect_matching_threshold.png', dpi=150)
    print('saved perfect_matching_threshold.png')

def plot_rank_vs_competition(df):
    """plot avg rank vs alpha, compare to theoretical bound"""
    # fix n and d-policy
    n_val = df['n'].unique()[0] if len(df['n'].unique()) > 0 else 500
    d_policy = 'logsq_c1.0'
    
    subset = df[(df['n'] == n_val) & (df['d_policy_name'] == d_policy)].copy()
    subset = subset.sort_values('alpha')
    
    if subset.empty:
        print(f'no data for n={n_val}, d_policy={d_policy}')
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # left: rank vs alpha
    axes[0].plot(subset['alpha'], subset['avg_proposer_rank'], 'o-', label='empirical avg rank', linewidth=2)
    axes[0].plot(subset['alpha'], subset['lb_rank'], 'x--', label='theoretical lower bound', linewidth=2)
    axes[0].set_xlabel('imbalance α (m/n - 1)')
    axes[0].set_ylabel('avg proposer rank')
    axes[0].set_title(f'rank vs competition (n={n_val}, {d_policy})')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    # add regime shading
    axes[0].axvspan(1, 2, alpha=0.1, color='green', label='small')
    axes[0].axvspan(4, 7, alpha=0.1, color='yellow', label='medium')
    axes[0].axvspan(11, 19, alpha=0.1, color='red', label='large')
    
    # right: ratio vs alpha
    axes[1].plot(subset['alpha'], subset['ratio'], 'o-', linewidth=2, color='purple')
    axes[1].axhline(1.0, color='red', linestyle='--', label='ratio=1 (at bound)', alpha=0.5)
    axes[1].set_xlabel('imbalance α (m/n - 1)')
    axes[1].set_ylabel('approximation ratio (avg_rank / lb)')
    axes[1].set_title(f'ratio to lower bound (n={n_val}, {d_policy})')
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    
    # add regime shading
    axes[1].axvspan(1, 2, alpha=0.1, color='green')
    axes[1].axvspan(4, 7, alpha=0.1, color='yellow')
    axes[1].axvspan(11, 19, alpha=0.1, color='red')
    
    plt.tight_layout()
    plt.savefig('../results/rank_vs_competition.png', dpi=150)
    print('saved rank_vs_competition.png')

def plot_heatmaps(df):
    """heatmaps for perfect_rate and ratio across (n, alpha)"""
    # fix d-policy
    d_policy = 'logsq_c1.0'
    subset = df[df['d_policy_name'] == d_policy].copy()
    
    if subset.empty:
        print(f'no data for d_policy={d_policy}')
        return
    
    n_vals = sorted(subset['n'].unique())
    alpha_vals = sorted(subset['alpha'].unique())
    
    # create grids
    perfect_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
    ratio_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
    
    for i, alpha in enumerate(alpha_vals):
        for j, n in enumerate(n_vals):
            row = subset[(subset['n'] == n) & (subset['alpha'] == alpha)]
            if not row.empty:
                perfect_grid[i, j] = row['perfect_rate'].values[0]
                ratio_grid[i, j] = row['ratio'].values[0]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # perfect matching rate heatmap
    im1 = axes[0].imshow(perfect_grid, aspect='auto', cmap='RdYlGn', vmin=0, vmax=1, origin='lower')
    axes[0].set_xticks(range(len(n_vals)))
    axes[0].set_xticklabels(n_vals)
    axes[0].set_yticks(range(len(alpha_vals)))
    axes[0].set_yticklabels([f'{a:.1f}' for a in alpha_vals])
    axes[0].set_xlabel('n (receivers)')
    axes[0].set_ylabel('α (imbalance)')
    axes[0].set_title(f'perfect matching rate ({d_policy})')
    plt.colorbar(im1, ax=axes[0])
    
    # ratio heatmap
    im2 = axes[1].imshow(ratio_grid, aspect='auto', cmap='viridis', origin='lower')
    axes[1].set_xticks(range(len(n_vals)))
    axes[1].set_xticklabels(n_vals)
    axes[1].set_yticks(range(len(alpha_vals)))
    axes[1].set_yticklabels([f'{a:.1f}' for a in alpha_vals])
    axes[1].set_xlabel('n (receivers)')
    axes[1].set_ylabel('α (imbalance)')
    axes[1].set_title(f'ratio to lower bound ({d_policy})')
    plt.colorbar(im2, ax=axes[1])
    
    plt.tight_layout()
    plt.savefig('../results/heatmaps.png', dpi=150)
    print('saved heatmaps.png')

def plot_d_policy_comparison(df):
    """compare different d-policies for fixed n and alpha"""
    n_val = 1000
    alpha_val = 7
    
    subset = df[(df['n'] == n_val) & (df['alpha'] == alpha_val)].copy()
    
    if subset.empty:
        print(f'no data for n={n_val}, alpha={alpha_val}')
        return
    
    subset = subset.sort_values('d')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # perfect rate vs d
    for policy in subset['d_policy_name'].unique():
        policy_data = subset[subset['d_policy_name'] == policy]
        axes[0].plot(policy_data['d'], policy_data['perfect_rate'], 'o-', label=policy)
    axes[0].set_xlabel('d (list length)')
    axes[0].set_ylabel('perfect matching rate')
    axes[0].set_title(f'd-policy comparison (n={n_val}, α={alpha_val})')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    # ratio vs d
    for policy in subset['d_policy_name'].unique():
        policy_data = subset[subset['d_policy_name'] == policy]
        axes[1].plot(policy_data['d'], policy_data['ratio'], 'o-', label=policy)
    axes[1].set_xlabel('d (list length)')
    axes[1].set_ylabel('ratio to lower bound')
    axes[1].set_title(f'd-policy comparison (n={n_val}, α={alpha_val})')
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('../results/d_policy_comparison.png', dpi=150)
    print('saved d_policy_comparison.png')

if __name__ == "__main__":
    print('loading results from csv...')
    df = load_results()
    
    print(f'loaded {len(df)} rows')
    print(f'n values: {sorted(df["n"].unique())}')
    print(f'alpha values: {sorted(df["alpha"].unique())}')
    print(f'd policies: {sorted(df["d_policy_name"].unique())}')
    print()
    
    print('generating plots...')
    plot_perfect_matching_threshold(df)
    plot_rank_vs_competition(df)
    plot_heatmaps(df)
    plot_d_policy_comparison(df)
    
    print('\nall plots generated')
