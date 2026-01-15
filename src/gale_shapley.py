import numpy as np
from collections import deque
from typing import Dict, Optional

class Proposer:
    """Proposer agent with truncated preference list of length d.
    
    Preferences are pre-sampled at initialization for efficiency.
    """
    def __init__(self, id: int, d: int, n_receivers: int, rng: np.random.Generator):
        self.id: int = id
        self.d: int = min(d, n_receivers)  # can't propose to more than n receivers
        # PRE-GENERATE all d preferences at initialization (much faster!)
        self.preference_list: np.ndarray = rng.choice(n_receivers, size=self.d, replace=False)
        self.next_proposal_idx: int = 0
        self.matched_to: Optional[int] = None
    
    def can_propose(self) -> bool:
        """Check if proposer has more receivers to propose to."""
        return self.next_proposal_idx < self.d
    
    def next_receiver(self) -> Optional[int]:
        """Get next receiver to propose to, or None if exhausted."""
        if not self.can_propose():
            return None
        r = int(self.preference_list[self.next_proposal_idx])
        self.next_proposal_idx += 1
        return r
    
    def get_rank(self, r_id: int) -> int:
        """Get rank of matched receiver (1-indexed).
        
        Args:
            r_id: Receiver ID
            
        Returns:
            Rank (1 = most preferred, d = least preferred in list)
        """
        return int(np.where(self.preference_list == r_id)[0][0]) + 1

class Receiver:
    """Receiver agent with i.i.d. uniform preferences generated on-demand.
    
    Preferences are represented as random scores in [0,1) with lower scores
    meaning higher preference. Scores are cached for consistency.
    """
    def __init__(self, id: int, rng: np.random.Generator):
        self.id: int = id
        self.rng: np.random.Generator = rng
        self.matched_to: Optional[int] = None
        self.scores: Dict[int, float] = {}
    
    def score_for(self, p_id: int) -> float:
        """Get preference score for proposer (generated on-demand, then cached)."""
        if p_id not in self.scores:
            self.scores[p_id] = self.rng.random()
        return self.scores[p_id]
    
    def prefers(self, new_p: int, cur_p: int) -> bool:
        """Check if receiver prefers new_p over cur_p (lower score = higher preference)."""
        return self.score_for(new_p) < self.score_for(cur_p)

class DeferredAcceptanceMarket:
    """Deferred Acceptance market with m proposers, n receivers, and truncated lists of length d.
    
    Implements proposer-proposing Gale-Shapley algorithm with:
    - Proposers: truncated preferences (length d), pre-sampled
    - Receivers: full preferences, i.i.d. uniform, generated on-demand
    
    Args:
        m: Number of proposers (long side)
        n: Number of receivers (short side)
        d: Length of proposer preference lists
        seed: Random seed for reproducibility
    """
    def __init__(self, m: int, n: int, d: int, seed: int = 0):
        self.m: int = m
        self.n: int = n
        self.d: int = d
        self.seed: int = seed
        
        # seed splitting for reproducibility
        master_rng = np.random.default_rng(seed)
        prop_seeds = master_rng.integers(0, 2**31, size=m)
        recv_seeds = master_rng.integers(0, 2**31, size=n)
        
        self.proposers = [Proposer(i, d, n, np.random.default_rng(prop_seeds[i])) for i in range(m)]
        self.receivers = [Receiver(j, np.random.default_rng(recv_seeds[j])) for j in range(n)]
    
    def run(self) -> Dict[int, int]:
        """Run proposer-proposing Deferred Acceptance algorithm.
        
        Returns:
            Dict mapping proposer IDs to matched receiver IDs (only matched proposers included)
        """
        free_queue = deque(range(self.m))
        proposers = self.proposers  # local reference for speed
        receivers = self.receivers  # local reference for speed
        
        while free_queue:
            p_id = free_queue.popleft()
            p = proposers[p_id]
            
            r_id = p.next_receiver()
            if r_id is None:
                continue
            
            r = receivers[r_id]
            
            if r.matched_to is None:
                p.matched_to = r_id
                r.matched_to = p_id
            else:
                cur = r.matched_to
                if r.prefers(p_id, cur):
                    proposers[cur].matched_to = None
                    free_queue.append(cur)
                    p.matched_to = r_id
                    r.matched_to = p_id
                else:
                    if p.can_propose():
                        free_queue.append(p_id)
        
        # Build result dict more efficiently
        return {p.id: p.matched_to for p in proposers if p.matched_to is not None}

