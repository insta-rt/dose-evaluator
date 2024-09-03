import numpy as np
import pandas as pd
from numpy import ndarray
from gzip import GzipFile
from nibabel import FileHolder, Nifti1Image

def read_file(byte_file):
    # See https://stackoverflow.com/questions/62579425/simpleitk-read-io-byteio
    fh = FileHolder(fileobj=GzipFile(fileobj=byte_file))
    img = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    arr = np.array(img.dataobj)
    return arr, img.header


def compute_dvh(_dose: np.ndarray, _struct_mask: np.ndarray, max_dose = 65, step_size = 0.1,
    ) -> tuple[ndarray, ndarray]:

    dose_in_oar = _dose[_struct_mask > 0]
    bins = np.arange(0, max_dose, step_size)
    total_voxels = len(dose_in_oar)
    values = []

    if total_voxels == 0:
        # There's no voxels in the mask
        values = np.zeros(len(bins))
    else:
        for bin in bins:
            number = (dose_in_oar >= bin).sum()
            value = (number / total_voxels) * 100
            values.append(value)
        values = np.asarray(values)

    return bins, values


def read_dose(dose_file):
    dose_volume, dose_header = read_file(dose_file)
    return dose_volume, dose_header


def read_masks(mask_files):
    structure_masks = {}
    for mask_file in mask_files:
        mask_volume, mask_header = read_file(mask_file)
        struct_name = mask_file.name.split(".")[0]
        structure_masks[struct_name] = mask_volume
    return structure_masks


def read_dose_and_masks(dose_file, mask_files):
    dose_volume, dose_header = read_dose(dose_file)
    structure_masks = read_masks(mask_files)

    return dose_volume, structure_masks


def dvh_from_files(dose_volume, structure_masks):

    dvh_data = {}
    max_dose = 70
    step_size = 0.1
    dvh_data["Dose"] = np.arange(0, max_dose, step_size)

    for structure in structure_masks.keys():
        bins, values = compute_dvh(dose_volume, structure_masks[structure], max_dose, step_size)
        dvh_data[structure] = values

    df = pd.DataFrame.from_dict(dvh_data)
    df = pd.melt(df, id_vars=['Dose'], value_vars=structure_masks.keys(),
                 var_name='Structure', value_name='Volume')
    return df


def dose_summary(dose_volume, structure_masks):
    dose_metrics = {}
    for structure in structure_masks.keys():
        dose_in_structure = dose_volume[structure_masks[structure] > 0]
        dose_metrics[structure] = {
            "Mean Dose": np.mean(dose_in_structure),
            "Max Dose": np.max(dose_in_structure),
            "Min Dose": np.min(dose_in_structure),
            "D95": np.percentile(dose_in_structure, 95),
            "D50": np.percentile(dose_in_structure, 50),
            "D5": np.percentile(dose_in_structure, 5),
        }

    df = pd.DataFrame.from_dict(dose_metrics).T
    return df