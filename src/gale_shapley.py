import numpy as np
from collections import deque

class Proposer:
    def __init__(self, id, d, rng):
        self.id = id
        self.d = d
        self.rng = rng
        self.proposed_to = set()
        self.proposals_order = []
        self.matched_to = None
    
    def can_propose(self):
        return len(self.proposed_to) < self.d
    
    def next_receiver(self, n_receivers):
        if not self.can_propose():
            return None
        
        while True:
            r = self.rng.integers(0, n_receivers)
            if r not in self.proposed_to:
                self.proposed_to.add(r)
                self.proposals_order.append(r)
                return r

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
        
        self.proposers = [Proposer(i, d, np.random.default_rng(prop_seeds[i])) for i in range(m)]
        self.receivers = [Receiver(j, np.random.default_rng(recv_seeds[j])) for j in range(n)]
    
    def run(self):
        free_queue = deque(range(self.m))
        
        while free_queue:
            p_id = free_queue.popleft()
            p = self.proposers[p_id]
            
            r_id = p.next_receiver(self.n)
            if r_id is None:
                continue
            
            r = self.receivers[r_id]
            
            if r.matched_to is None:
                p.matched_to = r_id
                r.matched_to = p_id
            else:
                cur = r.matched_to
                if r.prefers(p_id, cur):
                    self.proposers[cur].matched_to = None
                    free_queue.append(cur)
                    p.matched_to = r_id
                    r.matched_to = p_id
                else:
                    if p.can_propose():
                        free_queue.append(p_id)
        
        return {p.id: p.matched_to for p in self.proposers if p.matched_to is not None}

