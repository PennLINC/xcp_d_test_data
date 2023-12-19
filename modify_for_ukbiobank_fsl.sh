#!/bin/bash
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
