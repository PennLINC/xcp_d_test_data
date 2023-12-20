#!/bin/bash
cd /src/data/work/ukbiobank/

# FLIRT T1w-space boldref image to T1w space,
# because fMRIPrep derivatives are in T1w *world* space,
# but not same voxel space, and FSL can't handle that.
flirt \
    -in /src/data/work/ukbiobank/example_func.nii.gz \
    -ref /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -omat /src/data/work/ukbiobank/ignore_func2highres.mat \
    -out /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/example_func.nii.gz \
    -interp trilinear

# Apply mat to get T1w-space BOLD into T1w space
flirt \
    -in /src/data/work/ukbiobank/filtered_func_data_clean.nii.gz \
    -ref /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -applyxfm \
    -init /src/data/work/ukbiobank/ignore_func2highres.mat \
    -out /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/filtered_func_data_clean.nii.gz \
    -interp trilinear

# Apply mat to get T1w-space BOLD brain mask into T1w space
flirt \
    -in /src/data/work/ukbiobank/mask.nii.gz \
    -ref /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -applyxfm \
    -init /src/data/work/ukbiobank/ignore_func2highres.mat \
    -out /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/mask.nii.gz \
    -interp nearestneighbour

cd /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/
# FLIRT T1w-space T1w image to MNI152NLin6Asym-2mm
flirt \
    -in /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -ref /src/data/MNI152_T1_2mm.nii.gz \
    -omat /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/example_func2standard.mat \
    -interp spline

# FNIRT T1w-space T1w image to MNI152NLin6Asym-2mm
fnirt \
    --in=/src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    --ref=/src/data/MNI152_T1_2mm.nii.gz \
    --aff=/src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/example_func2standard.mat \
    --fout=/src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/example_func2standard_warp.nii.gz \
    --interp=spline
