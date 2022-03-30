import pandas as pd
import altair as alt
from altair import expr, datum
from vega_datasets import data
import datetime as dt
import streamlit as st

st.write('# Fake News on the Internet - BuzzFeed News Dataset')

# @st.cache decorator skip reloading the code when the app
@st.cache
def loadData():
    return pd.read_csv('top-2018-cleaned1.csv')

df = loadData()

#st.write('#### This is the first chart we created.')

#@st.cache(allow_output_mutation=True)

# Pre-process dataframe
@st.cache
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

# Define first graph - Daily publications
@st.cache(allow_output_mutation=True)
def graph1(df):
	fake_news_daily = alt.Chart(df).mark_line().encode(
    	x='published_date:T',
    	y=alt.Y('count(titre):Q'),
    	tooltip=['published_date:T', 'count(titre):Q', 'sum(fb_engagement):Q']
	).interactive()

	return fake_news_daily

# Showing Altair chart on the apps
fake_news_daily = graph1(df)

# Define second graph - Daily publication per domain name
@st.cache(allow_output_mutation=True)
def graph2(df):
	click_domain = alt.selection_multi(encodings=['color']) 
	daily_publi_per_domain = alt.Chart(df).mark_point().encode(
    	x='published_date:T',
    	y='fb_engagement:Q',
    	color='Domain name:N',
    	tooltip=['title:N', 'fb_engagement:Q', 'category:N'] 
	).interactive().add_selection(click_domain).transform_filter(click_domain)

	return daily_publi_per_domain

# Showing Altair chart on the apps
daily_publi_per_domain = graph2(df)

st.altair_chart(fake_news_daily | daily_publi_per_domain, use_container_width=False)

# Create new dataset to show top 10 fake news by category
#@st.cache()
def top10_df(df):
	df_top10 = df.groupby(['category','title'])['fb_engagement'].sum().reset_index()
	df_top10['Rank'] = df_top10.groupby('category')['fb_engagement'].rank('dense', ascending = False)
	df_top10 = df_top10[df_top10['Rank'] <= 10]
	df_top10 = df_top10.sort_values(['category','Rank'], ascending = False)

	return df_top10

df_top10 = top10_df(df)

# Define fourth graph - Repartition of categories per origin
def graph4(df):
	# adding a select to choose the origin
	all_origin = df['Origin'].unique()
	dropdown_origin = alt.binding_select(options= all_origin)
	select_origin = alt.selection_single(fields=['Origin'], bind = dropdown_origin, name = 'Choose')
	# Scatter plot with tooltip and interactive()
	cat_per_origin = alt.Chart(df).mark_bar().encode(
    	x=alt.X('Origin:N',sort ='-y'),
    	y=alt.Y('count(category):Q'),
    	color='category:N',
    	tooltip='count(category):Q'
	).interactive().add_selection(
    	select_origin
	).transform_filter(
    select_origin
	).properties(width=800, height=400)

	return cat_per_origin

cat_per_origin = graph4(df)
st.altair_chart(cat_per_origin)

# Create new df to get the top 10 articles by origin per month (ranking)
def df_engagement_month_origin(df):
	df_engagement_month_origin = df.groupby(['Origin','month_int', 'category'])['fb_engagement'].sum().reset_index()
	df_engagement_month_origin['Rank'] = df_engagement_month_origin.groupby('month_int')['fb_engagement'].rank('dense', ascending = False)
	df_engagement_month_origin = df_engagement_month_origin[df_engagement_month_origin['Rank'] <= 10]
	df_engagement_month_origin = df_engagement_month_origin.sort_values('month_int')

	return df_engagement_month_origin

df_engagement_month_origin = df_engagement_month_origin(df)

# Create new df to get the top 10 articles by category per month (ranking)
def df_engagement_month_category(df):
	df_engagement_month_category = df.groupby(['category','month_int', 'Origin'])['fb_engagement'].sum().reset_index()
	df_engagement_month_category['Rank'] = df_engagement_month_category.groupby('month_int')['fb_engagement'].rank('dense', ascending = False)
	df_engagement_month_category = df_engagement_month_category[df_engagement_month_category['Rank'] <= 10]
	df_engagement_month_category = df_engagement_month_category.sort_values('month_int')

	return df_engagement_month_category

df_engagement_month_category = df_engagement_month_category(df)

# Define fifth graph - Daily fake news publications
def graph5(df):
	# creating the slider
	month_slider = alt.binding_range(min=1, max=12, step=1)
	slider_selection_month = alt.selection_single(bind=month_slider, fields=['month_int'], name='slider')
	click_cat_orig = alt.selection_multi(encodings=['color'])
	# fake_news_daily
	fake_news_daily = alt.Chart(df).mark_point().encode(
    	x=alt.X('yearmonthdate(published_date):T', title = 'Day of publication'),
    	y=alt.Y('count(titre):Q'),
    	color=alt.Color('sum(fb_engagement)',scale=alt.Scale(scheme='goldred')),
    	tooltip=['published_date:T', 'sum(fb_engagement):Q']
	).add_selection(
    	slider_selection_month
	).transform_filter(
    	slider_selection_month)
	fake_news_daily = fake_news_daily.add_selection(click_cat_orig).transform_filter(click_cat_orig)

	return fake_news_daily

# Define sixth graph - Top 10 engagement per origin per month
def graph6(df_engagement_month_origin):
	month_slider = alt.binding_range(min=1, max=12, step=1)
	slider_selection_month = alt.selection_single(bind=month_slider, fields=['month_int'], name='slider')
	click_cat_orig = alt.selection_multi(encodings=['color'])
	engagement_per_origin = alt.Chart(df_engagement_month_origin).mark_bar().encode(
    	x='sum(fb_engagement):Q',
    	y=alt.Y('Origin:N',sort='-x'),
    	color='Origin:N',
    	tooltip='sum(fb_engagement):Q'
	).interactive().add_selection(click_cat_orig).transform_filter(click_cat_orig)
	engagement_per_origin = engagement_per_origin.add_selection(slider_selection_month).transform_filter(slider_selection_month)

	return engagement_per_origin

# Define seventh graph - Top 10 engagement per category per month
def graph7(df_engagement_month_category):
	month_slider = alt.binding_range(min=1, max=12, step=1)
	slider_selection_month = alt.selection_single(bind=month_slider, fields=['month_int'], name='slider')
	click_cat_orig = alt.selection_multi(encodings=['color'])
	engagement_per_category = alt.Chart(df_engagement_month_category).mark_bar().encode(
   		x='sum(fb_engagement):Q',
    	y=alt.Y('category:N',sort='-x'),
    	color = 'category:N',
    	tooltip='sum(fb_engagement):Q'
	).interactive().add_selection(click_cat_orig).transform_filter(click_cat_orig)
	engagement_per_category = engagement_per_category.add_selection(slider_selection_month).transform_filter(slider_selection_month)

	return engagement_per_category

fake_news_daily = graph5(df)
engagement_per_origin = graph6(df_engagement_month_origin)
engagement_per_category = graph7(df_engagement_month_category)

st.altair_chart(fake_news_daily | engagement_per_origin | engagement_per_category)












