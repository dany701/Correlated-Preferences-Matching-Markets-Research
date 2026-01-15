import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def load_results(filename='../results/sweep_results.csv'):
    """load sweep results from csv"""
    return pd.read_csv(filename)

def plot_baseline_average_rank(df):
    """baseline: histogram of rank distribution across all markets"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    d_policies = sorted(df['d_policy_name'].unique())
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    # Determine global max for consistent x-axis
    global_max_rank = df['avg_proposer_rank'].max()
    bins = np.linspace(0, global_max_rank + 5, 30)
    
    for idx, (d_policy, color) in enumerate(zip(d_policies, colors)):
        subset = df[df['d_policy_name'] == d_policy]
        
        # Get all average ranks for this policy
        ranks = subset['avg_proposer_rank'].values
        
        axes[idx].hist(ranks, bins=bins, alpha=0.7, color=color, edgecolor='black', linewidth=1.2)
        
        # Add vertical line for mean
        mean_rank = ranks.mean()
        axes[idx].axvline(mean_rank, color='red', linestyle='--', linewidth=2.5, 
                         label=f'Mean = {mean_rank:.2f}')
        
        # Add statistics text box
        stats_text = f'Mean: {mean_rank:.2f}\nStd: {ranks.std():.2f}\nN: {len(ranks)}'
        axes[idx].text(0.98, 0.97, stats_text, transform=axes[idx].transAxes,
                      verticalalignment='top', horizontalalignment='right',
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                      fontsize=10)
        
        axes[idx].set_xlabel('Average Proposer Rank', fontsize=11)
        axes[idx].set_ylabel('Frequency', fontsize=11)
        axes[idx].set_title(f'{d_policy}', fontsize=12, fontweight='bold')
        axes[idx].grid(axis='y', alpha=0.3)
        axes[idx].legend(fontsize=10)
        axes[idx].set_xlim([0, global_max_rank + 5])
    
    plt.suptitle('Baseline: Distribution of Average Ranks Across All Markets', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('../results/baseline_rank_distribution.png', dpi=150, bbox_inches='tight')
    print('saved baseline_rank_distribution.png')

def plot_rank_vs_lower_bound(df):
    """plot empirical rank vs theoretical lower bound"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    d_policies = sorted(df['d_policy_name'].unique())
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    for idx, (d_policy, color) in enumerate(zip(d_policies, colors)):
        subset = df[df['d_policy_name'] == d_policy].copy()
        subset = subset.sort_values(['n', 'alpha'])
        
        # Create x-axis labels combining n and alpha
        subset['label'] = subset.apply(lambda row: f"n={row['n']}\nα={row['alpha']:.0f}", axis=1)
        
        x_pos = np.arange(len(subset))
        width = 0.35
        
        axes[idx].bar(x_pos - width/2, subset['avg_proposer_rank'], width,
                     label='Empirical Rank', alpha=0.8, color=color)
        axes[idx].bar(x_pos + width/2, subset['lb_rank'], width,
                     label='Lower Bound', alpha=0.6, color='gray')
        
        axes[idx].set_xticks(x_pos)
        axes[idx].set_xticklabels(subset['label'], fontsize=8)
        axes[idx].set_xlabel('Market Configuration', fontsize=10)
        axes[idx].set_ylabel('Rank', fontsize=10)
        axes[idx].set_title(f'{d_policy}', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=9)
        axes[idx].grid(axis='y', alpha=0.3)
    
    plt.suptitle('Empirical Rank vs Theoretical Lower Bound', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('../results/rank_vs_lower_bound.png', dpi=150, bbox_inches='tight')
    print('saved rank_vs_lower_bound.png')

def plot_approximation_ratio_heatmap(df):
    """heatmap of approximation ratio across n and alpha"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    d_policies = sorted(df['d_policy_name'].unique())
    
    n_vals = sorted(df['n'].unique())
    alpha_vals = sorted(df['alpha'].unique())
    
    for idx, d_policy in enumerate(d_policies):
        subset = df[df['d_policy_name'] == d_policy]
        
        # Create grid
        ratio_grid = np.full((len(alpha_vals), len(n_vals)), np.nan)
        
        for i, alpha in enumerate(alpha_vals):
            for j, n in enumerate(n_vals):
                row = subset[(subset['n'] == n) & (subset['alpha'] == alpha)]
                if not row.empty:
                    ratio_grid[i, j] = row['ratio'].values[0]
        
        im = axes[idx].imshow(ratio_grid, aspect='auto', cmap='YlOrRd', 
                             origin='lower', vmin=0, vmax=0.25)
        
        axes[idx].set_xticks(range(len(n_vals)))
        axes[idx].set_xticklabels(n_vals)
        axes[idx].set_yticks(range(len(alpha_vals)))
        axes[idx].set_yticklabels([f'{a:.1f}' for a in alpha_vals])
        axes[idx].set_xlabel('n (receivers)', fontsize=10)
        axes[idx].set_ylabel('α (imbalance)', fontsize=10)
        axes[idx].set_title(f'{d_policy}', fontsize=12, fontweight='bold')
        
        # Add text annotations
        for i in range(len(alpha_vals)):
            for j in range(len(n_vals)):
                if not np.isnan(ratio_grid[i, j]):
                    text = axes[idx].text(j, i, f'{ratio_grid[i, j]:.2f}',
                                        ha="center", va="center", 
                                        color="black", fontsize=9)
        
        plt.colorbar(im, ax=axes[idx], label='Approximation Ratio')
    
    plt.suptitle('Approximation Ratio (Empirical / Lower Bound)', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('../results/approximation_ratio_heatmap.png', dpi=150, bbox_inches='tight')
    print('saved approximation_ratio_heatmap.png')

def plot_rank_by_imbalance(df):
    """plot average rank vs imbalance (alpha) for each n"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    n_vals = sorted(df['n'].unique())
    d_policies = sorted(df['d_policy_name'].unique())
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    markers = ['o', 's', '^']
    
    for idx, n_val in enumerate(n_vals):
        subset = df[df['n'] == n_val]
        
        for d_policy, color, marker in zip(d_policies, colors, markers):
            policy_data = subset[subset['d_policy_name'] == d_policy].sort_values('alpha')
            
            axes[idx].plot(policy_data['alpha'], policy_data['avg_proposer_rank'],
                         marker=marker, linewidth=2, markersize=8,
                         label=d_policy, color=color, alpha=0.8)
        
        axes[idx].set_xlabel('Imbalance α (m/n - 1)', fontsize=10)
        axes[idx].set_ylabel('Average Proposer Rank', fontsize=10)
        axes[idx].set_title(f'n = {n_val}', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=9)
        axes[idx].grid(alpha=0.3)
        
        # Add regime shading
        axes[idx].axvspan(0, 3, alpha=0.05, color='green', label='small' if idx == 0 else '')
        axes[idx].axvspan(4, 8, alpha=0.05, color='yellow', label='medium' if idx == 0 else '')
        axes[idx].axvspan(11, 20, alpha=0.05, color='red', label='large' if idx == 0 else '')
    
    plt.suptitle('Proposer Rank vs Competition (α)', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('../results/rank_by_imbalance.png', dpi=150, bbox_inches='tight')
    print('saved rank_by_imbalance.png')

def plot_perfect_matching_summary(df):
    """summary of perfect matching rates"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Perfect rate by d-policy
    policy_perfect = df.groupby('d_policy_name')['perfect_rate'].mean().sort_index()
    
    axes[0].bar(range(len(policy_perfect)), policy_perfect.values,
               color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.7)
    axes[0].set_xticks(range(len(policy_perfect)))
    axes[0].set_xticklabels(policy_perfect.index, rotation=0)
    axes[0].set_ylabel('Perfect Matching Rate', fontsize=10)
    axes[0].set_xlabel('d-Policy', fontsize=10)
    axes[0].set_title('Perfect Matching Rate by Policy', fontsize=12, fontweight='bold')
    axes[0].set_ylim([0, 1.05])
    axes[0].grid(axis='y', alpha=0.3)
    
    # Add percentage labels
    for i, v in enumerate(policy_perfect.values):
        axes[0].text(i, v + 0.02, f'{v*100:.0f}%', ha='center', fontweight='bold')
    
    # Right: Perfect rate heatmap (n vs alpha), averaged over d-policies
    n_vals = sorted(df['n'].unique())
    alpha_vals = sorted(df['alpha'].unique())
    
    perfect_grid = np.zeros((len(alpha_vals), len(n_vals)))
    
    for i, alpha in enumerate(alpha_vals):
        for j, n in enumerate(n_vals):
            perfect_grid[i, j] = df[(df['n'] == n) & (df['alpha'] == alpha)]['perfect_rate'].mean()
    
    im = axes[1].imshow(perfect_grid, aspect='auto', cmap='RdYlGn', 
                       vmin=0, vmax=1, origin='lower')
    axes[1].set_xticks(range(len(n_vals)))
    axes[1].set_xticklabels(n_vals)
    axes[1].set_yticks(range(len(alpha_vals)))
    axes[1].set_yticklabels([f'{a:.1f}' for a in alpha_vals])
    axes[1].set_xlabel('n (receivers)', fontsize=10)
    axes[1].set_ylabel('α (imbalance)', fontsize=10)
    axes[1].set_title('Perfect Matching Rate (Averaged)', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=axes[1], label='Perfect Rate')
    
    # Add text annotations
    for i in range(len(alpha_vals)):
        for j in range(len(n_vals)):
            text = axes[1].text(j, i, f'{perfect_grid[i, j]:.2f}',
                              ha="center", va="center", 
                              color="black", fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../results/perfect_matching_summary.png', dpi=150, bbox_inches='tight')
    print('saved perfect_matching_summary.png')

def plot_runtime_analysis(df):
    """runtime analysis across configurations"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Runtime by market size (n)
    for d_policy in sorted(df['d_policy_name'].unique()):
        policy_data = df[df['d_policy_name'] == d_policy].groupby('n').agg({
            'runtime_mean': 'mean'
        }).reset_index()
        
        axes[0].plot(policy_data['n'], policy_data['runtime_mean'] * 1000,
                    marker='o', linewidth=2, markersize=8, label=d_policy)
    
    axes[0].set_xlabel('n (receivers)', fontsize=10)
    axes[0].set_ylabel('Runtime (ms)', fontsize=10)
    axes[0].set_title('Runtime vs Market Size', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[0].set_xscale('log')
    axes[0].set_yscale('log')
    
    # Right: Runtime by imbalance (alpha)
    for d_policy in sorted(df['d_policy_name'].unique()):
        policy_data = df[df['d_policy_name'] == d_policy].groupby('alpha').agg({
            'runtime_mean': 'mean'
        }).reset_index()
        
        axes[1].plot(policy_data['alpha'], policy_data['runtime_mean'] * 1000,
                    marker='s', linewidth=2, markersize=8, label=d_policy)
    
    axes[1].set_xlabel('α (imbalance)', fontsize=10)
    axes[1].set_ylabel('Runtime (ms)', fontsize=10)
    axes[1].set_title('Runtime vs Imbalance', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../results/runtime_analysis.png', dpi=150, bbox_inches='tight')
    print('saved runtime_analysis.png')

if __name__ == "__main__":
    print('='*60)
    print('GENERATING VISUALIZATIONS FOR SWEEP RESULTS')
    print('='*60)
    
    print('\nloading results from csv...')
    df = load_results()
    
    print(f'loaded {len(df)} configurations')
    print(f'  n values: {sorted(df["n"].unique())}')
    print(f'  alpha values: {sorted(df["alpha"].unique())}')
    print(f'  d policies: {sorted(df["d_policy_name"].unique())}')
    print()
    
    print('generating plots...')
    print('-' * 60)
    
    plot_baseline_average_rank(df)
    plot_rank_vs_lower_bound(df)
    plot_approximation_ratio_heatmap(df)
    plot_rank_by_imbalance(df)
    plot_perfect_matching_summary(df)
    plot_runtime_analysis(df)
    
    print('-' * 60)
    print('\n✓ All visualizations generated successfully!')
    print('='*60)
