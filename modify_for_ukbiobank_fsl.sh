#!/bin/bash
cd /src/data/work/ukbiobank/

# FLIRT T1w-space boldref image to T1w space,
# because fMRIPrep derivatives are in T1w *world* space,
# but not same voxel space, and FSL can't handle that.
flirt \
    -in /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/example_func.nii.gz \
    -ref /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -omat /src/data/work/ukbiobank/func2highres.mat

# FLIRT T1w-space T1w image to MNI152NLin6Asym-2mm
flirt \
    -in /src/data/ukbiobank/0000001_01_2_0/T1/T1.nii.gz \
    -ref /src/data/MNI152_T1_2mm.nii.gz \
    -omat /src/data/work/ukbiobank/highres2standard.mat \
    -out /src/data/work/ukbiobank/T1_in_MNI_flirt.nii.gz

# FNIRT T1w-space T1w image to MNI152NLin6Asym-2mm
fnirt \
    --in=/src/data/work/ukbiobank/T1_in_MNI_flirt.nii.gz \
    --ref=/src/data/MNI152_T1_2mm.nii.gz \
    --fout=/src/data/work/ukbiobank/highresstd2standard_warp.nii.gz \
    --iout=/src/data/work/ukbiobank/T1_in_MNI_fnirt.nii.gz \
    --interp=spline

# Combine BOLD-to-T1w affine and T1w-to-MNI affine
convert_xfm \
    -omat /src/data/work/ukbiobank/func2standard.mat \
    -concat /src/data/work/ukbiobank/highres2standard.mat \
    /src/data/work/ukbiobank/func2highres.mat

# Combine BOLD-to-T1w affine and T1w-to-MNI warp
cd /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/

convertwarp \
    --ref=/src/data/MNI152_T1_2mm.nii.gz \
    --premat=/src/data/work/ukbiobank/func2standard.mat \
    --warp1=/src/data/work/ukbiobank/highresstd2standard_warp.nii.gz \
    --out=/src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/example_func2standard_warp.nii.gz

applywarp \
    -i /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/example_func.nii.gz \
    -r /src/data/MNI152_T1_2mm.nii.gz \
    -o /src/data/work/ukbiobank/example_func_in_MNI_fnirt.nii.gz \
    -w /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/reg/example_func2standard_warp.nii.gz

flirt \
    -in /src/data/ukbiobank/0000001_01_2_0/fMRI/rfMRI.ica/example_func.nii.gz \
    -ref /src/data/MNI152_T1_2mm.nii.gz \
    -applyxfm \
    -init /src/data/work/ukbiobank/func2standard.mat \
    -out /src/data/work/ukbiobank/example_func_in_MNI_flirt.nii.gz
