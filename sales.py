#libraries

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

#reading data

st.set_page_config(
        page_title="Sales App",
       initial_sidebar_state="expanded",  
       page_icon="🧊",
       )

filename = 'data/Input_Sales_Data_v2.csv'
logo_image = 'images/logo.jpg'

df = pd.read_csv(filename)

#embedding image
st.sidebar.image(logo_image,use_column_width=False, width=100,clamp=True)
st.markdown("<style>img{float: left;}</style>", unsafe_allow_html=True)

min_date = pd.to_datetime(df['Date'].min()).to_pydatetime()
max_date = pd.to_datetime(df['Date'].max()).to_pydatetime()

categories = tuple(df['Category'].unique())

col1, col2 = st.columns(2)

with col1:
      #slider embedding
      selected_date_range = st.slider("Date Ranges...",
                                    min_value = min_date,
                                    max_value = max_date,
                                    value = (min_date,max_date),
                                    format = "YYYY-MM-DD",
                                    )
with col2:
     # inserting a drop down
     option = st.selectbox('Categories',categories)

# filtering w.r.t date range
df = df[df['Category']==option]
filtered_df = df[(pd.to_datetime(df['Date']) >= selected_date_range[0]) 
                 & (pd.to_datetime(df['Date']) <= selected_date_range[1])]

#manufacturer volume and value sales
df_sales_agg = filtered_df \
                .groupby('Manufacturer') \
                .agg({'Volume':'sum','Value':'sum'}).sort_values(by='Value',ascending=False)
df_sales_agg['market_share'] = df_sales_agg['Value'].apply(lambda x: x*100/df_sales_agg['Value'].sum())
cmap = 'viridis'
df_sales_agg = df_sales_agg.style.background_gradient(cmap=cmap, subset=['market_share'])
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