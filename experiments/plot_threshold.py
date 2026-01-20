"""
Visualize threshold search results: d* vs n curves.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import log

def load_results(filename='../results/threshold_results.csv'):
    """Load threshold search results."""
    return pd.read_csv(filename)

def plot_threshold_curves(df):
    """
    Main plot: d* vs n, one curve per alpha regime.
    
    This is the CORE RESULT of the threshold experiment.
    """
    plt.figure(figsize=(12, 7))
    
    # Colors for regimes
    regime_colors = {
        'Small': '#2E86AB',
        'Medium': '#F18F01',
        'Large': '#C73E1D'
    }
    
    # Plot each regime
    for regime in ['Small', 'Medium', 'Large']:
        regime_data = df[df['regime'] == regime].sort_values('n')
        
        if regime_data.empty:
            continue
        
        alpha = regime_data['alpha'].iloc[0]
        color = regime_colors[regime]
        
        # Plot d* vs n
        plt.plot(regime_data['n'], regime_data['d_star'],
                marker='o', linewidth=3, markersize=10,
                label=f'{regime} (α={alpha:.1f})',
                color=color, alpha=0.9)
        
        # Add data labels
        for _, row in regime_data.iterrows():
            plt.annotate(f"{row['d_star']}", 
                        xy=(row['n'], row['d_star']),
                        xytext=(0, 10), textcoords='offset points',
                        ha='center', fontsize=9, fontweight='bold',
                        color=color, alpha=0.8)
    
    # Reference lines for comparison
    n_range = np.array(sorted(df['n'].unique()))
    
    # ln(n) reference
    ln_n = np.log(n_range)
    plt.plot(n_range, ln_n, 'k--', alpha=0.3, linewidth=1.5, label='ln(n)')
    
    # (ln(n))² reference
    ln_n_sq = (np.log(n_range))**2
    plt.plot(n_range, ln_n_sq, 'k:', alpha=0.3, linewidth=1.5, label='(ln(n))²')
    
    # sqrt(n) reference
    sqrt_n = np.sqrt(n_range)
    plt.plot(n_range, sqrt_n, 'k-.', alpha=0.3, linewidth=1.5, label='√n')
    
    plt.xlabel('Market Size n (receivers)', fontsize=14, fontweight='bold')
    plt.ylabel('Minimal List Length d*', fontsize=14, fontweight='bold')
    plt.title('Threshold for Perfect Matching: d* vs Market Size\n(P(perfect matching) ≥ 0.8)', 
             fontsize=16, fontweight='bold')
    plt.legend(fontsize=12, loc='upper left', framealpha=0.95)
    plt.grid(alpha=0.3, linestyle=':')
    plt.xscale('log')
    plt.yscale('log')
    
    # Add text box with interpretation
    textstr = 'Higher α (more competition)\n→ higher d* needed'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    plt.text(0.98, 0.02, textstr, transform=plt.gca().transAxes, fontsize=11,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    plt.savefig('../results/threshold_main.png', dpi=150, bbox_inches='tight')
    print('✓ Saved threshold_main.png')

def plot_scaling_analysis(df):
    """
    Secondary plot: Show how d* scales with n (log-log).
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    regime_colors = {
        'Small': '#2E86AB',
        'Medium': '#F18F01',
        'Large': '#C73E1D'
    }
    
    # Left: d* vs n (log-log)
    for regime in ['Small', 'Medium', 'Large']:
        regime_data = df[df['regime'] == regime].sort_values('n')
        
        if regime_data.empty:
            continue
        
        alpha = regime_data['alpha'].iloc[0]
        color = regime_colors[regime]
        
        axes[0].loglog(regime_data['n'], regime_data['d_star'],
                      marker='o', linewidth=2.5, markersize=8,
                      label=f'{regime} (α={alpha:.1f})',
                      color=color, alpha=0.9)
    
    axes[0].set_xlabel('Market Size n', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('d*', fontsize=12, fontweight='bold')
    axes[0].set_title('Threshold Scaling (log-log)', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(alpha=0.3, which='both', linestyle=':')
    
    # Right: Normalized d*/n vs n
    for regime in ['Small', 'Medium', 'Large']:
        regime_data = df[df['regime'] == regime].sort_values('n')
        
        if regime_data.empty:
            continue
        
        alpha = regime_data['alpha'].iloc[0]
        color = regime_colors[regime]
        
        ratio = regime_data['d_star'] / regime_data['n']
        
        axes[1].plot(regime_data['n'], ratio,
                    marker='s', linewidth=2.5, markersize=8,
                    label=f'{regime} (α={alpha:.1f})',
                    color=color, alpha=0.9)
    
    axes[1].set_xlabel('Market Size n', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('d*/n (fraction)', fontsize=12, fontweight='bold')
    axes[1].set_title('Relative Threshold', fontsize=13, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(alpha=0.3, linestyle=':')
    axes[1].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('../results/threshold_scaling.png', dpi=150, bbox_inches='tight')
    print('✓ Saved threshold_scaling.png')

def plot_summary_table(df):
    """
    Create a summary visualization showing all d* values.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table data
    n_values = sorted(df['n'].unique())
    regimes = ['Small', 'Medium', 'Large']
    
    table_data = []
    table_data.append(['n →'] + [str(n) for n in n_values])
    
    for regime in regimes:
        regime_data = df[df['regime'] == regime].sort_values('n')
        alpha = regime_data['alpha'].iloc[0]
        
        row = [f'{regime}\n(α={alpha:.1f})']
        for n in n_values:
            d_val = regime_data[regime_data['n'] == n]['d_star']
            if not d_val.empty:
                row.append(str(int(d_val.iloc[0])))
            else:
                row.append('—')
        table_data.append(row)
    
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.2] + [0.2]*len(n_values))
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(len(n_values) + 1):
        table[(0, i)].set_facecolor('#CCCCCC')
        table[(0, i)].set_text_props(weight='bold')
    
    # Style regime column
    for i in range(1, len(regimes) + 1):
        table[(i, 0)].set_facecolor('#EEEEEE')
        table[(i, 0)].set_text_props(weight='bold')
    
    # Color code cells by regime
    regime_colors = {'Small': '#E3F2FD', 'Medium': '#FFF3E0', 'Large': '#FFEBEE'}
    for i, regime in enumerate(regimes, 1):
        for j in range(1, len(n_values) + 1):
            table[(i, j)].set_facecolor(regime_colors[regime])
    
    plt.title('Minimal d* for Perfect Matching (P ≥ 0.8)', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('../results/threshold_table.png', dpi=150, bbox_inches='tight')
    print('✓ Saved threshold_table.png')

if __name__ == "__main__":
    print('='*70)
    print('THRESHOLD VISUALIZATION')
    print('='*70)
    
    print('\nLoading results...')
    df = load_results()
    
    print(f'Loaded {len(df)} results')
    print(f'  Regimes: {sorted(df["regime"].unique())}')
    print(f'  Market sizes: {sorted(df["n"].unique())}')
    print()
    
    print('Generating plots...')
    print('-'*70)
    
    plot_threshold_curves(df)
    plot_scaling_analysis(df)
    plot_summary_table(df)
    
    print('-'*70)
    print('\n✓ All threshold plots generated!')
    print('\nPlots saved:')
    print('  1. threshold_main.png      (THE MAIN RESULT)')
    print('  2. threshold_scaling.png   (Scaling analysis)')
    print('  3. threshold_table.png     (Summary table)')
    print('='*70)

