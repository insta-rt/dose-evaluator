import streamlit as st
import plotly.express as px
import pandas as pd

from src import utils


def display_summary(structure_mask, doses):

    summary_df = {}
    for id in doses.keys():
        st.markdown(f"## Summary of Dose volume: {id}")

        df = utils.dvh_by_structure(doses[id], structure_mask)
        fig = px.line(df, x="Dose", y="Volume", color="Structure")
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
        st.plotly_chart(fig, use_container_width=True)

        summary_df[id] = utils.dose_summary(doses[id], structure_mask)
        st.table(summary_df[id])
        csv = summary_df[id].to_csv(index=True)
        st.download_button(label="Download CSV", data=csv, file_name=f"dvh_data_{id}.csv", mime="text/csv")

        st.divider()

    return summary_df


def compare_differences(summary_df, selected_structures, ref_id):
    for id in summary_df.keys():
        if id == ref_id:
            continue

        diff_table = pd.DataFrame()
        st.markdown(f"#### Dose differences between Dose: {id} vs Reference: {ref_id}")
        for structure in selected_structures:
            diff_table.loc[:, structure] = summary_df[id].loc[structure, :] - summary_df[ref_id].loc[structure, :]
        st.table(diff_table)


def display_difference_dvh(doses, structure_mask, selected_structures):
    for structure in selected_structures:
        st.markdown(f"#### DVH comparisons for {structure}")
        df = utils.dvh_by_dose(doses, structure_mask[structure], structure)
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

        max_compares = 5
        n_compares = st.number_input(f"Number of dose volumes to compare (maximum: {max_compares}):",
                                     min_value=1, max_value=max_compares, value="min", step=1)

        dose_files = {}
        st.markdown("Upload the dose volumes:")
        if n_compares > 1:
            for id in range(1, n_compares+1):
                dose_files[id] = st.file_uploader(f"Upload dose volumes index: {id} (in .nii.gz)", type=['nii', 'gz'], key=id)
        else:
            dose_files[1] = st.file_uploader(f"Upload dose volume (in .nii.gz)", type=['nii', 'gz'], key=1)

        st.markdown("Upload the segmentation masks:")

        mask_files = st.file_uploader("Upload mask volumes (in .nii.gz)", accept_multiple_files=True,
                                          type=['nii', 'gz'], key=0)

        files_uploaded = (len(dose_files) > 0) and (len(mask_files) > 0)

        if files_uploaded:
            st.markdown(f"Both dose and mask files are uploaded. Click the toggle button below to proceed.")
            step_1_complete = st.toggle("Compute")

            structure_mask = utils.read_masks(mask_files)
            doses = {}
            for id in dose_files.keys():
                doses[id], _ = utils.read_dose(dose_files[id])
        st.divider()

    with tab2:
        st.markdown(f"## Step 2: Dose Metrics")
        st.markdown(f"Complete Step 1 to view metrics.")
        if step_1_complete:
            summary_df = display_summary(structure_mask, doses)
            step_2_complete = True

    with tab3:
        st.markdown(f"## Step 3: Examine Differences")
        st.markdown(f"Complete Step 2 to proceed.")
        if step_2_complete:
            ref_id = st.number_input("Choose reference dose: ", min_value=1, max_value=n_compares, value="min", step=1)

            all_structures = list(structure_mask.keys())
            selected_structures = st.multiselect(
                "Choose structures to compare:",
                list(all_structures),
                [],
            )

            compare_differences(summary_df, selected_structures, ref_id)
            display_difference_dvh(doses, structure_mask, selected_structures)
        st.divider()