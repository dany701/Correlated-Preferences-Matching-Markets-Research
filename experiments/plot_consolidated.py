"""
Consolidated plots: One figure per research question.

Three core questions:
1. FEASIBILITY: At what d does perfect matching emerge?
2. QUALITY: How do ranks degrade with competition?
3. SCALING: How does runtime grow with n?
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import log

# Consistent color scheme across all plots
REGIME_COLORS = {
    'Small': '#2E86AB',   # Blue
    'Medium': '#F18F01',  # Orange
    'Large': '#C73E1D'    # Red
}

def compute_d0(n, alpha):
    """Theoretical threshold d0(n, alpha) for perfect matching"""
    numerator = (1 + alpha)
    denominator = alpha + 1 / (n * (1 + alpha))
    return log(n) * log(numerator / denominator)

def plot_feasibility(df_threshold):
    """
    QUESTION 1: FEASIBILITY
    At what list length d* does perfect matching emerge?
    """
    plt.figure(figsize=(10, 7))
    
    for regime in ['Small', 'Medium', 'Large']:
        regime_data = df_threshold[df_threshold['regime'] == regime].sort_values('n')
        
        if regime_data.empty:
            continue
        
        alpha = regime_data['alpha'].iloc[0]
        color = REGIME_COLORS[regime]
        
        # Plot empirical d* vs n (solid line)
        plt.plot(regime_data['n'], regime_data['d_star'],
                marker='o', linewidth=3, markersize=12,
                label=f'{regime} (α={alpha:.1f}) - Empirical d*',
                color=color, alpha=0.9)
        
        # Plot theoretical d0 vs n (dashed line)
        n_smooth = np.logspace(np.log10(regime_data['n'].min()), 
                               np.log10(regime_data['n'].max()), 50)
        d0_values = [compute_d0(n, alpha) for n in n_smooth]
        plt.plot(n_smooth, d0_values, '--',
                linewidth=2, color=color, alpha=0.5,
                label=f'{regime} (α={alpha:.1f}) - Theory d₀')
        
        # Add value labels for empirical d*
        for _, row in regime_data.iterrows():
            plt.annotate(f"{row['d_star']}", 
                        xy=(row['n'], row['d_star']),
                        xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=10, fontweight='bold',
                        color=color, alpha=0.9)
    
    # Reference lines - smooth curves across full range
    n_min = df_threshold['n'].min()
    n_max = df_threshold['n'].max()
    n_range = np.logspace(np.log10(n_min), np.log10(n_max), 100)
    plt.plot(n_range, np.log(n_range), 'k--', alpha=0.25, linewidth=1.5, label='ln(n)')
    plt.plot(n_range, (np.log(n_range))**2, 'k:', alpha=0.25, linewidth=1.5, label='(ln(n))²')
    
    plt.xlabel('Market Size n (receivers)', fontsize=13, fontweight='bold')
    plt.ylabel('Minimal List Length d*', fontsize=13, fontweight='bold')
    plt.title('Q1: FEASIBILITY — Threshold for Perfect Matching\n' + 
              'Minimal d* such that P(perfect matching) ≥ 80%',
             fontsize=14, fontweight='bold', pad=15)
    plt.legend(fontsize=11, loc='upper left', framealpha=0.95)
    plt.grid(alpha=0.3, linestyle=':')
    plt.xscale('log')
    plt.yscale('log')
    
    # Ensure x-axis shows full range including n=5000
    plt.xlim(n_min * 0.7, n_max * 1.3)
    
    # Explicitly set x-axis ticks to show all n values
    n_ticks = sorted(df_threshold['n'].unique())
    plt.xticks(n_ticks, [f'{int(n)}' for n in n_ticks])
    
    # Add insight box
    textstr = 'Key Finding:\nHigher competition (α↑)\n→ Lower d* needed!\n\n(Probabilistic coverage)'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
    plt.text(0.98, 0.30, textstr, transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    plt.savefig('../results/figure1_feasibility.png', dpi=150, bbox_inches='tight')
    print('✓ Figure 1: Feasibility (threshold)')

def plot_quality(df_sweep):
    """
    QUESTION 2: QUALITY
    How do proposer ranks degrade with competition?
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    d_policies = sorted(df_sweep['d_policy_name'].unique())
    n_vals = sorted(df_sweep['n'].unique())
    
    colors_n = plt.cm.viridis(np.linspace(0.2, 0.9, len(n_vals)))
    
    for idx, d_policy in enumerate(d_policies):
        subset = df_sweep[df_sweep['d_policy_name'] == d_policy]
        
        for n_val, color in zip(n_vals, colors_n):
            n_data = subset[subset['n'] == n_val].sort_values('alpha')
            
            if n_data.empty:
                continue
            
            # Empirical (solid)
            axes[idx].errorbar(n_data['alpha'], n_data['avg_proposer_rank'],
                              yerr=n_data['std_proposer_rank'],
                              marker='o', linewidth=2.5, markersize=8,
                              label=f'n={n_val}', 
                              color=color, capsize=4, alpha=0.9, linestyle='-')
            
            # Theoretical bound (dashed, lighter)
            axes[idx].plot(n_data['alpha'], n_data['lb_rank'],
                          linestyle='--', linewidth=2, color=color, alpha=0.4)
        
        # Legend
        from matplotlib.lines import Line2D
        handles, labels = axes[idx].get_legend_handles_labels()
        handles.extend([
            Line2D([0], [0], color='gray', linewidth=2.5, linestyle='-', label='Empirical'),
            Line2D([0], [0], color='gray', linewidth=2, linestyle='--', alpha=0.6, label='Theory Bound')
        ])
        labels.extend(['— Empirical', '- - Theory Bound'])
        
        axes[idx].set_xlabel('Imbalance α = m/n - 1', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Average Proposer Rank (log scale)', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'{d_policy}', fontsize=12, fontweight='bold')
        axes[idx].legend(handles, labels, fontsize=8, loc='upper left')
        axes[idx].grid(alpha=0.3, linestyle=':', which='both')
        axes[idx].set_yscale('log')  # LOG SCALE to see empirical differences clearly
        
        # Regime shading
        axes[idx].axvspan(0, 3, alpha=0.06, color=REGIME_COLORS['Small'])
        axes[idx].axvspan(4, 8, alpha=0.06, color=REGIME_COLORS['Medium'])
        axes[idx].axvspan(11, 20, alpha=0.06, color=REGIME_COLORS['Large'])
    
    plt.suptitle('Q2: QUALITY — Rank Degradation with Competition\n' +
                'Empirical ranks vs theoretical lower bounds', 
                fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('../results/figure2_quality.png', dpi=150, bbox_inches='tight')
    print('✓ Figure 2: Quality (rank vs competition)')

def plot_scaling():
    """
    QUESTION 3: SCALING
    How does runtime grow with n?
    
    Combines data from scaling_test results.
    """
    # Load scaling test data (hardcoded from previous run)
    scaling_data = {
        'n': [500, 1000, 2000, 5000],
        'alpha_2': [0.049, 0.113, 0.280, 1.213],
        'alpha_7': [0.141, 0.423, 0.942, 3.897],
        'alpha_19': [0.377, 1.009, 2.623, 10.922]
    }
    
    plt.figure(figsize=(10, 7))
    
    # Plot each alpha
    for (label, alpha_val, data_key) in [
        ('Small (α=2)', 2, 'alpha_2'),
        ('Medium (α=7)', 7, 'alpha_7'),
        ('Large (α=19)', 19, 'alpha_19')
    ]:
        regime = 'Small' if alpha_val <= 3 else ('Medium' if alpha_val <= 10 else 'Large')
        color = REGIME_COLORS[regime]
        
        plt.loglog(scaling_data['n'], scaling_data[data_key],
                  marker='o', linewidth=3, markersize=10,
                  label=label, color=color, alpha=0.9)
    
    # Reference lines
    n_range = np.array([500, 5000])
    
    # O(n) reference
    baseline = 0.001
    plt.loglog(n_range, baseline * n_range / n_range[0], 
              'k--', alpha=0.3, linewidth=1.5, label='O(n)')
    
    # O(n log n) reference
    plt.loglog(n_range, baseline * (n_range * np.log(n_range)) / (n_range[0] * np.log(n_range[0])), 
              'k:', alpha=0.3, linewidth=1.5, label='O(n log n)')
    
    plt.xlabel('Market Size n (receivers)', fontsize=13, fontweight='bold')
    plt.ylabel('Runtime (seconds)', fontsize=13, fontweight='bold')
    plt.title('Q3: SCALING — Runtime Growth with Market Size\n' +
              'On-demand DA algorithm with d=(ln(n))² lists',
             fontsize=14, fontweight='bold', pad=15)
    plt.legend(fontsize=11, loc='upper left', framealpha=0.95)
    plt.grid(alpha=0.3, which='both', linestyle=':')
    
    # Add insight box
    textstr = 'Algorithm scales\n~O(m·d) as expected\n\nFeasible for\nn=5000 (80K agents)\nin <12 seconds'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
    plt.text(0.98, 0.02, textstr, transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    plt.savefig('../results/figure3_scaling.png', dpi=150, bbox_inches='tight')
    print('✓ Figure 3: Scaling (runtime)')

if __name__ == "__main__":
    print('='*70)
    print('GENERATING CONSOLIDATED FIGURES')
    print('Three figures, three questions')
    print('='*70)
    print()
    
    # Load data
    print('Loading data...')
    df_threshold = pd.read_csv('../results/threshold_results.csv')
    df_sweep = pd.read_csv('../results/sweep_results.csv')
    
    print('Generating figures...')
    print('-'*70)
    
    plot_feasibility(df_threshold)
    plot_quality(df_sweep)
    plot_scaling()
    
    print('-'*70)
    print()
    print('✓ All consolidated figures generated!')
    print()
    print('Final figures:')
    print('  1. figure1_feasibility.png   (Q1: Threshold for perfect matching)')
    print('  2. figure2_quality.png       (Q2: Rank degradation)')
    print('  3. figure3_scaling.png       (Q3: Runtime growth)')
    print('='*70)

