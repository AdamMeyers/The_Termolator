#!/usr/bin/env bash
set -e

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
    echo "Usage: $0 use_dictionary output_prefix foreground background termolator_dir [plain_text]" >&2
    exit 2
fi

use_dictionary=$1
prefix=$2
foreground=$3
background=$4
program_dir=$5
plain_text=${6:-False}
case "$plain_text" in
    [Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee]) ;;
    *) echo "plain_text must be True or False" >&2; exit 2 ;;
esac

work_dir=$(mktemp -d)
trap 'rm -r -- "$work_dir"' EXIT
shopt -s nullglob

prepare_corpus() {
    local input=$1 name=$2 file base
    local prepared="${prefix}_cleaned/$name"
    local -a files=("$input"/*)
    mkdir -p "$prepared" "$work_dir/cleaned/$name"
    if [ "${#files[@]}" -eq 0 ]; then
        echo "No input documents in $input" >&2
        return 1
    fi

    case "$plain_text" in
        [Ff][Aa][Ll][Ss][Ee])
            mkdir -p "$work_dir/xml/$name"
            : > "$work_dir/$name.xml.list"
            for file in "${files[@]}"; do
                if [ -f "$file" ] && [[ "$file" == *.xml ]]; then
                    base=${file##*/}
                    cp -- "$file" "$work_dir/xml/$name/$base"
                    printf '%s\n' "$work_dir/xml/$name/$base" >> "$work_dir/$name.xml.list"
                fi
            done
            python3 "$program_dir/remove_xml_chinese.py" "$work_dir/$name.xml.list" cleaned
            files=("$work_dir/xml/$name/"*cleaned.xml)
            ;;
    esac

    : > "cleaned_${name}List.txt"
    for file in "${files[@]}"; do
        [ -f "$file" ] || continue
        base=${file##*/}
        case "$plain_text" in
            [Ff][Aa][Ll][Ss][Ee]) base=${base%.xml}.txt ;;
        esac
        cp -- "$file" "$work_dir/cleaned/$name/$base"
        cp -- "$file" "$prepared/$base"
        printf '%s\n' "$prepared/$base" >> "cleaned_${name}List.txt"
    done
    if [ ! -s "cleaned_${name}List.txt" ]; then
        echo "No prepared documents in $input" >&2
        return 1
    fi
}

echo "Step 0: Preparing input"
prepare_corpus "$foreground" foreground
prepare_corpus "$background" background

echo "Step 1: Segmenting and tagging"
tagger_dir="$program_dir/Brandeis-CASIA-LanguageProcesser"
for corpus in background foreground; do
    mkdir -p "$work_dir/tagged/$corpus"
    (
        cd "$tagger_dir"
        java "-Xmx${TERMOLATOR_JAVA_HEAP:-25000m}" -cp WS_POS_brandeis.jar \
            brandeis.transition.wordseg.WordSegmentToolkit -mode test \
            -model model/train_brandeis.model.gz \
            -test "$work_dir/cleaned/$corpus/" -out "$work_dir/tagged/$corpus"
    )
done

echo "Step 2: Generating noun chunks"
python3 "$program_dir/chinese_noun_chunker_generator.py" \
    -f "$work_dir/tagged/foreground" -b "$work_dir/tagged/background" \
    -d "$use_dictionary" -p "$program_dir"

echo "Step 3: Ranking terms"
for corpus in foreground background; do
    sed 's|^\./||' "${corpus}_tchunk_list" | sort > "$prefix.internal_${corpus}_tchunk_list"
done
python3 "$program_dir/distributional_component.py" NormalRank \
    "$prefix.internal_foreground_tchunk_list" "$prefix.all_terms" False \
    "$prefix.internal_background_tchunk_list"

echo "Step 4: Filtering by Accessor Variety"
python3 "$program_dir/accessorvariety.py" "$prefix.all_terms" foreground_tchunk_list \
    > "$prefix.AV_filtered_terms"
cut -f 1 "$prefix.AV_filtered_terms" > "$prefix.out_term_list"
