import streamlit as st

from src.instructions import instruction_panel
from src.simple_panel import dvh_panel
import src.single_dose_mult_segm as sdms


# Initial code from here: https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app
# Run this from >> streamlit run app.py


def single_dose_single_segmentation():
    st.markdown(f"# {list(page_names_to_funcs.keys())[1]}")
    dvh_panel()


def single_dose_multiple_segmentation():
    st.markdown(f"# {list(page_names_to_funcs.keys())[2]}")
    sdms.panel()

def multiple_dose_single_segmentation():
    st.markdown(f"# {list(page_names_to_funcs.keys())[3]}")


def multiple_dose_multiple_segmentation():
    st.markdown(f"# {list(page_names_to_funcs.keys())[4]}")



page_names_to_funcs = {
    "Instructions": instruction_panel,
    "Single Dose Plan, Single Segmentation": single_dose_single_segmentation,
    "Single Dose Plan, Multiple Segmentations": single_dose_multiple_segmentation,
    "Multiple Dose Plans, Single Segmentation": multiple_dose_single_segmentation,
    "Multiple Dose Plans, Multiple Segmentations": multiple_dose_multiple_segmentation,
}

task_selection = st.sidebar.selectbox("Choose a task:", page_names_to_funcs.keys())
page_names_to_funcs[task_selection]()