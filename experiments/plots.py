import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def load_results(filename='../results/sweep_results.csv'):
    """load sweep results from csv"""
    return pd.read_csv(filename)

def get_regime_label(alpha):
    """Get regime label for alpha value."""
    if alpha <= 3:
        return "Small"
    elif alpha <= 8:
        return "Medium"
    else:
        return "Large"

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
            
            # Plot empirical rank with error bars (solid line)
            axes[idx].errorbar(n_data['alpha'], n_data['avg_proposer_rank'],
                              yerr=n_data['std_proposer_rank'],
                              marker='o', linewidth=2.5, markersize=8,
                              label=f'n={n_val}', 
                              color=color, capsize=4, alpha=0.9, linestyle='-')
            
            # Overlay theoretical lower bound (dashed, no label since we'll add legend separately)
            axes[idx].plot(n_data['alpha'], n_data['lb_rank'],
                          linestyle='--', linewidth=2, color=color, alpha=0.6)
            
            # Add regime labels to data points
            for _, row in n_data.iterrows():
                regime = get_regime_label(row['alpha'])
                axes[idx].annotate(regime, 
                                  xy=(row['alpha'], row['avg_proposer_rank']),
                                  xytext=(0, 8), textcoords='offset points',
                                  ha='center', fontsize=7, alpha=0.7,
                                  bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor=color, alpha=0.2, edgecolor='none'))
        
        # Add custom legend entries for line styles
        from matplotlib.lines import Line2D
        legend_elements = axes[idx].get_legend_handles_labels()[0]
        legend_labels = axes[idx].get_legend_handles_labels()[1]
        
        # Add explanation for line styles
        legend_elements.extend([
            Line2D([0], [0], color='gray', linewidth=2.5, linestyle='-', label='Empirical'),
            Line2D([0], [0], color='gray', linewidth=2, linestyle='--', alpha=0.6, label='Theoretical Bound')
        ])
        legend_labels.extend(['— Empirical', '- - Theoretical Bound'])
        
        axes[idx].set_xlabel('Imbalance α = m/n - 1', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('Average Proposer Rank', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'{d_policy}', fontsize=13, fontweight='bold')
        axes[idx].legend(legend_elements, legend_labels, fontsize=9, loc='best')
        axes[idx].grid(alpha=0.3, linestyle=':')
        
        # Add regime shading with labels
        axes[idx].axvspan(0, 3, alpha=0.08, color='green')
        axes[idx].axvspan(4, 8, alpha=0.08, color='yellow')
        axes[idx].axvspan(11, 20, alpha=0.08, color='red')
        
        # Add regime text labels
        y_pos = axes[idx].get_ylim()[1] * 0.98
        axes[idx].text(1.5, y_pos, 'Small', ha='center', va='top', 
                      fontsize=9, fontweight='bold', alpha=0.6, color='green')
        axes[idx].text(6, y_pos, 'Medium', ha='center', va='top',
                      fontsize=9, fontweight='bold', alpha=0.6, color='orange')
        axes[idx].text(15, y_pos, 'Large', ha='center', va='top',
                      fontsize=9, fontweight='bold', alpha=0.6, color='red')
    
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
            
            # Add regime labels to data points
            for _, row in n_data.iterrows():
                regime = get_regime_label(row['alpha'])
                axes[idx].annotate(regime, 
                                  xy=(row['alpha'], row['ratio']),
                                  xytext=(0, 8), textcoords='offset points',
                                  ha='center', fontsize=7, alpha=0.7,
                                  bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor=color, alpha=0.2, edgecolor='none'))
        
        # Add horizontal line at ratio=1 (optimal)
        axes[idx].axhline(1.0, color='red', linestyle='--', linewidth=2, 
                         alpha=0.7, label='Ratio=1 (optimal)')
        
        axes[idx].set_xlabel('Imbalance α = m/n - 1', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('Approximation Ratio (Empirical / Bound)', fontsize=12, fontweight='bold')
        axes[idx].set_title(f'{d_policy}', fontsize=13, fontweight='bold')
        axes[idx].legend(fontsize=9, loc='upper right')
        axes[idx].grid(alpha=0.3, linestyle=':')
        axes[idx].set_ylim([0, max(df['ratio'].max() * 1.1, 0.3)])
        
        # Add regime shading with labels
        axes[idx].axvspan(0, 3, alpha=0.08, color='green')
        axes[idx].axvspan(4, 8, alpha=0.08, color='yellow')
        axes[idx].axvspan(11, 20, alpha=0.08, color='red')
        
        # Add regime text labels
        y_pos = axes[idx].get_ylim()[1] * 0.98
        axes[idx].text(1.5, y_pos, 'Small', ha='center', va='top', 
                      fontsize=9, fontweight='bold', alpha=0.6, color='green')
        axes[idx].text(6, y_pos, 'Medium', ha='center', va='top',
                      fontsize=9, fontweight='bold', alpha=0.6, color='orange')
        axes[idx].text(15, y_pos, 'Large', ha='center', va='top',
                      fontsize=9, fontweight='bold', alpha=0.6, color='red')
    
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
        'Small Imbalance (α=2)': 2.0,
        'Medium Imbalance (α=7)': 7.0,
        'Large Imbalance (α=15)': 15.0
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
        axes[idx].legend(fontsize=10, loc='best')
        axes[idx].grid(alpha=0.3, linestyle=':')
        axes[idx].set_ylim([-0.05, 1.05])
    
    plt.suptitle('Phase Transition: Perfect Matching Threshold (Theorem 2)', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('../results/plot3_perfect_matching_threshold.png', dpi=150, bbox_inches='tight')
    print('✓ Plot 3: Perfect Matching Threshold (Phase Transition)')

if __name__ == "__main__":
    print('='*70)
    print('GENERATING 3 ESSENTIAL PLOTS')
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
    
    print('-'*70)
    print('\n✓ All 3 essential plots generated successfully!')
    print('\nPlots saved:')
    print('  1. plot1_rank_vs_imbalance.png       (THE MAIN PLOT)')
    print('  2. plot2_approximation_ratio.png     (Quality/Gap)')
    print('  3. plot3_perfect_matching_threshold.png (Phase Transition)')
    print('='*70)
