import streamlit as st
import plotly.express as px

from src import utils


def display_summary(dose, structure_masks):
    struct_intersect = {}
    summary_df = {}
    for id in structure_masks.keys():
        st.markdown(f"## Summary of Segmentation: {id}")
        if len(struct_intersect) == 0:
            struct_intersect = set(structure_masks[id].keys())
        else:
            struct_intersect = struct_intersect.intersection(set(structure_masks[id].keys()))
        summary_df[id] = utils.dose_summary(dose, structure_masks[id])

        df = utils.dvh_by_structure(dose, structure_masks[id])
        fig = px.line(df, x="Dose", y="Volume", color="Structure")
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
        st.plotly_chart(fig, use_container_width=True)

        st.table(summary_df[id])
        csv = summary_df[id].to_csv(index=True)
        st.download_button(label="Download CSV", data=csv, file_name=f"dvh_data_{id}.csv", mime="text/csv")

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


def display_difference_dvh(dose, structure_masks, selected_structures):
    for structure in selected_structures:
        current_structure = {}
        for id in structure_masks.keys():
            current_structure[structure + "_" + str(id)] = structure_masks[id][structure]

        st.markdown(f"#### DVH comparisons for {structure}")
        df = utils.dvh_by_structure(dose, current_structure)
        fig = px.line(df, x="Dose", y="Volume", color="Structure")
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
        st.plotly_chart(fig, use_container_width=True)


def panel():

    step_1_complete = False
    step_2_complete = False

    tab1, tab2, tab3 = st.tabs(["🗃️Upload Data", "📊 View Metrics", "🔍 Examine Differences"])

    with tab1:
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
                mask_files[id] = st.file_uploader(f"Upload mask volumes index: {id} (in .nii.gz)", accept_multiple_files=True,
                                              type=['nii', 'gz'], key=id+1)
        else:
            mask_files[1] = st.file_uploader("Upload mask volumes (in .nii.gz)", accept_multiple_files=True,
                                          type=['nii', 'gz'], key=0)

        files_uploaded = (dose_file is not None) and (len(mask_files) > 0)

        if files_uploaded:
            st.markdown(f"Both dose and mask files are uploaded. Click the toggle button below to proceed.")
            step_1_complete = st.toggle("Ready to Compute!")

    with tab2:
        st.markdown(f"## Step 2: Dose Metrics")
        st.markdown(f"Complete step 1 to view metrics.")
        if step_1_complete:
            dose, _ = utils.read_dose(dose_file)
            structure_masks = {}
            for id in mask_files.keys():
                structure_masks[id] = utils.read_masks(mask_files[id])

            summary_df, struct_intersect = display_summary(dose, structure_masks)

            st.divider()

            if len(struct_intersect) == 0:
                st.markdown("No common structures found in the segmentations. Please re-upload the mask files.")

            else:
                step_2_complete = True

    with tab3:
        st.markdown(f"## Step 3: Examine Differences")
        st.markdown(f"Complete step 1 and 2 to examine differences.")
        if step_1_complete and step_2_complete:
            selected_structures = st.multiselect(
                "Choose structures to compare:",
                list(struct_intersect),
                [],
            )

            display_difference_dvh(dose, structure_masks, selected_structures)

            ref_id = st.number_input("Choose reference segmentation: ", min_value=1, max_value=n_compares, value="min",
                                     step=1)
            compare_differences(summary_df, selected_structures, ref_id)