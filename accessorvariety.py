#!/usr/bin/env python3
"""Filter ranked Chinese terms using distinct left and right contexts."""

import re
import sys

LEFT_PUNCTUATION = re.compile(r'[，。!\?\-\/\(\)\\]')
RIGHT_PUNCTUATION = re.compile(r'[，。!\?\-\/\(\)\\"]')
MIN_CONTEXTS = 3


def main(args):
    ranked_path, file_list = args
    with open(ranked_path, encoding="utf-8") as ranked:
        rows = [(line.split("\t", 1)[0], line) for line in ranked]

    pending = {term: (set(), set()) for term, _ in rows}
    accepted = set()
    with open(file_list, encoding="utf-8") as filenames:
        for filename in filenames:
            if not pending:
                break
            with open(filename.rstrip("\n"), encoding="utf-8") as document:
                words = [line.split("\t", 1)[0] for line in document]

            passed = set()
            for index, word in enumerate(words):
                if word not in pending:
                    continue
                left_contexts, right_contexts = pending[word]
                # Preserve the legacy first-row wraparound and right offset.
                width = len(word.split(" "))
                right_index = index + width - 1
                if width == 1 and index + 1 < len(words):
                    right_index = index + 1
                left = LEFT_PUNCTUATION.sub("", words[index - 1])
                right = RIGHT_PUNCTUATION.sub("", words[right_index])
                if left:
                    left_contexts.add(left)
                if right:
                    right_contexts.add(right)
                if len(left_contexts) >= MIN_CONTEXTS and len(right_contexts) >= MIN_CONTEXTS:
                    passed.add(word)

            # The legacy filter finishes the current document before stopping.
            accepted.update(passed)
            for word in passed:
                del pending[word]

    for term, line in rows:
        if term in accepted:
            print(line, end="")


if __name__ == "__main__":
    main(sys.argv[1:])
