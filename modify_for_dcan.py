"""Prepare fMRIPrep data for DCAN conversion.

- Run morphometry and mesh surface files through anatomical workflow to get fsLR-32k GIFTIs.
- Warp aparcaseg in native space to MNI152NLin6Asym-2mm space/resolution.
- Warp ribbon in native space to MNI152NLin6Asym-2mm space/resolution.
"""
import os

from templateflow.api import get as get_template
from xcp_d.interfaces.ants import ApplyTransforms
from xcp_d.workflows.anatomical import init_warp_surfaces_to_template_wf


def main(fmri_dir, out_dir, work_dir):
    """Compile the workflows to run the additional processing steps."""
    subject_id = "sub-1648798153"
    # Step 1. Warp files from native T1w space to MNI152NLin6Asym-2mm space/resolution.
    anat_dir = os.path.join(fmri_dir, subject_id, "ses-PNC1", "anat")
    out_anat_dir = os.path.join(
        out_dir,
        subject_id,
        "ses-PNC1",
        "files",
        "MNINonLinear",
    )
    aparcaseg = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_desc-aparcaseg_dseg.nii.gz",
    )
    aparcaseg_out = os.path.join(out_anat_dir, "aparc+aseg.nii.gz")
    ribbon = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_desc-ribbon_mask.nii.gz",
    )
    ribbon_out = os.path.join(out_anat_dir, "ribbon.nii.gz")
    xfm = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_from-T1w_to-MNI152NLin6Asym_mode-image_xfm.h5",
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
        transforms=xfm,
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
        transforms=xfm,
        reference_image=template,
    )
    interface.run(cwd=work_dir)

    # Step 2. Warp surfaces from fsnative to fsLR-32k.
    for surface in ["pial", "thickness", "curv", "sulc"]:
        wf = init_warp_surfaces_to_template_wf(
            fmri_dir=fmri_dir,
            subject_id=subject_id,
            output_dir=work_dir,
            omp_nthreads=1,
            mem_gb=4,
            name="warp_surfaces_to_template_wf",
        )
        wf.inputs.inputnode.anat_to_template_xfm = ""
        wf.inputs.inputnode.template_to_anat_xfm = ""
        wf.inputs.inputnode.lh_pial_surf = ""
        wf.inputs.inputnode.rh_pial_surf = ""
        wf.inputs.inputnode.lh_wm_surf = ""
        wf.inputs.inputnode.rh_wm_surf = ""
        wf.run()


if __name__ == "__main__":
    main()
