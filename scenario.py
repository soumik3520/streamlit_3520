import streamlit as st
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
from ui import header_ui, sidebar_ui

from utils import (
    read_scenario_data,
    gen_aggrid,
    read_scenario_details,
    format_layout_fig,
)

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode,
    JsCode,
    ColumnsAutoSizeMode,
)
# Header
header_ui()
sidebar_ui()

#
sc_data = read_scenario_data()

# CSS to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

# Custom CSS
custom_css = {
    ".ag-header-cell-label": {"justify-content": "center"},
    "cellStyle": {"textAlign": "center"},
    ".ag-cell": {"display": "flex", "justify-content": "center",},
    # ".ag-cell": {"white-space": "break-spaces"},
}


# Aggrid generation
gd = gen_aggrid(sc_data)
gd.configure_column(
    field="Name", header_name="Name", cellStyle={"white-sapces": "break-spaces"}
)
gd.configure_selection(
    selection_mode="multiple", use_checkbox=True,
)
grid_options = gd.build()
grid_table = AgGrid(
    sc_data,
    height=250,
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,
    theme="balham",
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    custom_css=custom_css,
)

selected_row = grid_table["selected_rows"]

if len(selected_row) > 0:
    st.write("## Comparison of Selected Scenarios")
    selected_df = pd.DataFrame(selected_row)
    sel_cols = ["Name", "revenue", "cost", "profit"]
    selected_df = selected_df[sel_cols]

    selected_df = selected_df.rename(
        columns={
            "index": "Metric",
            "Name": "Scenario",
            "revenue": "Revenue",
            "cost": "Cost",
            "profit": "Profit",
        }
    )
    selected_df = selected_df.set_index("Scenario")
    selected_df = selected_df.T.reset_index()
    # st.dataframe(selected_df)
    fig = px.histogram(
        selected_df,
        x="index",
        y=[x for x in selected_df.columns if x != "index"],
        barmode="group",
        text_auto=".2s",
    )
    fig = format_layout_fig(fig, title="Scenario Comparison", x_axis_title="")
    fig = fig.update_layout(
        legend=dict(
            yanchor="bottom", xanchor="center", orientation="h", y=-0.5, x=0.5, title=""
        ),
        yaxis_title="Value",
    )
    st.plotly_chart(fig, use_container_width=True)
