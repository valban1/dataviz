import pandas as pd
import altair as alt
from altair import expr, datum
from vega_datasets import data
import datetime as dt
import streamlit as st

st.write('# Fake News on the Internet')

st.write('## 1. Load data')
# Load Gapminder data
# @st.cache decorator skip reloading the code when the app
@st.cache
def loadData():
    return pd.read_csv('top-2018-cleaned1.csv')

df = loadData()

# Use st.write() to render any objects on the web app
st.write('This is dataset table.')
st.write(df)

# Magic command: Streamlit automatically writes a variable 
# or a literal value to your app using st.write().
'List of columns in the table.'
df.columns.values

st.write('#### This is the first chart we created.')

#@st.cache(allow_output_mutation=True)

def pre_process(df):
	df = df[df['published_date'].str.contains("2018")].reset_index(drop=True)
	df['published_date'] = pd.to_datetime(df['published_date'])
	df['month'] = df['published_date'].dt.to_period('M').astype(str)
	df['month'] = pd.to_datetime(df['month'])
	df['month_int'] = [df['month'][x].month for x in range(len(df['month']))]
	df['year_int'] = [df['month'][x].year for x in range(len(df['month']))]

	return df

df = pre_process(df)
alt.data_transformers.disable_max_rows()

df_engagement_month_origin = df.groupby(['Origin','month_int'])['fb_engagement'].sum().reset_index()
df_engagement_month_origin['Rank'] = df_engagement_month_origin.groupby('month_int')['fb_engagement'].rank('dense', ascending = False)
df_engagement_month_origin = df_engagement_month_origin[df_engagement_month_origin['Rank'] <= 10]
df_engagement_month_origin = df_engagement_month_origin.sort_values('month_int')

engagement_per_origin = alt.Chart(df_engagement_month_origin).mark_bar().encode(
    x='sum(fb_engagement):Q',
    y=alt.Y('Origin:N',sort='-x'),
    color='Origin:N',
    tooltip='sum(fb_engagement):Q'
).interactive()

# Showing Altair chart on the apps
st.altair_chart(engagement_per_origin, use_container_width=False)

