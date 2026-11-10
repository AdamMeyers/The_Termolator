#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

from get_term_maps import get_term_maps, read_in_term_line


def chinese_term_groups(source_list, chunk_list, input_prefix):
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
        def source_groups():
            return chinese_term_groups(options.file_list, options.chinese_chunks, options.input_file_path)

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
