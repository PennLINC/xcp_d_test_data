anat_dir=/Users/taylor/Documents/linc/xcp_d_test_data/data/fmriprep-reduced/sub-1648798153/ses-PNC1/anat
out_dir=/Users/taylor/Documents/linc/xcp_d_test_data/data/derivatives/xcp_d/sub-1648798153/ses-PNC1/anat
dcan_dir=/Users/taylor/Documents/linc/xcp_d_test_data/data/derivatives/dcan/sub-1648798153/ses-PNC1/files/MNINonLinear/fsaverage_LR32k
hcp_dir=/Users/taylor/Documents/linc/xcp_d_test_data/data/derivatives/hcp/sub-1648798153/ses-PNC1/files/MNINonLinear/fsaverage_LR32k

for label in CORTEX_LEFT CORTEX_RIGHT
do
    for metric in curv sulc thickness
    do
        hemi=${label:7:1}
        wb_command -cifti-separate \
            ${anat_dir}/sub-1648798153_ses-PNC1_acq-refaced_space-fsLR_den-91k_curv.dscalar.nii \
            COLUMN \
            -metric $label \
            ${out_dir}/sub-1648798153_ses-PNC1_acq-refaced_space-fsLR_den-32k_hemi-${hemi}_${metric}.shape.gii

        if [ "$metric" = "curv" ];
        then
            suffix=curvature
        else
            suffix=$metric
        fi
        cp ${out_dir}/sub-1648798153_ses-PNC1_acq-refaced_space-fsLR_den-32k_hemi-${hemi}_${metric}.shape.gii \
            ${dcan_dir}/1648798153.${hemi}.${suffix}.32k_fs_LR.shape.gii
        cp ${out_dir}/sub-1648798153_ses-PNC1_acq-refaced_space-fsLR_den-32k_hemi-${hemi}_${metric}.shape.gii \
            ${hcp_dir}/1648798153.${hemi}.${suffix}.32k_fs_LR.shape.gii
    done
done

docker run --rm -ti \
    -v /Users/taylor/Documents/linc/xcp_d_test_data:/Users/taylor/Documents/linc/xcp_d_test_data \
    -v /Users/taylor/Documents/tsalo/xcp_d_testing/data/license.txt:/license.txt \
    -e FS_LICENSE=/license.txt \
    --entrypoint python \
    pennlinc/xcp_d:unstable \
    /Users/taylor/Documents/linc/xcp_d_test_data/modify_for_dcan.py
