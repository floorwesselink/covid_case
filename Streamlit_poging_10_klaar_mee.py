#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import numpy as np
import geopandas as gpd
import pandas as pd
import folium
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pycountry
import pycountry_convert as pc
import requests
import io


# # Inladen dataframes

# In[2]:


#Dataframes boxplots
cases_continenten = pd.read_csv('cases_continenten.csv')
tests_continenten = pd.read_csv('tests_continenten.csv')
vac_continenten = pd.read_csv('vac_continenten.csv')
deaths_continenten = pd.read_csv('deaths_continenten.csv')


# In[5]:


#Dataframes kaarten
cases_population = pd.read_csv('cases_population.csv')
deaths_population = pd.read_csv('deaths_population.csv')
tests_population = pd.read_csv('tests_population.csv')
vaccinations_population = pd.read_csv('vaccinations_population.csv')


# In[7]:


#Lijnplots
df_cases_lijn = pd.read_csv('df_cases_lijn.csv')
df_tests_lijn = pd.read_csv('df_tests_lijn.csv')
df_vac_lijn = pd.read_csv('df_vac_lijn.csv')
df_d_lijn = pd.read_csv('df_d_lijn.csv')
df_europa = pd.read_csv('df_europa.csv')
total_vac_europa = pd.read_csv('total_vac_europa.csv')


# # Streamlit

# In[22]:


st.title('Verloop Covid-19 pandemie')


# ## Boxplots

# In[8]:


st.header('Boxplots van Corona gevallen, testen, vaccinaties en sterfgevallen per continent')


# In[9]:


select_box_variabelen_box = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 30)


# In[10]:


#Boxplots continenten
if select_box_variabelen_box == 'Corona gevallen':
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Totaal aantal gevallen per land', 'Gevallen per honderd duizend inwoners'])
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Totaal aantal gevallen per land':
        kolom = 'total_cases'
    elif schaal == 'Gevallen per honderd duizend inwoners':
        kolom = 'cases_honderdduizend'    
    
    #Maken van figuur
    fig = px.box(cases_continenten, x=kolom, color = 'continent',
             title = 'Covid-19 gevallen per continent', hover_data = ['location'])
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Aantal gevallen')
        
    st.plotly_chart(fig)
    
    
    
   ##Corona testen   

elif  select_box_variabelen_box == 'Corona testen':
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Totaal aantal testen per land', 'Testen per honderd duizend inwoners'])
    
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Totaal aantal testen per land':
        kolom = 'total_tests'
    elif schaal == 'Testen per honderd duizend inwoners':
        kolom = 'tests_honderdduizend'        
    
    #Maken van figuur      
    fig = px.box(tests_continenten, x=kolom, color = 'continent',
             title = 'Verdeling Covid-19 testen per continent', hover_data = ['location'])
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Aantal testen')

    st.plotly_chart(fig)

    
     ##Corona vaccinaties
    
elif  select_box_variabelen_box == 'Corona vaccinaties':    
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Totaal aantal vaccinaties per land', 'Vaccinaties per honderd duizend inwoners'])
    
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Totaal aantal vaccinaties per land':
        kolom = 'total_vaccinations'
    elif schaal == 'Vaccinaties per honderd duizend inwoners':
        kolom = 'vac_honderdduizend'        
    
    #Maken van figuur      
    fig = px.box(vac_continenten, x=kolom, color = 'continent',
             title = 'Verdeling Covid-19 vaccinaties per continent', hover_data = ['location'])
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Aantal vaccinaties')

    st.plotly_chart(fig)
    
    
    ##Corona sterfgevallen
elif  select_box_variabelen_box == 'Corona doden':
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Totaal aantal sterfgevallen per land', 'sterfgevallen per honderd duizend inwoners'])
    
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Totaal aantal sterfgevallen per land':
        kolom = 'total_deaths'
    elif schaal == 'Sterfgevallen per honderd duizend inwoners':
        kolom = 'deaths_honderdduizend'        
    
    #Maken van figuur      
    fig = px.box(deaths_continenten, x=kolom, color = 'continent',
             title = 'Verdeling Covid-19 sterfgevallen per continent', hover_data = ['location'])
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Aantal sterfgevallen')

    st.plotly_chart(fig)


    


# ## Code kaart

# In[11]:


st.header('Kaart over Corona gevallen, testen, vaccinaties en stergevallen per maand')


# In[12]:


select_box_variabelen = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 10)

st.write('Variabele: ', select_box_variabelen)


# In[13]:


##Kiezen van de variabele uit de select box

#Corona gevallen
if select_box_variabelen =='Corona gevallen':
    
    #Slider voor maand
    start_time_cases = st.select_slider(
    'Datum: ',
    options=cases_population['month_year'].unique(), key = 2)
    
    
    #Juiste dataframe kiezen
    df_cases_map = cases_population[cases_population['month_year']==start_time_cases]
    
    #Keuze schaal
    schaal = st.radio('Schaal: ', ['Nieuwe corona gevallen', 'Corona gevallen per inwoner', 'Corona gevallen per miljoen inwoners', 'Corona gevallen per tien miljoen inwoners'])
    if schaal == 'Nieuwe corona gevallen':
        kolom = 'new_cases_smoothed'
        
    elif schaal == 'Corona gevallen per inwoner':
        kolom = 'cases_person'
        
    elif schaal == 'Corona gevallen per miljoen inwoners':
        kolom = 'per_milion'
        
    elif schaal =='Corona gevallen per tien miljoen inwoners':
        kolom = 'per_ten_million'
        
    
    #Plotten van het figuur
    fig_cases = px.choropleth(df_cases_map, locations='iso_code', color=f'{kolom}',
                           color_continuous_scale='YlOrRd',
                           scope="world",
                           locationmode = 'ISO-3',
                           labels={'total_cases':'total cases'})
    fig_cases.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                           coloraxis_colorbar={
                            'title': 'Aantal ' + f'{schaal.lower()}'})
    
    st.plotly_chart(fig_cases)


#Corona doden
elif select_box_variabelen == "Corona doden":
    
    #Slider voor de maand
    start_time_deaths = st.select_slider(
    'Datum: ',
    options=deaths_population['month_year'].unique(), key = 1)
    
    
    #Juiste dataframe kiezen
    df_deaths_map = deaths_population[deaths_population['month_year']==start_time_deaths]
    
    #Keuze schaal 
    schaal = st.radio('Schaal: ', ['Nieuwe corona doden', 'Corona doden per inwoner', 'Corona doden per miljoen inwoners', 'Corona doden per tien miljoen inwoners'])
    if schaal == 'Nieuwe corona doden':
        kolom = 'new_deaths_smoothed'
        maxi = max_deaths
    elif schaal == 'Corona doden per inwoner':
        kolom = 'deaths_person'
        maxi = max_deaths_person
    elif schaal == 'Corona doden per miljoen inwoners':
        kolom = 'per_milion'
        maxi = max_deaths_milion
    elif schaal =='Corona doden per tien miljoen inwoners':
        kolom = 'per_ten_million'
        maxi = max_deaths_ten_milion
    
    
    #Plotten van het figuur
    fig_deaths = px.choropleth(df_deaths_map, locations='iso_code', color=f'{kolom}',
                           color_continuous_scale='YlOrRd',
                           scope="world",
                           locationmode = 'ISO-3',
                           labels={'total_cases':'total cases'})
    fig_deaths.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                            coloraxis_colorbar={
                            'title': 'Aantal ' + f'{schaal.lower()}'})
    st.plotly_chart(fig_deaths)

    
#Corona testen
elif select_box_variabelen=='Corona testen':
    
    #Slider voor de maand
    start_time_tests = st.select_slider(
    'Datum: ',
    options=tests_population['month_year'].unique(), key = 3)
    
    
    #Juiste dataframe kiezen
    df_tests_map = tests_population[tests_population['month_year']==start_time_tests]
    
    #Keuze schaal
    schaal = st.radio('Schaal: ', ['Nieuwe corona testen', 'Corona testen per inwoner', 'Corona testen per miljoen inwoners', 'Corona testen per tien miljeon inwoners'])
    if schaal == 'Nieuwe corona testen':
        kolom = 'new_tests_smoothed'
        maxi = max_tests
    elif schaal == 'Corona testen per inwoner':
        kolom = 'tests_person'
        maxi = max_tests_person
    elif schaal == 'Corona testen per miljoen inwoners':
        kolom = 'per_milion'
        maxi = max_tests_milion
    elif schaal =='Corona testen per tien miljeon inwoners':
        kolom = 'per_ten_million'
        maxi = max_tests_ten_milion
    
    #Plotten van het figuur
    fig_tests = px.choropleth(df_tests_map, locations='iso_code', color=f'{kolom}',
                           color_continuous_scale='YlOrRd',
                           scope="world",
                           locationmode = 'ISO-3',
                           labels={'total_cases':'total cases'})
    fig_tests.update_layout(
                    margin={'r':0,'t':0,'l':0,'b':0},
                    coloraxis_colorbar={
                            'title': 'Aantal ' + f'{schaal.lower()}'})
                             
    st.plotly_chart(fig_tests)

    
#Corona vaccinaties
elif select_box_variabelen=='Corona vaccinaties':
    start_time_vaccinations = st.select_slider(
    'Datum: ',
    options=vaccinations_population['month_year'].unique(), key = 4)
    
    
    #Juiste dataframe kiezen
    df_vaccinations_map = vaccinations_population[vaccinations_population['month_year']==start_time_vaccinations]
    
    #Keuze schaal
    schaal = st.radio('Schaal: ', ['Nieuwe vaccinaties', 'Vaccinaties per inwoner', 'Vaccinaties per miljoen inwoners', 'Vaccinaties per tien miljoen inwoners'])
    if schaal == 'Nieuwe vaccinaties':
        kolom = 'new_vaccinations_smoothed'
        maxi = max_vaccinations
    elif schaal == 'Vaccinaties per inwoner':
        kolom = 'vaccinations_person'
        maxi = max_vaccinations_person
    elif schaal == 'Vaccinaties per miljoen inwoners':
        kolom = 'per_milion'
        maxi = max_vaccinations_milion
    elif schaal =='Vaccinaties per tien miljoen inwoners':
        kolom = 'per_ten_million'
        maxi = max_vaccinations_ten_milion
        
    #Plotten van het figuur   
    fig_vaccinations = px.choropleth(df_vaccinations_map, locations='iso_code', color=f'{kolom}',
                           color_continuous_scale='YlOrRd',
                           scope="world",
                           locationmode = 'ISO-3',
                           labels={'total_cases':'total cases'})
    fig_vaccinations.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                                  coloraxis_colorbar={
                            'title': 'Aantal ' + f'{schaal.lower()}'})
    st.plotly_chart(fig_vaccinations)



# ## Lijnplotten

# In[14]:


st.header('Lijnplot over Corona gevallen, testen, vaccinaties en stergevallen per continent')


# In[15]:


select_box_variabelen_lijn = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 22)

st.write('Variabele: ', select_box_variabelen_lijn)


# In[16]:


##Coronagevallen

if select_box_variabelen_lijn == 'Corona gevallen':
    
    df_cases_lijn['month_year'] = df_cases_lijn['month_year'].astype(str)
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Nieuwe corona gevallen', 'Corona gevallen per inwoner', 'Corona gevallen per honderd duizend inwoners'])
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Nieuwe corona gevallen':
        kolom = 'new_cases_smoothed'
    elif schaal == 'Corona gevallen per inwoner':
        kolom = 'cases_person'
    elif schaal == 'Corona gevallen per honderd duizend inwoners':
        kolom = 'cases_hundred_duizend'
    
    
    #Maken van figuur
    fig = px.line(df_cases_lijn, x = 'month_year', y = kolom, title='Covid-19 gevallen per continent', color = 'continent')
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Tijd',
                   yaxis_title='Aantal gevallen')
    
    st.plotly_chart(fig)


##Corona testen   

elif  select_box_variabelen_lijn == 'Corona testen':
    
    df_tests_lijn['month_year'] = df_tests_lijn['month_year'].astype(str)
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Nieuwe corona testen', 'Corona testen per inwoner', 'Corona testen per honderd duizend inwoners'])
    
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Nieuwe corona testen':
        kolom = 'new_tests_smoothed'
    elif schaal == 'Corona testen per inwoner':
        kolom = 'tests_person'
    elif schaal == 'Corona testen per honderd duizend inwoners':
        kolom = 'tests_hundred_duizend'
        
    
    #Maken van figuur
    fig = px.line(df_tests_lijn, x = 'month_year', y = kolom, 
              title='Covid-19 testen per continent', color = 'continent')
    
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Tijd',
                   yaxis_title='Aantal testen')
    
    st.plotly_chart(fig)

    
##Corona vaccinaties

elif select_box_variabelen_lijn == 'Corona vaccinaties':
    
    df_vac_lijn['month_year'] = df_vac_lijn['month_year'].astype(str)
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Nieuwe corona vaccinaties', 'Corona vaccinaties per inwoner', 'Corona vaccinaties per honderd duizend inwoners'])
    
    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Nieuwe corona vaccinaties':
        kolom = 'new_vaccinations_smoothed'
    elif schaal == 'Corona vaccinaties per inwoner':
        kolom = 'vac_person'
    elif schaal == 'Corona vaccinaties per honderd duizend inwoners':
        kolom = 'vac_hundred_duizend'


    
    #Maken van figuur
    fig = px.line(df_vac_lijn, x = 'month_year', y = kolom, 
                  title='Vaccinaties per continent', color = 'continent')
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Tijd',
                   yaxis_title='Aantal vaccinaties')

    
    st.plotly_chart(fig)

    
##Corona doden

elif select_box_variabelen_lijn == 'Corona testen per honderd duizend inwoners':
    
    df_d_lijn['month_year'] = df_d_lijn['month_year'].astype(str)
    
    #Schaal kiezen
    schaal = st.radio('Schaal: ', ['Nieuwe corona doden', 'Corona doden per inwoner', 'Corona doden per honderd duizend inwoners'])

    
    #Juiste kolom kiezen uit dataframe
    if schaal == 'Nieuwe corona doden':
        kolom = 'new_deaths_smoothed'
    elif schaal == 'Corona doden per inwoner':
        kolom = 'd_person'
    elif schaal == 'Corona doden per honderd duizend inwoners':
        kolom = 'd_hundred_duizend'
    
    
    #Maken van figuur
    fig = px.line(df_d_lijn, x = 'month_year', y = kolom,
                  title='Sterfgevallen per continent', color = 'continent')
    fig.update_layout(legend_title_text='Continenten', xaxis_title='Tijd',
                   yaxis_title='Aantal Sterfgevallen')
    
    st.plotly_chart(fig)
        


# In[17]:


st.header('Lijnplot over Corona gevallen, testen, vaccinaties en sterfgevallen in Europa')


# In[18]:


logaritmische_schaal = st.checkbox('Logaritmische schaal')

if logaritmische_schaal:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_vaccinations_smoothed'], mode = 'lines', name = 'Vaccinaties'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_cases_smoothed'], mode = 'lines', name = 'Gevallen'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_tests_smoothed'], mode = 'lines', name = 'Testen'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_deaths_smoothed'], mode = 'lines', name = 'Sterfgevallen'))
    fig.update_layout(legend_title_text='Legenda', xaxis_title='Tijd',
                   yaxis_title='Aantallen', title_text = 'Verloop van de Covid-19 pandemie in Europa')
    fig.update_yaxes(type= 'log')
    st.plotly_chart(fig)
    
else:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_vaccinations_smoothed'], mode = 'lines', name = 'Vaccinaties'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_cases_smoothed'], mode = 'lines', name = 'Gevallen'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_tests_smoothed'], mode = 'lines', name = 'Testen'))
    fig.add_trace(go.Scatter(x = df_europa['month_year'], y = df_europa['new_deaths_smoothed'], mode = 'lines', name = 'Sterfgevallen'))
    fig.update_layout(legend_title_text='Legenda', xaxis_title='Tijd',
                   yaxis_title='Aantallen', title_text = 'Verloop van de Covid-19 pandemie in Europa')
    st.plotly_chart(fig)
    


# ## voorspelling

# In[19]:


st.header('Sterfgevallen ten op zichte van vaccinaties')


# In[21]:


fig_scatter = px.scatter(total_vac_europa, x = 'total_vaccinations', y = 'total_deaths', hover_data = ['month_year'])
fig_scatter.update_layout(xaxis_title = 'Totale vaccinaties', yaxis_title = 'Totaal sterftegevallen', title_text = 'Verband tussen vaccinaties en sterfgevallen')
st.plotly_chart(fig_scatter)


# In[ ]:




