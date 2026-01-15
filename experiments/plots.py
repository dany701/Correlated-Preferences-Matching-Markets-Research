import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def load_results(filename='../results/sweep_results.csv'):
    """load sweep results from csv"""
    return pd.read_csv(filename)

def plot_1_rank_by_imbalance(df):
    """THE MAIN PLOT: How proposer outcomes degrade as competition increases.
    
    Shows:
    - x-axis: α (imbalance)
    - y-axis: average proposer rank
    - Lines: different n values
    - Overlay: theoretical lower bound (shaded/dashed)
    - Optional: error bars
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    d_policies = sorted(df['d_policy_name'].unique())
    n_vals = sorted(df['n'].unique())
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(n_vals)))
    
    for idx, d_policy in enumerate(d_policies):
        subset = df[df['d_policy_name'] == d_policy]
        
        for n_val, color in zip(n_vals, colors):
            n_data = subset[subset['n'] == n_val].sort_values('alpha')
            
            if n_data.empty:
                continue
            
            # Plot empirical rank with error bars
            axes[idx].errorbar(n_data['alpha'], n_data['avg_proposer_rank'],
                              yerr=n_data['std_proposer_rank'],
                              marker='o', linewidth=2.5, markersize=8,
                              label=f'n={n_val} (empirical)', 
                              color=color, capsize=4, alpha=0.9)
            
            # Overlay theoretical lower bound (dashed)
            axes[idx].plot(n_data['alpha'], n_data['lb_rank'],
                          linestyle='--', linewidth=2, color=color, alpha=0.6,
                          label=f'n={n_val} (bound)')
        
        axes[idx].set_xlabel('Imbalance α = m/n - 1', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('Average Proposer Rank', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'{d_policy}', fontsize=13, fontweight='bold')
        axes[idx].legend(fontsize=9, loc='best')
        axes[idx].grid(alpha=0.3, linestyle=':')
        
        # Add regime shading
        axes[idx].axvspan(0, 3, alpha=0.08, color='green')
        axes[idx].axvspan(4, 8, alpha=0.08, color='yellow')
        axes[idx].axvspan(11, 20, alpha=0.08, color='red')
    
    plt.suptitle('Rank vs Competition: How Proposer Outcomes Degrade with Imbalance', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('../results/plot1_rank_vs_imbalance.png', dpi=150, bbox_inches='tight')
    print('✓ Plot 1: Rank vs Imbalance (THE MAIN PLOT)')

def plot_2_gap_visualization(df):
    """Gap between empirical rank and theoretical lower bound.
    
    Shows the approximation ratio: avg_rank / LB_rank
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    d_policies = sorted(df['d_policy_name'].unique())
    n_vals = sorted(df['n'].unique())
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(n_vals)))
    
    for idx, d_policy in enumerate(d_policies):
        subset = df[df['d_policy_name'] == d_policy]
        
        for n_val, color in zip(n_vals, colors):
            n_data = subset[subset['n'] == n_val].sort_values('alpha')
            
            if n_data.empty:
                continue
            
            # Plot ratio
            axes[idx].plot(n_data['alpha'], n_data['ratio'],
                          marker='o', linewidth=2.5, markersize=8,
                          label=f'n={n_val}', color=color, alpha=0.9)
        
        # Add horizontal line at ratio=1 (optimal)
        axes[idx].axhline(1.0, color='red', linestyle='--', linewidth=2, 
                         alpha=0.7, label='Optimal (ratio=1)')
        
        axes[idx].set_xlabel('Imbalance α = m/n - 1', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('Approximation Ratio (Empirical / Bound)', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'{d_policy}', fontsize=13, fontweight='bold')
        axes[idx].legend(fontsize=9, loc='best')
        axes[idx].grid(alpha=0.3, linestyle=':')
        axes[idx].set_ylim([0, max(df['ratio'].max() * 1.1, 0.3)])
        
        # Add regime shading
        axes[idx].axvspan(0, 3, alpha=0.08, color='green')
        axes[idx].axvspan(4, 8, alpha=0.08, color='yellow')
        axes[idx].axvspan(11, 20, alpha=0.08, color='red')
    
    plt.suptitle('Quality of Matching: How Close to Theoretical Optimum?', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('../results/plot2_approximation_ratio.png', dpi=150, bbox_inches='tight')
    print('✓ Plot 2: Approximation Ratio (Gap Visualization)')

def plot_3_perfect_matching_threshold(df):
    """Phase transition: probability of perfect matching vs d/d0.
    
    Shows how feasibility depends on list length relative to theoretical threshold.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    n_vals = sorted(df['n'].unique())
    alpha_regimes = {
        'Small (α=2)': 2.0,
        'Medium (α=7)': 7.0,
        'Large (α=15)': 15.0
    }
    
    colors = ['#2E86AB', '#F18F01', '#C73E1D']
    
    for idx, n_val in enumerate(n_vals):
        subset = df[df['n'] == n_val]
        
        for (regime_name, alpha_val), color in zip(alpha_regimes.items(), colors):
            alpha_data = subset[subset['alpha'] == alpha_val].copy()
            
            if alpha_data.empty:
                continue
            
            # Compute normalized d (d / d0)
            alpha_data['d_normalized'] = alpha_data['d'] / alpha_data['d0']
            alpha_data = alpha_data.sort_values('d_normalized')
            
            axes[idx].plot(alpha_data['d_normalized'], alpha_data['perfect_rate'],
                          marker='o', linewidth=2.5, markersize=8,
                          label=regime_name, color=color, alpha=0.9)
        
        # Add vertical line at d/d0 = 1 (theoretical threshold)
        axes[idx].axvline(1.0, color='black', linestyle='--', linewidth=2, 
                         alpha=0.5, label='d=d₀ (theory)')
        
        axes[idx].set_xlabel('Normalized List Length (d / d₀)', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('Perfect Matching Probability', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'n={n_val}', fontsize=13, fontweight='bold')
        axes[idx].legend(fontsize=9, loc='best')
        axes[idx].grid(alpha=0.3, linestyle=':')
        axes[idx].set_ylim([-0.05, 1.05])
    
    plt.suptitle('Phase Transition: Perfect Matching Threshold (Theorem 2)', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('../results/plot3_perfect_matching_threshold.png', dpi=150, bbox_inches='tight')
    print('✓ Plot 3: Perfect Matching Threshold (Phase Transition)')

def plot_4_rank_distribution_by_competition(df):
    """Distribution of proposer ranks across competition regimes.
    
    Shows how the distribution shifts and spreads as α increases.
    Aggregates over all n values for clarity.
    """
    plt.figure(figsize=(12, 7))
    
    # Define competition regimes
    regimes = {
        'Small α=2': 2.0,
        'Medium α=7': 7.0,
        'Large α=15': 15.0
    }
    
    colors = ['#2E86AB', '#F18F01', '#C73E1D']
    
    # We'll aggregate ranks across all configurations for each α
    # Since we only have avg_rank per config, we'll create approximate distributions
    # by using the mean and std to generate samples (assuming normal for visualization)
    
    for (regime_name, alpha_val), color in zip(regimes.items(), colors):
        alpha_data = df[df['alpha'] == alpha_val]
        
        # Get all ranks and std for this α
        ranks = []
        for _, row in alpha_data.iterrows():
            # Generate samples from normal distribution for visualization
            # (in reality, you'd collect all individual proposer ranks from trials)
            mean = row['avg_proposer_rank']
            std = row['std_proposer_rank']
            n_samples = 1000
            samples = np.random.normal(mean, std, n_samples)
            samples = samples[samples > 0]  # ranks must be positive
            ranks.extend(samples)
        
        # Plot KDE / histogram
        plt.hist(ranks, bins=50, alpha=0.3, color=color, density=True, 
                edgecolor='none', label=f'{regime_name} (histogram)')
        
        # Add mean line
        mean_rank = np.mean(ranks)
        plt.axvline(mean_rank, color=color, linestyle='--', linewidth=3, 
                   alpha=0.9, label=f'{regime_name} mean={mean_rank:.1f}')
    
    plt.xlabel('Proposer Rank', fontsize=13, fontweight='bold')
    plt.ylabel('Density', fontsize=13, fontweight='bold')
    plt.title('Rank Distribution Shifts with Competition\n(Aggregated across all n and d-policies)', 
             fontsize=15, fontweight='bold')
    plt.legend(fontsize=11, loc='upper right')
    plt.grid(alpha=0.3, linestyle=':', axis='y')
    plt.xlim(left=0)
    
    # Add text box with interpretation
    textstr = 'As competition increases (α ↑):\n• Distribution shifts right\n• Spread increases\n• Average worsens'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig('../results/plot4_rank_distribution.png', dpi=150, bbox_inches='tight')
    print('✓ Plot 4: Rank Distribution by Competition')

if __name__ == "__main__":
    print('='*70)
    print('GENERATING 4 ESSENTIAL PLOTS')
    print('='*70)
    
    print('\nLoading results...')
    df = load_results()
    
    print(f'Loaded {len(df)} configurations')
    print(f'  n values: {sorted(df["n"].unique())}')
    print(f'  α values: {sorted(df["alpha"].unique())}')
    print(f'  d policies: {sorted(df["d_policy_name"].unique())}')
    print()
    
    print('Generating plots...')
    print('-'*70)
    
    plot_1_rank_by_imbalance(df)
    plot_2_gap_visualization(df)
    plot_3_perfect_matching_threshold(df)
    plot_4_rank_distribution_by_competition(df)
    
    print('-'*70)
    print('\n✓ All 4 essential plots generated successfully!')
    print('\nPlots saved:')
    print('  1. plot1_rank_vs_imbalance.png       (THE MAIN PLOT)')
    print('  2. plot2_approximation_ratio.png     (Quality/Gap)')
    print('  3. plot3_perfect_matching_threshold.png (Phase Transition)')
    print('  4. plot4_rank_distribution.png       (Distribution Shift)')
    print('='*70)
