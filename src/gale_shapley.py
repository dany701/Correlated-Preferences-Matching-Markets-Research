def gale_shapley(proposers_prefs, receivers_prefs):
    n = len(proposers_prefs)
    m = len(receivers_prefs)
    
    # precompute ranks for efficiency
    recv_rank = []
    for r in range(m):
        recv_rank.append({p: rank for rank, p in enumerate(receivers_prefs[r])})
    
    free = list(range(n))
    next_prop = [0] * n
    recv_match = {}
    
    while free:
        p = free.pop()
        if next_prop[p] >= len(proposers_prefs[p]):
            continue
            
        r = proposers_prefs[p][next_prop[p]]
        next_prop[p] += 1
        
        if r not in recv_match:
            recv_match[r] = p
        else:
            curr = recv_match[r]
            if recv_rank[r].get(p, float('inf')) < recv_rank[r].get(curr, float('inf')):
                recv_match[r] = p
                if next_prop[curr] < len(proposers_prefs[curr]):
                    free.append(curr)
            else:
                if next_prop[p] < len(proposers_prefs[p]):
                    free.append(p)
    
    return {p: r for r, p in recv_match.items()}


if __name__ == "__main__":
    # quick test
    props = [[0, 1], [1, 0]]
    recvs = [[1, 0], [0, 1]]
    m = gale_shapley(props, recvs)
    print(f"test matching: {m}")

