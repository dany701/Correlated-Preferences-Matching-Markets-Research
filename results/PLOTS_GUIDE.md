# Visualization Guide

## Overview
All visualizations are generated from 27 experimental configurations:
- n ∈ {100, 500, 1500} (market sizes)
- α ∈ {2.0, 7.0, 15.0} (imbalance levels)
- d-policies: log_c2, log_c6, logsq_c1.0

---

## Main Results

### 1. baseline_rank_distribution.png
**What it shows:** Histogram of average proposer ranks across ALL 27 configurations, one panel per d-policy.

**Key insight:** 
- Shows the full distribution of ranks (not just mean)
- Red dashed line = mean rank for that policy
- Text box shows: mean, std deviation, and sample size (N=9 configurations per policy)
- X-axis aligned across all three histograms for easy comparison

**Interpretation:** 
- Lower ranks = better proposer welfare
- Narrow distributions = consistent performance across different (n, α)
- log_c2 has lowest ranks (best welfare) but most variation

---

### 2. rank_vs_lower_bound.png  
**What it shows:** Side-by-side comparison of empirical ranks vs theoretical lower bounds for each configuration.

**Key insight:**
- Gray bars = theoretical minimum (lower bound)
- Colored bars = actual empirical results
- Shows how close we are to theoretical optimum

**Interpretation:** Empirical ranks are significantly better (lower) than theoretical bounds, especially for higher imbalance.

---

### 3. approximation_ratio_heatmap.png
**What it shows:** Heatmaps of empirical_rank / lower_bound_rank across (n, α) space.

**Key insight:**
- Lower ratios (darker yellow) = closer to theoretical bound
- Shows how ratio changes with market size and competition

**Interpretation:** Ratios range 0.07-0.21, meaning empirical results are 5-15x better than theoretical worst case.

---

## Detailed Analysis

### 4. rank_by_imbalance.png
**What it shows:** How average rank changes as imbalance (α) increases, for each market size.

**Key insight:**
- Shows effect of competition on proposer welfare
- Different policies show different sensitivities

**Interpretation:** Rank stays relatively stable across α for fixed d-policy, but grows with d.

---

### 5. perfect_matching_summary.png
**What it shows:** 
- Left: Perfect matching rate by policy (averaged)
- Right: Perfect matching rate heatmap across (n, α)

**Key insight:**
- All configurations achieved 100% perfect matching
- Chosen d-policies are sufficient for this parameter regime

**Interpretation:** These markets always have perfect stable matchings.

---

### 6. runtime_analysis.png
**What it shows:**
- Left: Runtime vs market size n (log-log scale)
- Right: Runtime vs imbalance α

**Key insight:**
- Runtime scales super-linearly with n (as expected: O(m·d))
- Runtime increases with α (more proposers to process)

**Interpretation:** Algorithm remains efficient even for n=1500, α=15 (24K proposers).

---

### 7. scaling_test.png
**What it shows:** Extended scaling test up to n=5000 for three imbalance levels.

**Key insight:**
- Runtime grows to ~11s for largest markets (100K proposers)
- Ranks grow logarithmically with n
- Higher imbalance = longer runtime but similar rank patterns

**Interpretation:** Algorithm can handle very large markets with acceptable runtime.

---

## Policy Definitions

The three d-policies determine how long each proposer's preference list is:

- **d=2ln(n)** - Short lists, proposers match quickly (lower ranks)
- **d=6ln(n)** - Longer lists, more proposals before matching (higher ranks)  
- **d=(ln(n))²** - Quadratic growth in ln(n), between the two log policies

Where:
- **n** = number of receivers (short side of market)
- **d** = length of each proposer's preference list

## Color Scheme
- **Blue (#2E86AB)**: d=2ln(n) policy
- **Purple (#A23B72)**: d=6ln(n) policy  
- **Orange (#F18F01)**: d=(ln(n))² policy

## Imbalance Regimes (background shading where shown)
- **Green**: Small imbalance (α ∈ [0-3])
- **Yellow**: Medium imbalance (α ∈ [4-8])
- **Red**: Large imbalance (α ∈ [11-20])
