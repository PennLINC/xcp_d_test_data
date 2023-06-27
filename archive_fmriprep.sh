find data/fmriprep-reduced -name '.DS_Store' -type f -delete
tar -C data/fmriprep-reduced -czf data/pnc_fmriprep.tar.gz .
