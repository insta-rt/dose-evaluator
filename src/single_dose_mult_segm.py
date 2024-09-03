import streamlit as st
import plotly.express as px
from src import utils


def display_summary(dose, structure_masks):
    struct_intersect = {}
    summary_df = {}
    for id in structure_masks.keys():
        st.divider()

        st.markdown(f"## Summary of Segmentation: {id}")
        if len(struct_intersect) == 0:
            struct_intersect = set(structure_masks[id].keys())
        else:
            struct_intersect = struct_intersect.intersection(set(structure_masks[id].keys()))
        summary_df[id] = utils.dose_summary(dose, structure_masks[id])
        st.table(summary_df[id])

    return summary_df, struct_intersect


def compare_differences(summary_df, selected_structures, ref_id):
    for structure in selected_structures:
        st.markdown(f"### For structure: {structure}")
        for id in summary_df.keys():
            if id == ref_id:
                continue
            st.markdown(f"#### Dose differences between Segmentation: {id} vs Reference: {ref_id}")
            diff = summary_df[id].loc[structure, :] - summary_df[ref_id].loc[structure, :]
            st.table(diff)


def panel():
    st.markdown(f"## Step 1: Upload dose distribution volume and mask files")
    st.markdown(
        f"Look [here](https://pyradise.readthedocs.io) to format your files into NIfTI format using Pyradise.")

    dose_file = st.file_uploader("Upload the unique dose distribution volume (in .nii.gz)", type=['nii', 'gz'])

    max_compares = 5
    n_compares = st.number_input(f"Number of segmentations to compare (maximum: {max_compares}):",
                                 min_value=1, max_value=max_compares, value="min", step=1)

    mask_files = {}
    st.markdown("Upload the mask volumes for each segmentation.")
    if n_compares > 1:
        for id in range(1, n_compares+1):
            mask_files[id] = st.file_uploader(f"Upload mask volumes index: {id+1} (in .nii.gz)", accept_multiple_files=True,
                                          type=['nii', 'gz'], key=id+1)
    else:
        mask_files[1] = st.file_uploader("Upload mask volumes (in .nii.gz)", accept_multiple_files=True,
                                      type=['nii', 'gz'], key=0)

    files_uploaded = (dose_file is not None) and (len(mask_files) > 0)

    if files_uploaded:
        st.markdown(f"Both dose and mask files are uploaded. Click the toggle button below to proceed.")
        on = st.toggle("Compute")

        dose, _ = utils.read_dose(dose_file)
        structure_masks = {}
        for id in mask_files.keys():
            structure_masks[id] = utils.read_masks(mask_files[id])

        if on:
            st.markdown(f"## Step 2: Dose Metrics")
            summary_df, struct_intersect = display_summary(dose, structure_masks)

            st.divider()

            if len(struct_intersect) == 0:
                st.markdown("No common structures found in the segmentations. Please re-upload the mask files.")

            else:
                st.markdown(f"## Step 3: List Differences")
                ref_id = st.number_input("Choose reference segmentation: ", min_value=1, max_value=n_compares, value="min", step=1)
                selected_structures = st.multiselect(
                    "Choose structures to compare:",
                    list(struct_intersect),
                    [],
                )

                compare_differences(summary_df, selected_structures, ref_id)