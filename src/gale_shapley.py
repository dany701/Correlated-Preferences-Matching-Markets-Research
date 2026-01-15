import numpy as np
from collections import deque

class Proposer:
    def __init__(self, id, d, n_receivers, rng):
        self.id = id
        self.d = min(d, n_receivers)  # can't propose to more than n receivers
        # PRE-GENERATE all d preferences at initialization (much faster!)
        self.preference_list = rng.choice(n_receivers, size=self.d, replace=False)
        self.next_proposal_idx = 0
        self.matched_to = None
    
    def can_propose(self):
        return self.next_proposal_idx < self.d
    
    def next_receiver(self):
        if not self.can_propose():
            return None
        r = int(self.preference_list[self.next_proposal_idx])
        self.next_proposal_idx += 1
        return r
    
    def get_rank(self, r_id):
        """Get rank of matched receiver (1-indexed)"""
        # Find position in preference list
        return int(np.where(self.preference_list == r_id)[0][0]) + 1

class Receiver:
    def __init__(self, id, rng):
        self.id = id
        self.rng = rng
        self.matched_to = None
        self.scores = {}
    
    def score_for(self, p_id):
        if p_id not in self.scores:
            self.scores[p_id] = self.rng.random()
        return self.scores[p_id]
    
    def prefers(self, new_p, cur_p):
        return self.score_for(new_p) < self.score_for(cur_p)

class DeferredAcceptanceMarket:
    def __init__(self, m, n, d, seed=0):
        self.m = m
        self.n = n
        self.d = d
        self.seed = seed
        
        # seed splitting for reproducibility
        master_rng = np.random.default_rng(seed)
        prop_seeds = master_rng.integers(0, 2**31, size=m)
        recv_seeds = master_rng.integers(0, 2**31, size=n)
        
        self.proposers = [Proposer(i, d, n, np.random.default_rng(prop_seeds[i])) for i in range(m)]
        self.receivers = [Receiver(j, np.random.default_rng(recv_seeds[j])) for j in range(n)]
    
    def run(self):
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

