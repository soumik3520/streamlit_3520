# libraries

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

#reading data

filename = 'Input_Sales_Data_v2.csv'
logo_image = 'logo.jpg'
df = pd.read_csv(filename)

#setting config
st.set_page_config(
        page_title="Sales App",
       initial_sidebar_state="expanded",  
       page_icon="🧊",
       )

#embedding image
st.sidebar.image(logo_image,use_column_width=False, width=100,clamp=True)
st.markdown("<style>img{float: left;}</style>", unsafe_allow_html=True)

min_date = pd.to_datetime(df['Date'].min()).to_pydatetime()
max_date = pd.to_datetime(df['Date'].max()).to_pydatetime()

#slider embedding
selected_date_range = st.slider(
    "Date Ranges...",
    min_value = min_date,
    max_value = max_date,
    value = (min_date,max_date),
    format = "YYYY-MM-DD",  
)
# filtering w.r.t date range
filtered_df = df[(pd.to_datetime(df['Date']) >= selected_date_range[0]) 
                 & (pd.to_datetime(df['Date']) <= selected_date_range[1])]

#manufacturer volume and value sales
df_sales_agg = filtered_df.groupby('Manufacturer') \
                          .agg({'Volume':'sum','Value':'sum'})
st.dataframe(df_sales_agg)

# top five manufactures - based on sales
filtered_df['total_cog'] = filtered_df['Price'] * filtered_df['Volume']
weighted_sales = filtered_df \
            .groupby('Manufacturer') \
            .agg(weighted_price=('total_cog', lambda x: x.sum() / filtered_df['Volume'].sum())).reset_index()
top_manu = weighted_sales.sort_values(by='weighted_price',ascending=False).head(5)

#creating line graph
figsize =(10,4)
fig = plt.figure(facecolor='lightgray')
fig, ax = plt.subplots(figsize=figsize)
ax.plot(top_manu['Manufacturer'], top_manu['weighted_price'], marker='o', linestyle='-', color='b')
ax.set_xlabel('Manufacturer')
ax.set_ylabel('Sales')
ax.set_title('Top 5 Manufacturer Sales')
plt.xticks(rotation=45)
st.pyplot(fig)