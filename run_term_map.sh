#!/bin/sh
set -e

# Arguments: foreground file list, ranked term list, output prefix,
# input path prefix, Termolator directory, language, optional Chinese chunk list.
if [ "${6:-}" = "zh" ]; then
    python3 "$5/run_term_map.py" "$2" "$1" "$3.term_instance_map" "$4" \
        --chinese-chunks "${7:-foreground_tchunk_list}"
else
    "$5/make_io_file.py" "$1" "$3.internal_terms_list" .terms
    if [ "${6:-}" = "fr" ]; then
        "$5/summary/term_generator.py" "$3"
    fi
    "$5/run_term_map.py" "$2" "$3.internal_terms_list" "$3.term_instance_map" "$4"
fi

grep "<term" "$3.term_instance_map" | sed 's/.*variants="//;s/".*//' > "$3.edited_term_list"
