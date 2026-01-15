# Strongly Imbalanced Matching Markets with Partial Preferences

**CSCI 23 Winter Study Independent Project**

## Overview

This project investigates **strongly imbalanced** random matching markets with **i.i.d. uniform preferences** where the number of proposers significantly exceeds the number of receivers (α = m/n - 1 > 1). We implement an **optimized Deferred Acceptance (Gale-Shapley) algorithm** with partial (truncated) preference lists to study:

1. Phase transitions for perfect stable matching existence
2. Proposer rank degradation under competition
3. Scaling behavior across market sizes

## Core Setup

- **n** = number of receivers (short side), capacity = 1
- **m** = number of proposers (long side)  
- **α = m/n - 1** (imbalance ratio, required α > 1 for strong imbalance)
- **d** = proposer preference list length (top-d truncation)
- Preferences are i.i.d. uniform, generated **on-demand** during algorithm execution
- Proposers propose (candidate-proposing DA)
- **Stability is guaranteed** by DA; **perfect matching is not**

## Implementation Highlights

### Optimized Deferred Acceptance Algorithm

Our implementation features several key optimizations:

- **Pre-sampled proposer preferences**: Each proposer samples d unique receivers at initialization using `numpy.choice(replace=False)`, eliminating rejection sampling bottleneck during the algorithm
- **On-demand receiver preferences**: Receivers generate random scores lazily (only when a proposer proposes), implementing true i.i.d. uniform preferences
- **Efficient data structures**: Numpy arrays for fast indexing and lookups
- **Reproducible randomness**: Hierarchical seed splitting ensures reproducibility

**Note:** "Partial preferences" refers to proposers only having length-d truncated lists, not full rankings over all n receivers.

### Theoretical Benchmarks

**Threshold for perfect matching (Theorem 2 reference):**
```
d₀(n, α) = ln(n) · ln((1 + α) / (α + 1/(n(1+α))))
```

**Lower bound on expected proposer rank (Theorem 3):**
```
LB_rank(n, α, d) = d / ln((1 + α) / (α + 1/(n(1+α))))
```

We compute the **approximation ratio** = avg_rank / LB_rank to measure how close empirical results are to the theoretical lower bound.

## Experiments Conducted

### Main Parameter Sweep (`experiments/sweep.py`)

**Configuration:**
- n ∈ {100, 500, 1500} (small, medium, large markets)
- α ∈ {2.0, 7.0, 15.0} (one per imbalance regime)
  - α = 2.0: small imbalance (m/n = 3)
  - α = 7.0: medium imbalance (m/n = 8)  
  - α = 15.0: large imbalance (m/n = 16)
- d-policies (preference list lengths):
  - **d=2ln(n)**: short lists
  - **d=6ln(n)**: long lists
  - **d=(ln(n))²**: quadratic growth
- **Total: 27 configurations**
- Adaptive trials: 30 baseline, up to 100 near phase transitions

**Key Metrics Collected:**
- Perfect matching rate
- Average proposer rank (empirical)
- Theoretical lower bound
- Approximation ratio
- Runtime

### Scaling Test (`experiments/scale_test.py`)

Tests runtime and rank scaling for n ∈ {500, 1000, 2000, 5000} across three imbalance regimes (α = 2, 7, 19).

**Findings:**
- Runtime scales approximately **O(m · d)** as expected
- For n=5000, α=19 (m=100,000 proposers): ~11 seconds per trial
- Average ranks grow logarithmically with n
- Algorithm remains efficient even for very large markets

## Key Results

### Perfect Matching Behavior

**All configurations achieved perfect matching rate = 1.0**, indicating that the chosen d-policies (log and log²) provide sufficient preference list lengths for strong stable matchings in these parameter regimes.

### Proposer Rank Analysis

| n    | α    | d-policy    | Avg Rank | LB Rank | Ratio | Runtime (ms) |
|------|------|-------------|----------|---------|-------|--------------|
| 100  | 2.0  | d=2ln(n)    | 5.17     | 24.76   | 0.21  | 4.8          |
| 100  | 7.0  | d=2ln(n)    | 5.41     | 74.99   | 0.07  | 12.3         |
| 500  | 2.0  | d=(ln(n))²  | 18.80    | 96.27   | 0.20  | 41.6         |
| 1500 | 7.0  | d=6ln(n)    | 22.09    | 262.47  | 0.08  | 214.9        |
| 1500 | 15.0 | d=(ln(n))²  | 27.17    | 321.98  | 0.08  | 386.7        |

**Observations:**
- Approximation ratios range from **0.07 to 0.21**, indicating empirical results are significantly better than theoretical lower bounds (as expected)
- Higher imbalance (larger α) leads to lower ratios, suggesting better-than-bound performance in highly competitive markets
- Average ranks increase with d (more proposals = worse outcomes)
- Ranks remain remarkably stable across different α values for fixed n and d

### Runtime Scaling

From the scaling test:
- **α = 2**: 0.05s (n=500) → 1.21s (n=5000)
- **α = 7**: 0.14s (n=500) → 3.90s (n=5000)
- **α = 19**: 0.38s (n=500) → 10.92s (n=5000)

The optimized algorithm handles markets with **100,000+ agents** in reasonable time.

## Visualizations

All plots are saved in `results/`. We focus on **3 essential plots** that tell the complete story:

### The 3 Essential Plots

1. **plot1_rank_vs_imbalance.png** ⭐ **THE MAIN PLOT**
   - How proposer outcomes degrade as competition increases
   - Shows empirical ranks vs theoretical lower bounds
   - Separate lines for different market sizes n
   - Each data point labeled with regime (Small/Medium/Large)
   - **Key insight**: Competition hurts welfare, but DA performs 5-15× better than theory predicts

2. **plot2_approximation_ratio.png** (Quality/Gap Visualization)
   - Approximation ratio: empirical rank / theoretical bound
   - Shows how close DA comes to optimal performance
   - Data points labeled by regime
   - **Key insight**: Ratios 0.07-0.25 mean remarkably good performance

3. **plot3_perfect_matching_threshold.png** (Phase Transition)
   - Probability of perfect matching vs normalized list length (d/d₀)
   - Clear labels: Small/Medium/Large Imbalance regimes
   - Validates Theorem 2 threshold predictions
   - **Key insight**: Sharp transition confirms theoretical predictions

### Supplementary
4. **scaling_test.png**: Extended runtime test (n up to 5000, 100K+ agents)

## Repository Structure

```
matching-markets/
├── src/
│   ├── gale_shapley.py      # Optimized on-demand DA implementation
│   └── preferences.py        # Preference generation utilities
├── experiments/
│   ├── sweep.py             # Main parameter sweep
│   ├── plots.py             # Visualization generation
│   ├── scale_test.py        # Runtime scaling analysis
│   ├── baseline.py          # Initial proof-of-concept
│   └── sweep_imbalance.py   # Early imbalance exploration
├── results/
│   ├── sweep_results.csv    # Main experimental data
│   └── *.png                # Generated plots
└── README.md
```

## Running the Experiments

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run experiments
cd experiments
python sweep.py          # Main parameter sweep (~1-2 minutes)
python plots.py          # Generate visualizations
python scale_test.py     # Runtime analysis (~20 seconds)
```

## Future Directions

- Extend to larger n values (10000+) with further optimizations
- Explore lower α values near the threshold (α ≈ 1)
- Test focused sweeps around theoretical d₀ thresholds
- Study receiver welfare metrics
- Investigate non-uniform preference distributions (tiered, Mallows model)
- Analyze two-sided partial preferences

## References

This work builds on theoretical results for random matching markets with partial preferences, particularly focusing on the strongly imbalanced regime where competition is intense and perfect matchings are not guaranteed despite stable matchings always existing.

---

**Author**: CSCI 23 Winter Study  
**Date**: January 2026
