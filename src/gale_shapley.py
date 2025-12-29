
def gale_shapley(proposers_prefs, receivers_prefs):
    """
    run proposer-optimal gale-shapley deferred acceptance.

    parameters
    ----------
    proposers_prefs : list[list[int]]
        for each proposer i, a list of receiver indices ordered from most
        to least preferred.
    receivers_prefs : list[list[int]]
        for each receiver j, a list of proposer indices ordered from most
        to least preferred.

    returns
    -------
    dict[int, int]
        a mapping proposer -> receiver for all matched proposers.
        in unbalanced markets, some agents may remain unmatched.
    """
    n_proposers = len(proposers_prefs)
    n_receivers = len(receivers_prefs)

    # precompute receiver rankings: rank[receiver][proposer] = priority (lower is better)
    receiver_rank = []
    for r in range(n_receivers):
        ranking = {p: rank for rank, p in enumerate(receivers_prefs[r])}
        receiver_rank.append(ranking)

    # state
    free_proposers = list(range(n_proposers))
    next_proposal_index = [0] * n_proposers
    receiver_match = {}  # receiver -> proposer

    # main loop: continue while there exists a free proposer with options left
    while free_proposers:
        p = free_proposers.pop()
        prefs = proposers_prefs[p]

        # skip proposers who have exhausted all receivers
        if next_proposal_index[p] >= len(prefs):
            continue

        r = prefs[next_proposal_index[p]]
        next_proposal_index[p] += 1

        # if receiver index is out of market range, treat as invalid and continue
        if r < 0 or r >= n_receivers:
            continue

        if r not in receiver_match:
            # receiver is free: match immediately
            receiver_match[r] = p
        else:
            # receiver currently matched, decide whether to switch
            current_p = receiver_match[r]
            # if receiver has not ranked one of the proposers (e.g. truncated list),
            # treat missing entry as worst possible rank.
            current_rank = receiver_rank[r].get(current_p, float("inf"))
            new_rank = receiver_rank[r].get(p, float("inf"))

            if new_rank < current_rank:
                # receiver prefers new proposer
                receiver_match[r] = p
                # old proposer becomes free again if they still have options
                if next_proposal_index[current_p] < len(proposers_prefs[current_p]):
                    free_proposers.append(current_p)
            else:
                # receiver keeps current match; proposer remains free if they have options left
                if next_proposal_index[p] < len(prefs):
                    free_proposers.append(p)

    # build proposer -> receiver mapping
    proposer_match = {}
    for r, p in receiver_match.items():
        proposer_match[p] = r

    return proposer_match


def is_stable_matching(proposers_prefs, receivers_prefs, matching):
    """
    Check stability of a matching for diagnostic/toy tests.

    Returns True if no blocking pair exists.
    """
    n_proposers = len(proposers_prefs)
    n_receivers = len(receivers_prefs)

    # precompute receiver rankings
    receiver_rank = []
    for r in range(n_receivers):
        ranking = {p: rank for rank, p in enumerate(receivers_prefs[r])}
        receiver_rank.append(ranking)

    # for each proposer, check whether there exists a receiver that both sides prefer
    for p in range(n_proposers):
        prefs_p = proposers_prefs[p]
        # current match (or None if unmatched)
        current_r = matching.get(p, None)
        # rank of current match (higher index = worse; unmatched = infinity)
        if current_r is None:
            current_rank_p = float("inf")
        else:
            current_rank_p = prefs_p.index(current_r)

        for better_r in prefs_p:
            # stop once we reach receivers that are not strictly preferred
            if prefs_p.index(better_r) >= current_rank_p:
                break

            if better_r < 0 or better_r >= n_receivers:
                continue

            # check if receiver better_r prefers p to its current partner
            current_p_for_r = None
            for prop, rec in matching.items():
                if rec == better_r:
                    current_p_for_r = prop
                    break

            ranking_r = receiver_rank[better_r]
            rank_p = ranking_r.get(p, float("inf"))
            rank_current = ranking_r.get(current_p_for_r, float("inf"))

            if rank_p < rank_current:
                # blocking pair found
                return False
    return True


def _run_toy_tests():
    # 1) balanced toy example n=3
    proposers_prefs = [
        [0, 1, 2],
        [0, 1, 2],
        [0, 1, 2],
    ]
    receivers_prefs = [
        [0, 1, 2],
        [1, 0, 2],
        [2, 1, 0],
    ]
    m = gale_shapley(proposers_prefs, receivers_prefs)
    assert len(m) == 3
    assert is_stable_matching(proposers_prefs, receivers_prefs, m)

    # 2) unbalanced case: 3 proposers, 2 receivers
    proposers_prefs = [
        [0, 1],
        [0, 1],
        [0, 1],
    ]
    receivers_prefs = [
        [0, 1, 2],
        [1, 0, 2],
    ]
    m = gale_shapley(proposers_prefs, receivers_prefs)
    # at most 2 matches since only 2 receivers
    assert len(m) <= 2
    assert is_stable_matching(proposers_prefs, receivers_prefs, m)

    # 3) manual stability check on a small instance
    proposers_prefs = [
        [1, 0],
        [1, 0],
    ]
    receivers_prefs = [
        [1, 0],
        [0, 1],
    ]
    m = gale_shapley(proposers_prefs, receivers_prefs)
    assert is_stable_matching(proposers_prefs, receivers_prefs, m)

    print("✓ All Gale-Shapley toy tests passed.")


if __name__ == "__main__":
    _run_toy_tests()

