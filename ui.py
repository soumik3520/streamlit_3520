import streamlit as st
import base64


def header_ui(title="Scenario Comparison"):
    st.markdown(
        """
        <style>
        .pageheader {
            padding: 0px;
            width: 100%;
            margin-left: 0px;
            margin-top: -60px;
            margin-bottom: 50px;
        }
        .pagetitle {
            text-align: center; 
            #position: absolute; 
            width: 100%;  
            margin-bottom: 10px; 
            #border: 2px #D3D2D2;
            font-size: 30px;
            font-weight: bold;
            padding: 10px;
            border-radius: 10px;
            background-color: #D01E2F;
            color: black; 
            #color: white;
        }
    """,
        unsafe_allow_html=True,
    )

    metric_style = """
    <style>
 div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   height: 150px;
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red;
}
    <style>
    """
    st.markdown(metric_style, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='pageheader'>
            <p class='pagetitle'>
                {title}
            </p>
        </div>""",
        unsafe_allow_html=True,
    )


@st.cache_data()
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(png_file):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: 50px 70px;
                    margin-top: -30px;
                    margin-bottom: 30px;
                    padding-top: 100px;
                    padding-bottom: 20px;
                }
            </style>
            """ % (
        binary_string
    )


def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup, unsafe_allow_html=True,
    )


def sidebar_ui():
    img = "Bacardi-logo.png"
    add_logo(img)


def insert_dummy_buttons():
    names_list = [
        "Product Inventory",
        "Demand Profile",
        "Price Profile",
        "Cost Profile",
        "Cpacity Projections",
        "Capital Cost Projections",
        "Margin Targets",
        "Econometric Assumptions",
        "Other Assumptions",
    ]
    with st.sidebar.expander("Click to access other views"):
        st.write("temp")
        for name_ in names_list:
            st.sidebar.text_area(name_)