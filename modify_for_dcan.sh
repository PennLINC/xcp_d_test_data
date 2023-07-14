docker run --rm -ti \
    -v /Users/taylor/Documents/linc/xcp_d_test_data:/Users/taylor/Documents/linc/xcp_d_test_data \
    --entrypoint "python /Users/taylor/Documents/linc/xcp_d_test_data/modify_for_dcan.py" \
    pennlinc/xcp_d:unstable
