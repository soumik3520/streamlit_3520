import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode,
    JsCode,
    ColumnsAutoSizeMode,
)


def read_data(file_name, separator=";"):
    df = pd.read_csv(file_name, sep=separator, encoding="ISO-8859-1")
    grp_cols = [
        "Retailer",
        "Category",
        "Segment",
        "Sub-Segment",
        "Brand",
        "KNAC-14",
        "Description",
        "Day",
        "Month",
        "Year",
    ]
    df = (
        df.groupby(grp_cols)
        .agg(
            Units=("Units", "sum"),
            Volume=("Sales in kg", "sum"),
            Value=("Sales in LC", "sum"),
        )
        .reset_index()
    )
    df["Date"] = df[["Day", "Month", "Year"]].apply(
        lambda row: "-".join(row.values.astype(str)), axis=1
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y").dt.normalize()
    df["year"] = df["Date"].dt.year
    df["SKU"] = df["Description"]
    df["Value"] = 0.0012 * df["Value"]
    df["n_weeks"] = df.groupby(["KNAC-14"])["Date"].transform("nunique")
    df = df.loc[df["n_weeks"] >= 114]
    df["pred_flag"] = np.where(df["Date"].dt.year == 2021, 1, 0)
    df = df.drop(["Day", "Month", "Year", "Description", "n_weeks"], axis=1)
    df = df.sort_values(by=["SKU", "Date"])
    tt = df[["SKU"]].drop_duplicates()
    tt["R2"] = np.random.randint(low=55, high=85, size=tt.shape[0])
    df = pd.merge(df, tt)
    # df["R2"] = df.groupby(["SKU"])["R2"].transform("min")
    df["MAPE"] = (100 - df["R2"]) / 2
    df["Unit Price"] = df["Value"] / df["Units"]
    df["Vol Price"] = df["Value"] / df["Volume"]
    return df


# tt = read_data("data/weekly_raw_data.csv")
# tt.to_csv("data/sales_data.csv", index=False)


@st.cache_data()
def read_app_data():
    df = pd.read_excel("data/Bacardi-ToolData.xlsx", sheet_name="Data")
    df["Date"] = "01-01-" + df["Year"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    return df


def build_line_chart(df, x_col="Date", y_col="Units", color_col="SKU"):
    # color = ["#D01E2F" if x == 0 else "goldenrod" for x in pred_flag]
    fig = px.line(df, x=x_col, y=y_col, color=color_col)
    fig.update_traces(line={"width": 3})
    fig.update_xaxes(showgrid=False, ticklabelmode="period", tickformat="%Y")
    fig.update_layout(
        legend=dict(yanchor="bottom", xanchor="center", orientation="h", y=-0.5, x=0.5)
    )
    return fig


def format_layout_fig(fig, title="Unit Sales", x_axis_title="Year", prefix=False):
    fig.update_layout(title_text=title)
    fig.update_xaxes(
        title_text=x_axis_title,
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )
    fig.update_yaxes(
        rangemode="tozero", showline=True, linewidth=1, linecolor="black", mirror=True
    )
    fig.update(layout=dict(title=dict(x=0.5)))
    fig.update_layout(
        title_font_family="Rockwell", title_font_color="Black", template="plotly_white"
    )
    fig.update_layout(hovermode="x unified")
    fig.update_layout(
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Rockwell")
    )
    if prefix:
        fig.update_layout(yaxis_tickprefix="$")
    return fig


def gen_sku_metrics(df):
    tt = (
        df.groupby(["SKU", "year"])
        .agg(
            Units=("Units", "sum"),
            Value=("Value", "sum"),
            Rsq=("R2", "mean"),
            MAPE=("MAPE", "mean"),
        )
        .reset_index()
        .sort_values(by=["SKU", "year"])
    )
    tt["unit_growth"] = tt.groupby(["SKU"])["Units"].pct_change()
    tt["value_growth"] = tt.groupby(["SKU"])["Value"].pct_change()
    out_dict = {
        "units_sales": tt.loc[tt["year"] == 2020]["Units"].values[0],
        "value_sales": tt.loc[tt["year"] == 2020]["Value"].values[0],
        "unit_yoy_grth": tt.loc[tt["year"] == 2020]["unit_growth"].values[0],
        "value_yoy_grth": tt.loc[tt["year"] == 2020]["value_growth"].values[0],
        "MAPE": tt["MAPE"].mean(),
        "R2": tt["Rsq"].mean(),
    }
    return out_dict


@st.cache_data()
def read_scenario_data():
    df = pd.read_excel("data/scenarios.xlsx", sheet_name="Scenarios Summary")
    df["Created Date"] = df["Created Date"].dt.normalize()
    df["prec_profit"] = df["prec_profit"] * 100
    # df = df.style.format({"% Profit": "{:.2%}",}).background_gradient(
    #     subset="% Profit", cmap=temp
    # )
    return df


def gen_aggrid(df):
    gd = GridOptionsBuilder.from_dataframe(df)
    # gd.configure_default_column(hide=True, editable=False)
    gd.configure_default_column(type=["leftAligned"])
    gd.configure_column(
        field="Created Date",
        header_name="Created Date",
        hide=False,
        type=["customDateTimeFormat"],
        custom_format_string="MM-dd-yyyy",
    )
    gd.configure_column(
        field="revenue",
        header_name="Revenue ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.revenue.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="cost",
        header_name="Capital Costs ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.cost.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="inv_cost",
        header_name="Inventory Cost ($)",
        hide=True,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.inv_cost.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="profit",
        header_name="Profit ($)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.profit.toLocaleString('en-US');",
    )
    gd.configure_column(
        field="prec_profit",
        header_name="% Profit",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.prec_profit.toLocaleString() +'%';",
    )
    return gd


@st.cache_data()
def read_scenario_details():
    df = pd.read_excel("data/scenarios.xlsx", sheet_name="Details")
    return df


# @st.cache_data()
def read_scenario_planner():
    df = pd.read_excel("data/scenarios.xlsx", sheet_name="planner1")
    df["allocation"] = df["allocation"] * 100
    return df


def gen_aggrid_sc(df):
    sel_cols = [
        "sku",
        "age",
        "allocation",
        "exp_price",
        "cost",
        "demand",
    ]
    df = df[sel_cols]
    gd = GridOptionsBuilder.from_dataframe(df)
    # gd.configure_default_column(hide=True, editable=False)

    gd.configure_column(
        field="sku", header_name="SKU", hide=False, editable=False,
    )

    gd.configure_column(
        field="age",
        header_name="Demand Horizon(yrs)",
        hide=False,
        type=[
            # "numericColumn",
            # "numberColumnFilter",
            # "customNumericFormat",
        ],
        valueFormatter="data.age.toLocaleString('en-US');",
        editable=False,
    )

    gd.configure_column(
        field="exp_price",
        header_name="Expected Price (per case)",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueGetter="data.exp_price.toLocaleString('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits:0})",
        editable=False,
    )
    gd.configure_column(
        field="cost",
        header_name="Capital Costs	",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueGetter="data.cost.toLocaleString('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits:0})",
        editable=False,
    )
    gd.configure_column(
        field="demand",
        header_name="Demand",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        valueFormatter="data.demand.toLocaleString('en-US');",
        editable=False,
    )
    gd.configure_column(
        field="allocation",
        header_name="Allocation",
        hide=False,
        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
        # valueGetter="data.allocation.toLocaleString('en-US', {style: 'percent', maximumFractionDigits:0,minimumFractionDigits:0})",
        valueFormatter="data.allocation.toLocaleString() + '%'",
        editable=True,
    )
    return gd


def mult_yaxis_plot(x_data, y1_data, y2_data, y1_name=None, y2_name=None, colors=None):
    # Create figure with secondary y-axis
    y1_name = "yaxis data" if y1_name is None else y1_name
    y2_name = "yaxis2 data" if y2_name is None else y2_name
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = "#49246C" if None else colors
    # Add traces
    fig.add_trace(
        go.Scatter(x=x_data, y=y1_data, name=y1_name, line={"width": 3}),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=x_data, y=y2_data, name=y2_name, line={"color": "#CD0F26", "width": 3}
        ),
        secondary_y=True,
    )
    return fig