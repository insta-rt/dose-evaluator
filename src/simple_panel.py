import streamlit as st
import plotly.express as px
from src import utils


def dvh_panel():
    st.markdown(f"## Step 1: Upload dose distribution volume and mask files")
    st.markdown(
        f"Look [here](https://pyradise.readthedocs.io) to format your files into NIfTI format using Pyradise.")
    dose_file = st.file_uploader("Upload a dose distribution volume (in .nii.gz)", type=['nii', 'gz'])

    mask_files = st.file_uploader("Upload mask volumes (in .nii.gz)", accept_multiple_files=True,
                                  type=['nii', 'gz'])

    files_uploaded = (dose_file is not None) and (len(mask_files) > 0)

    if files_uploaded:
        st.markdown(f"Both dose and mask files are uploaded. Click the button below to proceed.")
        x = st.button("Compute")

        st.divider()

        if x:
            st.markdown(f"## Step 2: Visualize DVH")
            dose, structures = utils.read_dose_and_masks(dose_file, mask_files)
            df = utils.dvh_from_files(dose, structures)
            fig = px.line(df, x="Dose", y="Volume", color="Structure")
            fig.update_xaxes(showgrid=True)
            fig.update_yaxes(showgrid=True)
            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            st.markdown(f"## Step 3: Dose Metrics")
            df = utils.dose_summary(dose, structures)
            st.table(df)

            st.markdown(f"Download the DVH data here.")
            csv = df.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name="dvh_data.csv", mime="text/csv")