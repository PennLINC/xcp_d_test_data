"""Prepare fMRIPrep data for DCAN conversion.

- Run morphometry and mesh surface files through anatomical workflow to get fsLR-32k GIFTIs.
- Warp aparcaseg in native space to MNI152NLin6Asym-2mm space/resolution.
- Warp ribbon in native space to MNI152NLin6Asym-2mm space/resolution.
"""
import os
import shutil

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
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_desc-ribbon_mask.nii.gz",
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
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_hemi-L_pial.surf.gii",
    )
    rh_pial_surf = os.path.join(
        anat_dir,
        f"{subject_id}_ses-PNC1_acq-refaced_hemi-R_pial.surf.gii",
    )
    extensions = {
        "pial": ".surf.gii",
        "white": ".surf.gii",
        "thickness": ".shape.gii",
        "curv": ".shape.gii",
        "sulc": ".shape.gii",
    }
    out_surfaces = {
        "pial": "pial",
        "white": "white",
        "thickness": "thickness",
        "curv": "curvature",
        "sulc": "sulc",
    }
    for surface in extensions.keys():
        name = f"warp_{surface}_to_template_wf"
        wf = init_warp_surfaces_to_template_wf(
            fmri_dir=fmri_dir,
            subject_id=subject_id,
            output_dir=work_dir,
            omp_nthreads=1,
            mem_gb=4,
            name=name,
        )

        lh_surf = os.path.join(
            anat_dir,
            f"{subject_id}_ses-PNC1_acq-refaced_hemi-L_{surface}{extensions[surface]}",
        )
        rh_surf = os.path.join(
            anat_dir,
            f"{subject_id}_ses-PNC1_acq-refaced_hemi-R_{surface}{extensions[surface]}",
        )

        wf.inputs.inputnode.anat_to_template_xfm = anat_to_template_xfm
        wf.inputs.inputnode.template_to_anat_xfm = template_to_anat_xfm
        wf.inputs.inputnode.lh_pial_surf = lh_pial_surf
        wf.inputs.inputnode.rh_pial_surf = rh_pial_surf
        wf.inputs.inputnode.lh_wm_surf = lh_surf
        wf.inputs.inputnode.rh_wm_surf = rh_surf
        wf.base_dir = work_dir
        wf_res = wf.run()
        wf_nodes = get_nodes(wf_res)
        lh_surf_fslr = wf_nodes[f"{name}.outputnode"].get_output("lh_wm_surf")
        rh_surf_fslr = wf_nodes[f"{name}.outputnode"].get_output("rh_wm_surf")

        lh_surf_out = os.path.join(
            surf_dir,
            f"{subject}.L.{out_surfaces[surface]}.32k_fs_LR{extensions[surface]}",
        )
        rh_surf_out = os.path.join(
            surf_dir,
            f"{subject}.R.{out_surfaces[surface]}.32k_fs_LR{extensions[surface]}",
        )
        os.rename(lh_surf_fslr, lh_surf_out)
        os.rename(rh_surf_fslr, rh_surf_out)
        if surface == "thickness":
            # Mock up the corrected thickness, myelin, and smoothed myelin
            # The myelin maps might not work correctly since they're shape.giis
            lh_smm = os.path.join(
                surf_dir, f"{subject}.L.SmoothedMyelinMap.32k_fs_LR.func.gii"
            )
            rh_smm = os.path.join(
                surf_dir, f"{subject}.R.SmoothedMyelinMap.32k_fs_LR.func.gii"
            )
            lh_mm = os.path.join(surf_dir, f"{subject}.L.MyelinMap.32k_fs_LR.func.gii")
            rh_mm = os.path.join(surf_dir, f"{subject}.R.MyelinMap.32k_fs_LR.func.gii")
            lh_ct = os.path.join(
                surf_dir, f"{subject}.L.corrThickness.32k_fs_LR.shape.gii"
            )
            rh_ct = os.path.join(
                surf_dir, f"{subject}.R.corrThickness.32k_fs_LR.shape.gii"
            )
            shutil.copyfile(lh_surf_out, lh_smm)
            shutil.copyfile(lh_surf_out, lh_mm)
            shutil.copyfile(lh_surf_out, lh_ct)
            shutil.copyfile(rh_surf_out, rh_smm)
            shutil.copyfile(rh_surf_out, rh_mm)
            shutil.copyfile(rh_surf_out, rh_ct)


if __name__ == "__main__":
    fmri_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/fmriprep-reduced"
    out_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/derivatives/dcan"
    work_dir = "/Users/taylor/Documents/linc/xcp_d_test_data/data/work/dcan"
    main(fmri_dir, out_dir, work_dir)
