#!/bin/bash
docker run --rm -ti \
    -v /Users/taylor/Documents/linc/xcp_d_test_data:/src \
    -v /Users/taylor/Documents/tsalo/xcp_d_testing/data/license.txt:/license.txt \
    -v /Users/taylor/Documents/tsalo/xcp_d/xcp_d:/usr/local/miniconda/lib/python3.10/site-packages/xcp_d \
    -e FS_LICENSE=/license.txt \
    --entrypoint python \
    pennlinc/xcp_d:unstable \
    /src/modify_for_ukbiobank.py

docker run --rm -ti \
    -v /Users/taylor/Documents/linc/xcp_d_test_data:/src \
    -v /Users/taylor/Documents/tsalo/xcp_d_testing/data/license.txt:/license.txt \
    -v /Users/taylor/Documents/tsalo/xcp_d/xcp_d:/usr/local/miniconda/lib/python3.10/site-packages/xcp_d \
    -e FS_LICENSE=/license.txt \
    --entrypoint /bin/bash \
    flywheel/fsl-anat:1.1.2_6.0.1 \
    /src/modify_for_ukbiobank_fsl.sh
