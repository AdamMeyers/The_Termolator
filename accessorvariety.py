#!/usr/bin/env python3
"""Filter ranked Chinese terms using distinct left and right contexts."""

import re
import sys

from chinese_term_matching import candidate_index, candidate_spans

LEFT_PUNCTUATION = re.compile(r'[，。!\?\-\/\(\)\\]')
RIGHT_PUNCTUATION = re.compile(r'[，。!\?\-\/\(\)\\"]')
MIN_CONTEXTS = 3


def main(args):
    ranked_path, file_list = args
    with open(ranked_path, encoding="utf-8-sig") as ranked:
        rows = [(line.split("\t", 1)[0].lower(), line) for line in ranked]
    candidates = {term for term, _ in rows}
    lengths = candidate_index(candidates)
    pending = {term: (set(), set()) for term in candidates}

    with open(file_list, encoding="utf-8") as filenames:
        for filename in filenames:
            if not pending:
                break
            with open(filename.rstrip("\n"), encoding="utf-8") as document:
                words = [line.rstrip("\n").split("\t", 1)[0] for line in document]

            for term, start, end in candidate_spans(words, lengths, pending):
                left_contexts, right_contexts = pending[term]
                if start:
                    left = LEFT_PUNCTUATION.sub("", words[start - 1])
                    if left:
                        left_contexts.add(left)
                if end < len(words):
                    right = RIGHT_PUNCTUATION.sub("", words[end])
                    if right:
                        right_contexts.add(right)
                if len(left_contexts) >= MIN_CONTEXTS and len(right_contexts) >= MIN_CONTEXTS:
                    del pending[term]

    for term, line in rows:
        if term not in pending:
            print(line, end="")


if __name__ == "__main__":
    main(sys.argv[1:])
