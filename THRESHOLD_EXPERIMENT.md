# Threshold Search Experiment

## 🎯 Goal

Find the **minimal preference list length d*** needed for perfect matching to occur with high probability (≥ 80%).

This is **much more interesting** than our previous experiments because it directly answers:
> "What's the minimum d required for feasibility?"

---

## 🔬 Method: Binary Search with Adaptive Trials

### For each (n, α) pair:

1. **Bracketing Phase**
   - Test candidate d values: ln(n), (ln(n))², √n, n/2, n
   - Find first d where Pr(perfect) ≥ 0.8
   - Establishes bounds [d_low, d_high]

2. **Binary Search Phase**
   - Search between bounds to find minimal d*
   - Start with 10 trials per test
   - If ambiguous (0.4 ≤ rate ≤ 0.95), run 30 more trials
   - Early stopping if clearly above/below threshold

3. **Confirmation Phase**
   - Run 50 trials at d* to confirm result

4. **Warm Start**
   - Use previous n's d* to initialize bounds for next n
   - Dramatically reduces search steps

---

## 📊 Parameters

**Market Sizes:**
- n ∈ {500, 1000, 2000, 5000}

**Competition Regimes:**
- Small: α = 1.5 (m/n ≈ 2.5)
- Medium: α = 7.0 (m/n = 8)
- Large: α = 15.0 (m/n = 16)

**Target:** Pr(perfect matching) ≥ 0.8

**Total configurations:** 12 (4 n-values × 3 α-regimes)

---

## 📈 Expected Results

### Main Plot: d* vs n

**X-axis:** Market size n  
**Y-axis:** Minimal list length d*  
**Three curves:** One per α regime

**Expected behavior:**
1. d* increases with n (likely logarithmic growth)
2. Higher α → higher d* curve (more competition needs longer lists)
3. Curves should be well-separated by regime

**Reference lines on plot:**
- ln(n) - constant dashed line
- (ln(n))² - constant dotted line
- √n - constant dash-dot line

**Key questions answered:**
- Does d* grow like ln(n) or (ln(n))²?
- How much does α shift the threshold?
- Is the scaling consistent across regimes?

---

## 🚀 Why This is Better Than Previous Experiments

### Previous Experiments:
✅ Fixed d-policies (d=2ln(n), d=6ln(n), d=(ln(n))²)  
✅ Measured outcomes (rank, perfect matching rate)  
❌ All achieved 100% perfect matching (boring!)  
❌ Didn't show **where the threshold is**

### This Experiment:
✅ **Searches for the threshold**  
✅ Will show the **phase transition**  
✅ Directly comparable to Theorem 2's d₀ prediction  
✅ Shows **minimal feasibility requirements**  

---

## 🔍 What We'll Learn

1. **Minimal d* for each (n, α)**
   - Smallest d that guarantees perfect matching w.h.p.

2. **Scaling behavior**
   - How does d* grow with n?
   - Is it O(log n), O(log² n), or O(√n)?

3. **Competition effects**
   - How much does α shift the threshold?
   - Is the shift additive or multiplicative?

4. **Theory vs Practice**
   - Compare d* to theoretical d₀ from Theorem 2
   - Is the theory tight or pessimistic?

---

## 📂 Output Files

### Data:
- `results/threshold_results.csv` - All d* values and rates

### Plots:
1. **threshold_main.png** ⭐ THE MAIN RESULT
   - d* vs n curves (log-log scale)
   - One curve per α regime
   - Reference lines for comparison

2. **threshold_scaling.png** (Analysis)
   - Left: d* vs n (log-log)
   - Right: d*/n ratio vs n

3. **threshold_table.png** (Summary)
   - Clean table of all d* values
   - Color-coded by regime

---

## ⏱️ Runtime Estimate

- Small regime (α=1.5): ~5-10 minutes
- Medium regime (α=7.0): ~10-15 minutes  
- Large regime (α=15.0): ~15-20 minutes

**Total:** ~30-45 minutes for all 12 configurations

With adaptive trials and warm start, should be manageable!

---

## 🎯 Key Insight

The **threshold d*** directly tells us:
> "How much information do proposers need to guarantee everyone gets matched?"

This is the **fundamental feasibility question** for truncated preference markets!

