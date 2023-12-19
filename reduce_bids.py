"""Reduce BIDS files for test dataset.

Steps:
1. Rename subject ID and session ID in folder and file names.
2. Update IntendedFor field in field map JSONs.
3. Reduce BOLD files to first 50 volumes.
"""
import json
import os
from glob import glob

import nibabel as nb

if __name__ == "__main__":
    mapper = {
        "sub-1648798153": "sub-01",
        "ses-PNC1": "ses-1",
    }
    bids_dir = "/cbica/home/salot/datasets/pnc-bold/"

    # Rename folders
    os.rename(
        os.path.join(bids_dir, "sub-1648798153"),
        os.path.join(bids_dir, "sub-01"),
    )
    os.rename(
        os.path.join(bids_dir, "sub-01/ses-PNC"),
        os.path.join(bids_dir, "sub-01/ses-1"),
    )

    # Rename files with new subject and session IDs
    all_files = sorted(glob(os.path.join(bids_dir, "sub-*/ses-*/*/*")))
    for file_ in all_files:
        new_file = file_
        for map_key, map_val in mapper.items():
            new_file = new_file.replace(map_key, map_val)

        os.rename(file_, new_file)

    # Reduce BOLD files to first 50 volumes.
    bold_files = sorted(glob(os.path.join(bids_dir, "sub-*/ses-*/func/*.nii.gz")))
    for bold_file in bold_files:
        img = nb.load(bold_file)
        data = img.get_fdata()
        data = data[:, :, :, :50]
        new_img = nb.Nifti1Image(data, img.affine, img.header)
        new_img.to_filename(bold_file)

    # Update IntendedFor field in field map JSONs.
    fmap_jsons = sorted(glob(os.path.join(bids_dir, "sub-*/ses-*/fmap/*.json")))
    for fmap_json in fmap_jsons:
        with open(fmap_json, "r") as fo:
            fmap_metadata = json.load(fo)

        if "IntendedFor" in fmap_metadata:
            intended_for = fmap_metadata["IntendedFor"]
            new_intended_for = []
            for fpath in intended_for:
                for map_key, map_val in mapper.items():
                    fpath = fpath.replace(map_key, map_val)

                new_intended_for.append(fpath)
