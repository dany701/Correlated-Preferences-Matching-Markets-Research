# Matching Markets: Random Matching Markets Baseline

**CSCI 23 Winter Study Independent Project**

## Overview

This project extends the work of Potukuchi & Singh (2024) by investigating the behavior of stable matching markets under various preference correlation structures. The baseline implementation uses uniform random preferences to establish benchmark statistics for proposer-optimal outcomes. Future work will explore tiered and Mallows preference models to understand how correlation affects perfect matching rates and rank distributions.

## Current Status

- ✓ Gale–Shapley algorithm implemented with support for balanced and unbalanced markets
- ✓ Uniform random preference generator with reproducible seeding
- ✓ Baseline experiment runner with 300 trials (N=100, M=100)
- ✓ Stability verification on small test cases
- ✓ Histogram visualization of proposer rank distribution

## How to Run

1. Activate the virtual environment (already created):

```bash
source venv/bin/activate
```

2. Install dependencies (if needed):

```bash
pip install -r requirements.txt
```

3. Run the baseline experiment:

```bash
cd experiments
python baseline.py
```

Or from the project root:

```bash
source venv/bin/activate && python experiments/baseline.py
```

This will:
- Execute 300 trials with uniform random preferences
- Print summary statistics (mean rank, perfect matching rate)
- Generate `results/baseline_plot.png` showing the proposer rank distribution

## Next Steps

- Implement tiered preference models (high/low tier partitions)
- Add Mallows model generator for correlated preferences
- Parameter sweeps across market sizes (N) and imbalance ratios (N/M)
- Compare perfect matching behavior across preference structures
- Analyze receiver-side outcomes and welfare metrics

