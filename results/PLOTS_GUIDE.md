# Visualization Guide: Three Questions, Three Figures

## 📊 The Complete Story

This study answers **three core research questions** about strongly imbalanced matching markets:

1. **FEASIBILITY:** At what list length d* does perfect matching emerge?
2. **QUALITY:** How do proposer ranks degrade with competition?
3. **SCALING:** How does runtime grow with market size?

Each question has **one dedicated figure** that tells a clear, focused story.

---

## Figure 1: FEASIBILITY — Threshold for Perfect Matching

**File:** `figure1_feasibility.png`

### The Question
> What is the minimal preference list length d* required for all receivers to be matched with high probability (≥80%)?

### What It Shows
- **X-axis:** Market size n (log scale)
- **Y-axis:** Minimal list length d* (log scale)
- **Three curves:** One per competition regime (Small/Medium/Large imbalance)
- **Reference lines:** ln(n), (ln(n))² for comparison

### Key Finding
**Counterintuitive result:** Higher competition → Lower d* needed!

```
Small imbalance (α=1.5):  d* ≈ 4-5
Medium imbalance (α=7.0): d* ≈ 1-2  
Large imbalance (α=15.0): d* ≈ 1
```

### Why This Makes Sense
**Probabilistic coverage:** With 16 proposers per receiver (α=15), even if each only knows 1 receiver, coverage is excellent. With only 2.5 proposers per receiver (α=1.5), each needs to know 4-5 receivers to ensure everyone is discovered.

### Methodology
- Binary search to find threshold d* where P(perfect matching) ≥ 0.8
- Adaptive trials (10-100 per test)
- Warm start across n values for efficiency

---

## Figure 2: QUALITY — Rank Degradation with Competition

**File:** `figure2_quality.png`

### The Question
> How do proposer outcomes degrade as competition increases, and how close are they to the theoretical worst case?

### What It Shows
- **Three subplots:** One per d-policy (d=2ln(n), d=6ln(n), d=(ln(n))²)
- **X-axis:** Imbalance α = m/n - 1
- **Y-axis:** Average proposer rank
- **Colored lines:** Different market sizes n (solid = empirical, dashed = theoretical bound)
- **Background shading:** Competition regimes (green/orange/red)

### Key Findings

1. **Rank increases with competition** — but only moderately
   - α=2 (Small): rank ≈ 5-7
   - α=15 (Large): rank ≈ 7-8
   - Even 5× more proposers only adds 2-3 ranks!

2. **Empirical >> Theoretical bound** (huge gap)
   - Empirical ranks are **5-15× better** than theory predicts
   - Gap shows Deferred Acceptance performs remarkably well
   - Theory is very pessimistic

3. **d-policy matters more than α**
   - Longer lists (d=6ln(n)) → worse ranks
   - Effect of list length dominates effect of competition

### Interpretation
The **solid/dashed gap** is the whole point — it shows how much better DA performs than the theoretical lower bound. Lower is better for proposers, and empirical stays low even as theory predicts disaster.

---

## Figure 3: SCALING — Runtime Growth with Market Size

**File:** `figure3_scaling.png`

### The Question
> How does algorithm runtime grow as markets get larger, and is it feasible for real-world sizes?

### What It Shows
- **X-axis:** Market size n (log scale)  
- **Y-axis:** Runtime in seconds (log scale)
- **Three curves:** One per competition regime
- **Reference lines:** O(n), O(n log n) for comparison

### Key Findings

1. **Scales approximately O(m·d)** as expected
   - Algorithm is efficient
   - Log-log plot shows super-linear but manageable growth

2. **Feasible for large markets**
   - n=5000, α=19 → 80,000 total agents → 10.9 seconds
   - n=1000, α=7 → 8,000 total agents → 0.4 seconds

3. **Competition affects runtime**
   - Higher α → longer runtime (more proposers to process)
   - But effect is linear in m

### Practical Implications
The algorithm can handle **real-world scale markets** (thousands of participants) in reasonable time. Even with extreme competition (α=19), runtime stays under 12 seconds for n=5000.

---

## Design Principles

### Consistent Styling
**Color scheme (used across all figures):**
- 🔵 **Small imbalance:** Blue (#2E86AB)
- 🟠 **Medium imbalance:** Orange (#F18F01)
- 🔴 **Large imbalance:** Red (#C73E1D)

**Typography:**
- Title: 14pt bold
- Axes: 11-13pt bold
- Legends: 8-11pt

**Layout:**
- Log scales where appropriate (Figure 1, Figure 3)
- Grid lines for readability (dotted, alpha=0.3)
- Reference lines for context (dashed/dotted, gray)

### Why These Three?
Each figure answers a **distinct, essential question** that cannot be answered by the others:
1. Figure 1: Minimum requirements (feasibility)
2. Figure 2: Performance quality (welfare)
3. Figure 3: Computational cost (practicality)

Together they provide a **complete picture** of strongly imbalanced matching markets.

---

## Summary Table: d* Values

From Figure 1 (Feasibility):

| n    | α=1.5<br/>(Small) | α=7.0<br/>(Medium) | α=15.0<br/>(Large) |
|------|-------------------|---------------------|---------------------|
| 500  | 4                 | 1                   | 1                   |
| 1000 | 5                 | 2                   | 1                   |
| 2000 | 5                 | 2                   | 1                   |
| 5000 | 5                 | 2                   | 1                   |

**Observation:** d* barely grows with n, and actually **decreases** with α!

---

## Data Sources

- **Figure 1:** `threshold_results.csv` (threshold search experiment)
- **Figure 2:** `sweep_results.csv` (main parameter sweep)
- **Figure 3:** Scaling test data (from `scale_test.py`)

All experiments use:
- i.i.d. uniform preferences (on-demand generation)
- Proposer-proposing Deferred Acceptance
- Reproducible seeds
- Optimized implementation (pre-sampled proposer lists)

---

## How to Regenerate

```bash
cd experiments

# Generate all three figures
python plot_consolidated.py

# Or generate individual experiments' data first:
python threshold_search.py  # For Figure 1 data
python sweep.py             # For Figure 2 data
python scale_test.py        # For Figure 3 data
```

All figures save to `results/` with self-documenting names.
