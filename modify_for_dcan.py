"""Prepare fMRIPrep data for DCAN conversion.

- Run mesh surface files through anatomical workflow to get fsLR-32k GIFTIs.
- Warp aparcaseg in native space to MNI152NLin6Asym-2mm space/resolution.
- Warp ribbon in native space to MNI152NLin6Asym-2mm space/resolution.
"""
import os

from templateflow.api import get as get_template
from xcp_d.interfaces.ants import ApplyTransforms
from xcp_d.tests.utils import get_nodes
from xcp_d.workflows.anatomical import init_warp_surfaces_to_template_wf


def main(fmri_dir, out_dir, work_dir):
    """Compile the workflows to run the additional processing steps."""
    subject = "1648798153"
    subject_id = f"sub-{subject}"

    anat_dir = os.path.join(fmri_dir, subject_id, "ses-PNC1", "anat")
    out_anat_dir = os.path.join(
        out_dir,
        subject_id,
        "ses-PNC1",
        "files",
        "MNINonLinear",
    )
    surf_dir = os.path.join(out_anat_dir, "fsaverage_LR32k")
    os.makedirs(surf_dir, exist_ok=True)

    # Step 1. Warp files from native T1w space to MNI152NLin6Asym-2mm space/resolution.
    aparcaseg = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_desc-aparcaseg_dseg.nii.gz",
    )
    aparcaseg_out = os.path.join(out_anat_dir, "aparc+aseg.nii.gz")
    ribbon = os.path.join(
        anat_dir, f"{subject_id}_ses-PNC1_acq-refaced_desc-ribbon_mask.nii.gz"
    )
    ribbon_out = os.path.join(out_anat_dir, "ribbon.nii.gz")
    anat_to_template_xfm = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_from-T1w_to-MNI152NLin6Asym_mode-image_xfm.h5",
    )
    template_to_anat_xfm = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.h5",
    )
    template = str(
        get_template(
            template="MNI152NLin6Asym",
            cohort=None,
            resolution=2,
            desc=None,
            suffix="T1w",
        ),
    )
    interface = ApplyTransforms(
        num_threads=1,
        interpolation="GenericLabel",
        input_image_type=3,
        dimension=3,
        input_image=aparcaseg,
        output_image=aparcaseg_out,
        transforms=anat_to_template_xfm,
        reference_image=template,
    )
    interface.run(cwd=work_dir)

    interface = ApplyTransforms(
        num_threads=1,
        interpolation="GenericLabel",
        input_image_type=3,
        dimension=3,
        input_image=ribbon,
        output_image=ribbon_out,
        transforms=anat_to_template_xfm,
        reference_image=template,
    )
    interface.run(cwd=work_dir)

    # Step 2. Warp surfaces from fsnative to fsLR-32k.
    lh_pial_surf = os.path.join(
        anat_dir, f"{subject_id}_ses-PNC1_acq-refaced_hemi-L_pial.surf.gii"
    )
    rh_pial_surf = os.path.join(
        anat_dir, f"{subject_id}_ses-PNC1_acq-refaced_hemi-R_pial.surf.gii"
    )
    lh_wm_surf = os.path.join(
        anat_dir, f"{subject_id}_ses-PNC1_acq-refaced_hemi-L_white.surf.gii"
    )
    rh_wm_surf = os.path.join(
        anat_dir, f"{subject_id}_ses-PNC1_acq-refaced_hemi-R_white.surf.gii"
    )
    wf = init_warp_surfaces_to_template_wf(
        fmri_dir=fmri_dir,
        subject_id=subject_id,
        output_dir=work_dir,
        omp_nthreads=1,
        mem_gb=4,
        name="warp",
    )

    wf.inputs.inputnode.anat_to_template_xfm = anat_to_template_xfm
    wf.inputs.inputnode.template_to_anat_xfm = template_to_anat_xfm
    wf.inputs.inputnode.lh_pial_surf = lh_pial_surf
    wf.inputs.inputnode.rh_pial_surf = rh_pial_surf
    wf.inputs.inputnode.lh_wm_surf = lh_wm_surf
    wf.inputs.inputnode.rh_wm_surf = rh_wm_surf
    wf.base_dir = work_dir
    wf_res = wf.run()
    wf_nodes = get_nodes(wf_res)
    lh_wm_fslr = wf_nodes["warp.split_up_surfaces_fsLR_32k_lh"].get_output("out2")
    rh_wm_fslr = wf_nodes["warp.split_up_surfaces_fsLR_32k_rh"].get_output("out2")
    lh_wm_out = os.path.join(surf_dir, f"{subject}.L.white.32k_fs_LR.surf.gii")
    rh_wm_out = os.path.join(surf_dir, f"{subject}.R.white.32k_fs_LR.surf.gii")
    os.rename(lh_wm_fslr, lh_wm_out)
    os.rename(rh_wm_fslr, rh_wm_out)

    lh_pial_fslr = wf_nodes["warp.split_up_surfaces_fsLR_32k_lh"].get_output("out1")
    rh_pial_fslr = wf_nodes["warp.split_up_surfaces_fsLR_32k_rh"].get_output("out1")
    lh_pial_out = os.path.join(surf_dir, f"{subject}.L.pial.32k_fs_LR.surf.gii")
    rh_pial_out = os.path.join(surf_dir, f"{subject}.R.pial.32k_fs_LR.surf.gii")
    os.rename(lh_pial_fslr, lh_pial_out)
    os.rename(rh_pial_fslr, rh_pial_out)


if __name__ == "__main__":
    fmri_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/fmriprep-reduced"
    out_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/derivatives/dcan"
    work_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/work/dcan"
    main(fmri_dir, out_dir, work_dir)
