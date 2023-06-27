docker run --rm -u $(id -u) \
    -v /Users/taylor/Documents/linc/xcp_d_test_data/data:/bids-input:rw \
    -v /Users/taylor/Documents/tsalo/xcp_d/xcp_d:/usr/local/miniconda/lib/python3.8/site-packages/xcp_d \
    -v /Users/taylor/Documents/tsalo/xcp_d_testing/data/license.txt:/license.txt \
    --env FS_LICENSE=/license.txt \
    pennlinc/xcp_d:unstable \
    /bids-input/fmriprep-reduced \
    /bids-input/derivatives \
    participant \
    --input-type fmriprep \
    -w /bids-input/work \
    --participant_label 1648798153 \
    --dummy-scans auto \
    --head-radius auto \
    --warp-surfaces-native2std \
    --cifti \
    --motion-filter-type notch \
    --band-stop-min 12 \
    --band-stop-max 18 \
    --mem-gb 4 \
    --nthreads 1 \
    -v
