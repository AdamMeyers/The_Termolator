"""Match ranked Chinese terms against contiguous chunk tokens."""

from collections import defaultdict


def candidate_index(terms):
    by_first = defaultdict(set)
    for term in terms:
        tokens = term.lower().split()
        if tokens:
            by_first[tokens[0]].add(len(tokens))
    return {first: tuple(sorted(lengths)) for first, lengths in by_first.items()}


def candidate_spans(words, lengths_by_first, terms):
    """Yield (ranked term, first token, exclusive end token)."""
    normalized = [word.lower() for word in words]
    for start, first in enumerate(normalized):
        for length in lengths_by_first.get(first, ()):
            end = start + length
            if end > len(normalized):
                break
            term = " ".join(normalized[start:end])
            if term in terms:
                yield term, start, end
