#libraries

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

filename = 'data/Input_Sales_Data_v2.csv'
logo_image = 'images/logo.jpg'

df = pd.read_csv(filename)



st.set_page_config(
        page_title="Sales App",
       initial_sidebar_state="expanded",  
       page_icon="🧊",
       )


menu_selection = st.sidebar.selectbox("Menu:", ["First Page", "Second Page"])
if menu_selection == "First Page":
   
    st.title("Sales App")
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
    plt.xticks(rotation=90)
    st.pyplot(fig)

else:
     
     st.title('Detailed Sales Analysis')
     categories = tuple(df['Category'].unique())
     manufacturers = tuple(df['Manufacturer'].unique())
     brands = tuple(df['Brand'].unique())
     col1, col2, col3 = st.columns(3)
     with col1:
         cat_option = st.selectbox('Categories',categories)
     with col2:
         manu_option =  st.selectbox('Manufacturer',manufacturers)
     with col3:
         brand_option = st.selectbox('Brand', brands)

     met1, met2, met3 = st.columns(3)
      

     fil_df = df[(df['Category']==cat_option) & (df['Manufacturer']==manu_option) & (df['Brand']==brand_option)]     
     volume_sales = df.agg(Volume_Sales=('Volume','sum')).values
     sales = df.agg(YTD_Sales=('Price','sum')).values
     skus = df['SKU Name'].nunique()

     with met1:
         st.metric(label="YTD Volume", value=volume_sales)   
     with met2:
         st.metric(label="YTD Sales", value=sales) 
     with met3:
         st.metric(label="#SKUs", value=skus)
      
     line_col, pie_col = st.columns(2)

     with line_col:
         volume_value_df = df[['Date','Volume','Value']]
         volume_value_df['Date'] = pd.to_datetime(volume_value_df['Date'])
         volume_value_df.set_index('Date',inplace=True)
         weekly_sales = volume_value_df.resample('W-Mon').sum()
         fig, ax1 = plt.subplots()
         ax1.plot(weekly_sales.index, weekly_sales['Volume'], marker='o', color='tab:blue', label='Volume')
         ax1.set_xlabel('Week')
         ax1.set_ylabel('Volume', color='tab:blue')
         ax1.tick_params(axis='y', labelcolor='tab:blue')
         ax1.legend(loc='upper left')
         ax2 = ax1.twinx()
         ax2.plot(weekly_sales.index, weekly_sales['Value'], marker='s', color='tab:orange', label='Value')
         ax2.set_ylabel('Value', color='tab:orange')
         ax2.tick_params(axis='y', labelcolor='tab:orange')
         ax2.legend(loc='upper right')

         fig.tight_layout()
         st.pyplot(fig)
     with pie_col:
        brand_df = df[df['Brand']==brand_option]
        top_10_skus = brand_df.groupby('SKU Name').agg(total_price=('Price','sum')).sort_values('total_price').tail(10).reset_index()
        fig, ax = plt.subplots()
        
        ax.pie(top_10_skus['total_price'], labels=top_10_skus['SKU Name'], autopct='%1.1f%%', startangle=45)
        plt.tight_layout()
        ax.axis('equal') 
        st.pyplot(fig)

     vol_col, val_col = st.columns(2)
     with vol_col:
           
           fig, ax1 = plt.subplots()
           ax1.plot(df.index, df['Price'], color='tab:blue', marker='o', label='Price')
           ax1.set_xlabel('Date')
           ax1.set_ylabel('Price', color='tab:blue')
           ax1.tick_params(axis='y', labelcolor='tab:blue')
           ax1.legend(loc='upper left')
           ax2 = ax1.twinx()
           ax2.plot(df.index, df['Volume'], color='tab:orange', marker='s', label='Volume')
           ax2.set_ylabel('Volume', color='tab:orange')
           ax2.tick_params(axis='y', labelcolor='tab:orange')
           ax2.legend(loc='upper right')

           fig.tight_layout()
           st.pyplot(fig)

     with val_col:
           fig, ax1 = plt.subplots()
           ax1.plot(df.index, df['Price'], color='tab:blue', marker='o', label='Price')
           ax1.set_xlabel('Date')
           ax1.set_ylabel('Price', color='tab:blue')
           ax1.tick_params(axis='y', labelcolor='tab:blue')
           ax1.legend(loc='upper left')
           ax2 = ax1.twinx()
           ax2.plot(df.index, df['Value'], color='tab:orange', marker='s', label='Value')
           ax2.set_ylabel('Value', color='tab:orange')
           ax2.tick_params(axis='y', labelcolor='tab:orange')
           ax2.legend(loc='upper right')
           

           fig.tight_layout()
           st.pyplot(fig)   
            
     #sku multiselect
     sku_list = list(df['SKU Name'].unique())
     sku_options = st.multiselect('Select SKUs', sku_list)
     sku_filtered_df = df[df['SKU Name'].isin(sku_options)]

     sku_line, sku_bar = st.columns(2)
     


            
            
    
    

         
         





