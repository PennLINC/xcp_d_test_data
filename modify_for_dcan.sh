docker run --rm -ti \
    -v /Users/taylor/Documents/linc/xcp_d_test_data:/Users/taylor/Documents/linc/xcp_d_test_data \
    -v /Users/taylor/Documents/tsalo/xcp_d_testing/data/license.txt:/license.txt \
    -e FS_LICENSE=/license.txt \
    --entrypoint python \
    pennlinc/xcp_d:unstable \
    /Users/taylor/Documents/linc/xcp_d_test_data/modify_for_dcan.py
