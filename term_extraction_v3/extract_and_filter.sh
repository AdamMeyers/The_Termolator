NYU_TERM_SYS_DIR=.
NYU_TERM_FILTER_CUTOFF=0.5
FULL_ABBREV_DICT=${NYU_TERM_SYS_DIR}/bio-cs-full-abbrev.dict
ABBREV_FULL_DICT=${NYU_TERM_SYS_DIR}/bio-cs-abbrev-full.dict
${NYU_TERM_SYS_DIR}/main.py $1 $2 -d $3 > $3/output.txt
${NYU_TERM_SYS_DIR}/run_make_term_dict.py $3/output.txt $3/output.accept $3/output.reject ${ABBREV_FULL_DICT} ${FULL_ABBREV_DICT} ${NYU_TERM_FILTER_CUTOFF} true
