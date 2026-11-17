#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from chinese_term_matching import candidate_index, candidate_spans
from get_term_maps import get_term_maps, read_in_term_line


def phrase_occurrences(source, chunk, phrases, lengths):
    with chunk.open(encoding="utf-8") as chunks:
        tokens = [line.rstrip("\n").split("\t", 1)[0] for line in chunks]
    spans = list(candidate_spans(tokens, lengths, phrases))
    if not spans:
        return {}

    # The segmenter preserves non-whitespace characters. Refuse to report
    # misleading offsets if the chunk file belongs to different source text.
    text = source.read_text(encoding="utf-8")
    offsets = [i for i, char in enumerate(text) if not char.isspace()]
    if "".join(text[i] for i in offsets) != "".join(tokens):
        raise ValueError(f"Cannot align foreground chunk {chunk} with {source}")

    boundaries = [0]
    for token in tokens:
        boundaries.append(boundaries[-1] + len(token))
    occurrences = {}
    for term, start, end in spans:
        position = (offsets[boundaries[start]], offsets[boundaries[end] - 1])
        occurrences.setdefault(term, []).append(position)
    return occurrences


def chinese_term_groups(source_list, chunk_list, input_prefix, phrases, lengths):
    from summary.term_generator import occurrence_groups, term_attributes

    chunk_paths = {}
    with open(chunk_list, encoding="utf-8") as chunks:
        for line in chunks:
            path = Path(line.strip())
            if not path.name:
                continue
            if path.name in chunk_paths and chunk_paths[path.name] != path:
                raise ValueError(f"Ambiguous foreground chunk basename: {path.name}")
            chunk_paths[path.name] = path
    with open(source_list, encoding="utf-8") as sources:
        for line in sources:
            source = Path(line.strip())
            if not source.name:
                continue
            if not source.is_absolute():
                prefixed_source = Path(input_prefix) / source
                if prefixed_source.is_file() or not source.is_file():
                    source = prefixed_source
            chunk = chunk_paths.get(source.name + ".tchunk")
            if chunk is None:
                raise ValueError(f"No foreground chunk for {source}")
            document = os.path.splitext(os.path.relpath(source, input_prefix))[0]

            def groups():
                parsed = {}
                for word, positions in occurrence_groups(source, chunk):
                    if word not in parsed:
                        parsed[word] = read_in_term_line(term_attributes(word, len(positions)).lower())
                    yield parsed[word], positions

                if phrases:
                    for term, positions in phrase_occurrences(source, chunk, phrases, lengths).items():
                        yield {"string": term, "lemma": term, "whole_only": True}, positions

            yield document, groups()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("term_list")
    parser.add_argument("file_list")
    parser.add_argument("term_map")
    parser.add_argument("input_file_path")
    parser.add_argument("--chinese-chunks")
    options = parser.parse_args(args[1:])

    if options.chinese_chunks:
        with open(options.term_list, encoding="utf-8-sig") as ranked:
            phrases = {form.lower() for line in ranked for form in line.rstrip("\n").split("\t")
                       if len(form.split()) > 1}
        lengths = candidate_index(phrases)

        def source_groups():
            return chinese_term_groups(options.file_list, options.chinese_chunks,
                                       options.input_file_path, phrases, lengths)

        destination = Path(options.term_map)
        with NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            get_term_maps(options.term_list, None, temporary_path, options.input_file_path,
                          source_groups=source_groups)
            temporary_path.replace(destination)
        finally:
            temporary_path.unlink(missing_ok=True)
    elif os.path.isfile(options.term_list) and not os.path.isfile(options.term_map):
        get_term_maps(options.term_list, options.file_list, options.term_map, options.input_file_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
