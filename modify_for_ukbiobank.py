"""Prepare fMRIPrep data for UK Biobank conversion.

-   Copy T1w-space boldref to fMRI/rfMRI.ica/example_func.nii.gz
-   Copy T1w-space BOLD data to
    fMRI/rfMRI.ica/filtered_func_data_clean.nii.gz
-   Convert motion parameters to FSL format and put in
    fMRI/rfMRI.ica/mc/prefiltered_func_data_mcf.par
-   Copy rmsd values to fMRI/rfMRI.ica/mc/prefiltered_func_data_mcf_abs.rms
-   FNIRT T1w-space BOLD data to MNI152NLin6Asym (resolution?) and output
    warp field to fMRI/rfMRI.ica/reg/example_func2standard_warp.nii.gz
"""
import json
import os

import nibabel as nb
import numpy as np
import pandas as pd


def main(fmri_dir, out_dir, work_dir):
    """Compile the workflows to run the additional processing steps."""
    subject = "01"
    subject_id = f"sub-{subject}"
    session = "1"
    session_id = f"ses-{session}"

    # fMRIPrep outputs all files in RAS+.
    # UK Biobank uses FSL for preprocessing,
    # so all converted files need to be in LAS+.
    las_orientation = nb.orientations.axcodes2ornt("LAS")

    os.makedirs(work_dir, exist_ok=True)

    out_sub_dir = os.path.join(out_dir, f"00000{subject}_0{session}_2_0")

    in_anat_dir = os.path.join(fmri_dir, subject_id, session_id, "anat")
    out_anat_dir = os.path.join(out_sub_dir, "T1")
    os.makedirs(out_anat_dir, exist_ok=True)

    # MNI152NLin6Asym-space T1w, for XCP-D
    in_anat_file = os.path.join(
        in_anat_dir,
        f"{subject_id}_{session_id}_space-MNI152NLin6Asym_desc-preproc_T1w.nii.gz",
    )
    anat_img = nb.load(in_anat_file)
    anat_img_las = anat_img.as_reoriented(las_orientation)
    out_anat_file = os.path.join(out_anat_dir, "T1_brain_to_MNI.nii.gz")
    anat_img_las.to_filename(out_anat_file)

    # T1w-space T1w, to create the transforms
    in_anat_file = os.path.join(
        in_anat_dir,
        f"{subject_id}_{session_id}_desc-preproc_T1w.nii.gz",
    )
    anat_img = nb.load(in_anat_file)
    anat_img_las = anat_img.as_reoriented(las_orientation)
    out_anat_file = os.path.join(out_anat_dir, "T1.nii.gz")
    anat_img_las.to_filename(out_anat_file)

    in_func_dir = os.path.join(fmri_dir, subject_id, session_id, "func")
    out_func_dir = os.path.join(out_sub_dir, "fMRI")
    os.makedirs(out_func_dir, exist_ok=True)
    out_ica_dir = os.path.join(out_func_dir, "rfMRI.ica")
    os.makedirs(out_ica_dir, exist_ok=True)
    out_reg_dir = os.path.join(out_ica_dir, "reg")
    os.makedirs(out_reg_dir, exist_ok=True)

    # Reorient BOLD files to LAS+ and place them in the working directory
    in_sbref = os.path.join(
        in_func_dir,
        f"{subject_id}_{session_id}_task-rest_acq-singleband_space-T1w_boldref.nii.gz",
    )
    sbref_img = nb.load(in_sbref)
    sbref_img_las = sbref_img.as_reoriented(las_orientation)
    out_sbref = os.path.join(out_ica_dir, "example_func.nii.gz")
    sbref_img_las.to_filename(out_sbref)

    in_func_file = os.path.join(
        in_func_dir,
        f"{subject_id}_{session_id}_task-rest_acq-singleband_space-T1w_desc-preproc_bold.nii.gz",
    )
    out_func_file = os.path.join(out_ica_dir, "filtered_func_data_clean.nii.gz")
    func_img = nb.load(in_func_file)
    func_img_las = func_img.as_reoriented(las_orientation)
    func_img_las.to_filename(out_func_file)

    in_mask_file = os.path.join(
        in_func_dir,
        f"{subject_id}_{session_id}_task-rest_acq-singleband_space-T1w_desc-brain_mask.nii.gz",
    )
    out_mask_file = os.path.join(out_ica_dir, "mask.nii.gz")
    mask_img = nb.load(in_mask_file)
    mask_img_las = mask_img.as_reoriented(las_orientation)
    mask_img_las.to_filename(out_mask_file)

    # Convert motion parameters to FSL format. Rotations come first, then translations.
    out_mc_dir = os.path.join(out_ica_dir, "mc")
    os.makedirs(out_mc_dir, exist_ok=True)
    in_motpars_file = os.path.join(
        in_func_dir,
        f"{subject_id}_{session_id}_task-rest_acq-singleband_desc-confounds_timeseries.tsv",
    )
    out_motpars_file = os.path.join(out_mc_dir, "prefiltered_func_data_mcf.par")
    confounds_df = pd.read_table(in_motpars_file)
    # FSL puts rotations first. Same units as fMRIPrep though.
    motpars_df = confounds_df[
        [
            "rot_x",
            "rot_y",
            "rot_z",
            "trans_x",
            "trans_y",
            "trans_z",
        ]
    ]
    motpars = motpars_df.values
    np.savetxt(out_motpars_file, motpars, fmt="%.9f", delimiter="  ", newline="\n")

    out_rmsd_file = os.path.join(out_mc_dir, "prefiltered_func_data_mcf_abs.rms")
    rmsd = confounds_df["rmsd"].fillna(0).values
    np.savetxt(out_rmsd_file, rmsd, fmt="%.9f", delimiter="  ", newline="\n")

    # Some hardcoded metadata
    metadata = {
        "Manufacturer": "Siemens",
        "ManufacturersModelName": "Skyra",
        "MagneticFieldStrength": 3,
        "FlipAngle": 51,
        "EchoTime": 0.0424,
        "RepetitionTime": 3,
        "EffectiveEchoSpacing": 0.000639989,
        "PhaseEncodingDirection": "j-",
    }
    out_json_file = os.path.join(out_func_dir, "rfMRI.json")
    with open(out_json_file, "w") as fo:
        json.dump(metadata, fo, sort_keys=True, indent=4)

    out_json_file = os.path.join(out_func_dir, "rfMRI_SBREF.json")
    with open(out_json_file, "w") as fo:
        json.dump(metadata, fo, sort_keys=True, indent=4)


if __name__ == "__main__":
    fmri_dir = "/src/data/fmriprep"
    out_dir = "/src/data/ukbiobank"
    work_dir = "/src/data/work/ukbiobank"
    main(fmri_dir, out_dir, work_dir)
