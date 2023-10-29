#libraries
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

filename = 'data/Input_Sales_Data_v2.csv'
logo_image = 'images/logo.jpg'

#config set up
st.set_page_config(
        page_title = "Sales-Dashboard app",
       initial_sidebar_state ="auto", 
       page_icon = "🧊",
       layout = "centered",
       
       )

#reading the file
df = pd.read_csv(filename)
#title
st.title('Sales Dashboard App')
manufactures = tuple(df['Manufacturer'].unique())
categories = tuple(df['Category'].unique())
brands = tuple(df['Brand'].unique())

col1, col2, col3 = st.columns(3)
