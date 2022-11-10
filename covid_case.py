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


# In[2]:


#Titel stramlit
st.title('Verloop Covid-19 pandemie')


# In[3]:


#Df inladen
#df = pd.read_csv('owid-covid-data.csv')


# In[4]:


url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
download = requests.get(url).content

df = pd.read_csv(io.StringIO(download.decode('utf-8')))


# In[5]:


#Relevante kolommen selecteren
df_covid = df[['iso_code', 'location', 'date', 'total_cases', 'new_cases_smoothed', 'total_deaths', 'new_deaths_smoothed', 
               'icu_patients', 'hosp_patients', 'total_tests', 'new_tests', 'new_tests_smoothed', 'total_vaccinations', 
               'people_vaccinated', 'people_fully_vaccinated', 'total_boosters', 'new_vaccinations',
               'new_vaccinations_smoothed', 'stringency_index', 'population_density', 'median_age', 'gdp_per_capita',
               'extreme_poverty', 'handwashing_facilities', 'hospital_beds_per_thousand', 'population', 
               'excess_mortality_cumulative']]


# # H1: new_cases, new_deaths, new_tests & new_vaccinations
# Deze vier variabelen belijken we per maand. We gebruiken de new_smoothed variabelen, aangezien elk land niet elke dag een report doet over het nieuwe aantal gevallen, doden, testen of vaccinaties. De smoothed berekent het gemiddelde per jaar. 
# 1. We voegen een nieuwe kolom toe, met alleen de maand en het jaar. 
# 2. We kijken alleen naar de maanden waarvoor er van meer dan 27 dagen de aantal besmettingen bekend zijn. 
# 3. De landen waarvoor er een bepaalde maand geen gegevens beschikbaar zijn, worden opgevuld met NA waarden. 

# In[6]:


#Maand en jaar selecteren vanuit datum kolom
df_covid['date'] = pd.to_datetime(df_covid['date'])
df_covid['month_year'] = pd.to_datetime(df['date']).dt.to_period('M')


# In[7]:


#new Vaccinations smoothed 7-days
vac_smooth = df_covid[df_covid['new_vaccinations_smoothed'].isna()==False][['iso_code','location','date', 
                                                                            "new_vaccinations_smoothed", 'month_year']]
vac_smooth_days = vac_smooth.groupby(['iso_code', 'month_year']).count()
vac_smooth_27 = list(vac_smooth_days[vac_smooth_days['date']>27].index)
vac_smooth_month = vac_smooth.groupby(['iso_code','month_year'])[['new_vaccinations_smoothed']].sum()
vac_smooth_total = vac_smooth_month[vac_smooth_month.index.isin(vac_smooth_27)==True]

df_vaccinations = vac_smooth_total.reindex(pd.MultiIndex.from_product(vac_smooth_total.index.levels)).reset_index()


# In[8]:


#new tests smoothed 7-days
tests = df_covid[df_covid['new_tests_smoothed'].isna()==False][['iso_code', 'location', 'date', 'new_tests_smoothed', 
                                                                'month_year']]
tests_days = tests.groupby(['iso_code', 'month_year']).count()
tests_days_27 = list(tests_days[tests_days['date']>27].index)
tests_month = tests.groupby(['iso_code', 'month_year'])[['new_tests_smoothed']].sum()
tests_total = tests_month[tests_month.index.isin(tests_days_27)==True]

df_tests = tests_total.reindex(pd.MultiIndex.from_product(tests_total.index.levels)).reset_index()


# In[9]:


#test dataframe maken met locaties
locaties_tests = df_covid[df_covid['new_tests_smoothed'].isna()==False][['iso_code', 'location']].drop_duplicates()
test_merge = df_tests.merge(locaties_tests, on = 'iso_code', how = 'left')


# In[10]:


#new cases smoothed 7-days
cases = df_covid[df_covid['new_cases_smoothed'].isna()==False][['iso_code', 'location', 'date', 'new_cases_smoothed', 
                                                                'month_year']]
cases_days  = cases.groupby(['iso_code', 'month_year']).count()
cases_days_27 = list(cases_days [cases_days ['date']>27].index)
cases_month = cases.groupby(['iso_code', 'month_year'])[['new_cases_smoothed']].sum()
cases_total = cases_month[cases_month.index.isin(cases_days_27)==True]


df_cases = cases_total.reindex(pd.MultiIndex.from_product(cases_total.index.levels)).reset_index()


# In[11]:


#new deaths smoothed 7-days
deaths = df_covid[df_covid['new_deaths_smoothed'].isna()==False][['iso_code', 'location', 'date', 'new_deaths_smoothed', 
                                                                  'month_year']]
deaths_days  = deaths.groupby(['iso_code', 'month_year']).count()
deaths_days_27 = list(deaths_days[deaths_days['date']>27].index)
deaths_month = deaths.groupby(['iso_code', 'month_year'])[['new_deaths_smoothed']].sum()
deaths_total = deaths_month[deaths_month.index.isin(deaths_days_27)==True]


df_deaths = deaths_total.reindex(pd.MultiIndex.from_product(deaths_total.index.levels)).reset_index()


# # H2: icu_patients & hosp_patients
# 
# Voor sommige landen is er geen icu data beschikbaar, deze hebben 0 icu_patienten als alles wordt opgeteld. 
# 
# We filteren het dataframe op de landen waarvoor icu data bekend is. 
# 1. Eerst de range bepalen van de minimale datum (08-01-2020) en de maximale datum (01-11-2022). 
# 2. Uiteindelijk heeft elk land deze range met datums, om alles tegelijk te houden. 

# In[12]:


hoi = df_covid.groupby('iso_code').count().sort_values(by = 'icu_patients')


# In[13]:


#icu
icu = df_covid[df_covid['icu_patients'].isna()==False]
icu_date = icu.groupby(['iso_code', 'date']).count()
iso_code, datum = zip(*icu_date.index)

begin_date = datetime.datetime.strptime("08-1-2020", "%d-%m-%Y")
eind_date = datetime.datetime.strptime("01-11-2022", "%d-%m-%Y")
date_range = pd.date_range(start = begin_date, end = eind_date)
date_range_df = pd.DataFrame(date_range, columns = ['date'])

#hsp
hsp = df_covid[df_covid['hosp_patients'].isna()==False]
hsp_date = hsp.groupby(['iso_code', 'date']).count()
iso_code_hsp, datum_hsp = zip(*hsp_date.index)

date_range_hsp = pd.date_range(start = min(datum_hsp), end = max(datum_hsp))
df_date_range_hsp = pd.DataFrame(date_range_hsp, columns = ['date'])


# ## H2.1: icu_patiens definitief
# 1. Lijst met alle iso_code waarvan er icu patiënten bekend zijn, waarover we kunnen loopen.(list_iso_icu)
# 2. Maken van leeg dataframe met de drie variabelen die nodig zijn. (df_covid_icu)
# 
# Nu de for loop
# 1. Dataframe wordt gepakt waar alleen het destbetreffende land in zit (df). 
# 2. De eerste datum wordt bepaald, waarop er icu patienten zijn genoteerd.
# 3. De laatste datum wordt bepaald, waarop er icu patienten zijn genoteerd.
# 4. Hier wordt een datum range van gemaakt.
# 5. Deze wordt gemerged, zodat we voor elke dag in die periode een datum hebben. De onbekende waarde worden gevuld met forward filling. 
# 6. Vervolgens wordt aan dit dataframe alle missende datums van de volledige dataframe aan toegevoegd. Zodat elk land evenveel datums tot zijn beschikking heeft. 
# 7. De missende aantallen voor deze datums worden niet ingevuld. 
# 8. Uiteindelijk wordt hier een nieuw data frame van gemaakt. 

# In[14]:


list_iso_icu = icu['iso_code'].unique()
df_covid_icu = pd.DataFrame(columns = ['iso_code', 'date', 'icu_patients'])

for iso in list_iso_icu:
    df = icu[icu['iso_code']==iso][['iso_code', 'date', 'icu_patients']]
    begin = df['date'].min()
    eind = df['date'].max()
    date_range = pd.date_range(start = begin, end = eind)
    date_df = pd.DataFrame(date_range, columns = ['date'])
    df_date_range = df.merge(date_df, on = 'date', how = 'right')
    df_new = df_date_range.fillna(method = 'ffill')
    df_new_range = df_new.merge(date_range_df, on = 'date', how = 'right')
    df_new_range['iso_code']=iso
    df_covid_icu = df_covid_icu.append(df_new_range, ignore_index = False)
    



# ## H2.2: hsp_patients
# Zelfde beschrijving als icu_patients alleen dan met hsp patients

# In[15]:


list_iso_hsp = hsp['iso_code'].unique()
df_covid_hsp = pd.DataFrame(columns = ['iso_code', 'date', 'hosp_patients'])

for iso in list_iso_hsp:
    df = hsp[hsp['iso_code']==iso][['iso_code', 'date', 'hosp_patients']]
    date_range = pd.date_range(start = df['date'].min(), end = df['date'].max())
    date_df = pd.DataFrame(date_range, columns = ['date'])
    df_date_range = df.merge(date_df, on = 'date', how = 'right')
    df_new = df_date_range.fillna(method = 'ffill')
    df_new_range = df_new.merge(df_date_range_hsp, on = 'date', how = 'right')
    df_new_range['iso_code']=iso
    df_covid_hsp = df_covid_hsp.append(df_new_range)


# ## H3.1 Dataframes voor de kaart

# In[16]:


#df_deaths voor kaart

population = df_covid[['iso_code', 'date', 'population']]
population_df = population.groupby('iso_code')[['population']].mean().reset_index()
deaths_population = df_deaths.merge(population_df, on = 'iso_code')

deaths_population['deaths_person'] = deaths_population['new_deaths_smoothed']/ deaths_population['population']
deaths_population['per_milion'] = deaths_population['deaths_person'] * 1000000
deaths_population['per_ten_million'] = deaths_population['deaths_person'] *10000000

max_deaths = deaths_population['new_deaths_smoothed'].max()
max_deaths_person = deaths_population['deaths_person'].max()
max_deaths_milion = deaths_population['per_milion'].max()
max_deaths_ten_milion = deaths_population['per_ten_million'].max()


# In[17]:


#df_cases voor kaart
cases_population = df_cases.merge(population_df, on = 'iso_code')

cases_population['cases_person'] = cases_population['new_cases_smoothed']/ cases_population['population']
cases_population['per_milion'] = cases_population['cases_person'] * 1000000
cases_population['per_ten_million'] = cases_population['cases_person'] *10000000

max_cases = cases_population['new_cases_smoothed'].max()
max_cases_person = cases_population['cases_person'].max()
max_cases_milion = cases_population['per_milion'].max()
max_cases_ten_milion = cases_population['per_ten_million'].max()


# In[18]:


#df_vaccinations
vaccinations_population = df_vaccinations.merge(population_df, on='iso_code')

vaccinations_population['vaccinations_person'] = vaccinations_population['new_vaccinations_smoothed']/ vaccinations_population['population']
vaccinations_population['per_milion'] = vaccinations_population['vaccinations_person'] * 1000000
vaccinations_population['per_ten_million'] = vaccinations_population['vaccinations_person'] *10000000

max_vaccinations = vaccinations_population['new_vaccinations_smoothed'].max()
max_vaccinations_person = vaccinations_population['vaccinations_person'].max()
max_vaccinations_milion = vaccinations_population['per_milion'].max()
max_vaccinations_ten_milion = vaccinations_population['per_ten_million'].max()


# In[19]:


#df_tests

tests_population = df_tests.merge(population_df, on = 'iso_code')

tests_population['tests_person'] = tests_population['new_tests_smoothed']/tests_population['population']
tests_population['per_milion'] = tests_population['tests_person'] * 1000000
tests_population['per_ten_million'] = tests_population['tests_person'] *10000000

max_tests = tests_population['new_tests_smoothed'].max()
max_tests_person = tests_population['tests_person'].max()
max_tests_milion = tests_population['per_milion'].max()
max_tests_ten_milion = tests_population['per_ten_million'].max()


# ## H3.2 Dataframes voor de lijnplots

# In[20]:


#Lijnplot maken cases totaal & functie voor bepalen populatie
def population(iso_code):
    population = df_covid[df_covid['iso_code']==iso_code]['population'].reset_index(drop=True)[0]
    return population


# ### De dataframes die worden gebruikt voor de lijnplots Wereld

# In[21]:


#CASES

continenten = ['OWID-AFR', 'OWID_ASI', 'OWID_EUR', 'OWID_OCE', 'OWID_SAM', 'OWID_NAM']
df_cases_lijn = df_cases[df_cases['iso_code'].isin(continenten)]
conti_names1 = {'OWID_ASI': 'Azie',
              'OWID_SAM': 'Zuid-America',
              'OWID_OCE': 'Oceanië',
              'OWID_EUR': 'Europa',
              'OWID_NAM': 'Noord-America',
              'OWID-AFR': 'Afrika'}
df_cases_lijn['continent'] = df_cases_lijn['iso_code'].map(conti_names1)
df_cases_lijn = df_cases_lijn.assign(populatie = lambda x: x['iso_code'].apply(population))
df_cases_lijn['cases_person'] = df_cases_lijn['new_cases_smoothed']/df_cases_lijn['populatie']
df_cases_lijn['cases_hundred_duizend'] = df_cases_lijn['cases_person'] *100000



# In[22]:


#TESTEN

#Landen in continent plaatsen
def convert(row):
    cn_code = pc.country_name_to_country_alpha2(row.location, cn_name_format = 'default')
    conti_code = pc.country_alpha2_to_continent_code(cn_code)
    return conti_code

#Niet erkende landen verwijderen
test_merge = test_merge[test_merge['location'] != "Cote d'Ivoire"]
test_merge = test_merge[test_merge['location'] != 'Democratic Republic of Congo']
test_merge = test_merge[test_merge['location'] != 'Curacao']
test_merge = test_merge[test_merge['location'] != 'Faeroe Islands']
test_merge = test_merge[test_merge['location'] != 'Kosovo']
test_merge = test_merge[test_merge['location'] != 'Timor']

#Continent kolom toevoegen
test_merge['continent'] = test_merge.apply(convert, axis = 1)
conti_names = {'AS': 'Azie',
              'SA': 'Zuid-America',
              'OC': 'Oceanië',
              'EU': 'Europa',
              'NA': 'Noord-America',
              'AF': 'Afrika'}
test_merge['continent'] = test_merge['continent'].map(conti_names)

#De dataset die gebruikt wordt met de lijnplot, populatie nog toevoegen en andere schalen
df_tests_lijn = test_merge.groupby(['month_year', 'continent'])[['new_tests_smoothed']].sum().reset_index()
conti_names2 = {'Azie':population('OWID_ASI'),
              'Zuid-America':population('OWID_SAM'),
              'Oceanië':population('OWID_OCE'),
              'Europa':population('OWID_EUR'),
              'Noord-America':population('OWID_NAM'),
              'Afrika':population('OWID_AFR')}

df_tests_lijn['populatie'] = df_tests_lijn['continent'].apply(lambda x: conti_names2[x] )
df_tests_lijn['tests_person'] = df_tests_lijn['new_tests_smoothed']/df_tests_lijn['populatie']
df_tests_lijn['tests_hundred_duizend'] = df_tests_lijn['tests_person'] *100000



# In[23]:


#VACCINATIONS

df_vac_lijn = df_vaccinations[df_vaccinations['iso_code'].isin(continenten)]
conti_names1 = {'OWID_ASI': 'Azie',
              'OWID_SAM': 'Zuid-America',
              'OWID_OCE': 'Oceanië',
              'OWID_EUR': 'Europa',
              'OWID_NAM': 'Noord-America',
              'OWID_AFR': 'Afrika'}
df_vac_lijn['continent'] = df_vac_lijn['iso_code'].map(conti_names1)
df_vac_lijn = df_vac_lijn.assign(populatie = lambda x: x['iso_code'].apply(population))
df_vac_lijn['vac_person'] = df_vac_lijn['new_vaccinations_smoothed']/df_vac_lijn['populatie']
df_vac_lijn['vac_hundred_duizend'] = df_vac_lijn['vac_person'] *100000


# In[24]:


#DEATHS

df_d_lijn = df_deaths[df_deaths['iso_code'].isin(continenten)]
conti_names1 = {'OWID_ASI': 'Azie',
              'OWID_SAM': 'Zuid-America',
              'OWID_OCE': 'Oceanië',
              'OWID_EUR': 'Europa',
              'OWID_NAM': 'Noord-America',
              'OWID_AFR': 'Afrika'}
df_d_lijn['continent'] = df_d_lijn['iso_code'].map(conti_names1)
df_d_lijn = df_d_lijn.assign(populatie = lambda x: x['iso_code'].apply(population))
df_d_lijn['d_person'] = df_d_lijn['new_deaths_smoothed']/df_d_lijn['populatie']
df_d_lijn['d_hundred_duizend'] = df_d_lijn['d_person'] *100000


# ### Dataframes voor lijnplot Europa

# In[25]:


#Plot Europa met alle data
#Filter de data op Europa
cases_europa = df_cases_lijn[df_cases_lijn['continent'] == 'Europa']
vac_europa = df_vac_lijn[df_vac_lijn['continent'] == 'Europa']
deaths_europa = df_d_lijn[df_d_lijn['continent'] == 'Europa']
tests_europa = df_tests_lijn[df_tests_lijn['continent'] == 'Europa']

#Drop locaties
cases_europa = cases_europa.drop('continent', axis = 1)
vac_europa = vac_europa.drop('continent', axis = 1)
deaths_europa = deaths_europa.drop('continent', axis = 1)
tests_europa = tests_europa.drop('continent', axis = 1)
tests_europa = tests_europa.drop(8, axis = 0)
tests_europa = tests_europa.drop(2, axis = 0)
tests_europa = tests_europa.drop(176, axis = 0)

#Concat tot 1 dataframe
frames = [cases_europa, vac_europa, deaths_europa, tests_europa]
df_europa = pd.concat(frames, ignore_index = True)
df_europa['month_year'] = df_europa['month_year'].astype(str)


# ## H3.3 Boxplot dataframes

# In[26]:


##CASES
cases_count = cases_total.groupby(['iso_code']).count().reset_index()
cases_count['month_count'] = cases_count['new_cases_smoothed']
cases_count = cases_count[['iso_code', 'month_count']]

hist_cases = df_covid[['iso_code', 'total_cases', 'population']].drop_duplicates(subset='iso_code', keep = 'last')

cases_count_1 = cases_count.merge(hist_cases, on = 'iso_code', how = 'left')
cases_count_1['cases_month'] = cases_count_1['total_cases']/cases_count_1['month_count']
cases_count_1['cases_person'] = cases_count_1['cases_month']/cases_count_1['population']
cases_count_1['cases_honderdduizend'] = cases_count_1['cases_person'] * 100000

df_continenten = test_merge.groupby(['iso_code', 'continent']).count().reset_index()
df_continenten = df_continenten[['iso_code', 'continent']]

cases_continenten = cases_count_1.merge(df_continenten, on = 'iso_code', how = 'outer' )
cases_europa = cases_continenten[cases_continenten['continent']=='Europa']


##TESTS
tests_count = tests_total.groupby(['iso_code']).count().reset_index()
tests_count['month_count'] = tests_count['new_tests_smoothed']
tests_count = tests_count[['iso_code', 'month_count']]

hist_tests = df_covid[['iso_code', 'total_tests', 'population']]
hist_tests = hist_tests[hist_tests['total_tests'].isna()==False]
hist_tests = hist_tests.drop_duplicates(subset='iso_code', keep = 'last')

tests_count_1 = tests_count.merge(hist_tests, on = 'iso_code', how = 'left')
tests_count_1['tests_month'] = tests_count_1['total_tests']/tests_count_1['month_count']
tests_count_1['tests_person'] = tests_count_1['tests_month']/tests_count_1['population']
tests_count_1['tests_honderdduizend'] = tests_count_1['tests_person'] * 100000

tests_continenten = tests_count_1.merge(df_continenten, on = 'iso_code', how = 'outer' )
tests_europa = tests_continenten[tests_continenten['continent']=='Europa']


##VACCINATIONS
vac_count = vac_smooth_total.groupby(['iso_code']).count().reset_index()
vac_count['month_count'] = vac_count['new_vaccinations_smoothed']
vac_count = vac_count[['iso_code', 'month_count']]

hist_vac = df_covid[['iso_code', 'total_vaccinations', 'population']]
hist_vac = hist_vac[hist_vac['total_vaccinations'].isna()==False]
hist_vac = hist_vac.drop_duplicates(subset='iso_code', keep = 'last')

vac_count_1 = vac_count.merge(hist_vac, on = 'iso_code', how = 'left')
vac_count_1['vac_month'] = vac_count_1['total_vaccinations']/vac_count_1['month_count']
vac_count_1['vac_person'] = vac_count_1['vac_month']/vac_count_1['population']
vac_count_1['vac_honderdduizend'] = vac_count_1['vac_person'] * 100000

vac_continenten = vac_count_1.merge(df_continenten, on = 'iso_code', how = 'outer' )
vac_europa = vac_continenten[vac_continenten['continent']=='Europa']


##DEATHS
deaths_count = deaths_total.groupby(['iso_code']).count().reset_index()
deaths_count['month_count'] = deaths_count['new_deaths_smoothed']
deaths_count = deaths_count[['iso_code', 'month_count']]

hist_deaths = df_covid[['iso_code', 'total_deaths', 'population']]
hist_deaths = hist_deaths[hist_deaths['total_deaths'].isna()==False]
hist_deaths = hist_deaths.drop_duplicates(subset='iso_code', keep = 'last')

deaths_count_1 = deaths_count.merge(hist_deaths, on = 'iso_code', how = 'left')
deaths_count_1['deaths_month'] = deaths_count_1['total_deaths']/deaths_count_1['month_count']
deaths_count_1['deaths_person'] = deaths_count_1['deaths_month']/deaths_count_1['population']
deaths_count_1['deaths_honderdduizend'] = deaths_count_1['deaths_person'] * 100000

deaths_continenten = deaths_count_1.merge(df_continenten, on = 'iso_code', how = 'outer' )
deaths_europa = deaths_continenten[deaths_continenten['continent']=='Europa']


# In[27]:


#Hover info veranderen naar naam land
landen = test_merge[['iso_code', 'location']]

cases_continenten = cases_continenten.merge(landen, on = 'iso_code', how = 'left')
tests_continenten = tests_continenten.merge(landen, on = 'iso_code', how = 'left')
vac_continenten = vac_continenten.merge(landen, on = 'iso_code', how = 'left')
deaths_continenten = deaths_continenten.merge(landen, on = 'iso_code', how = 'left')


# # H.4 Code voor de analyses

# ## H4.1 Code voor de boxplots

# In[28]:


st.header('Boxplots van Corona gevallen, testen, vaccinaties en sterfgevallen per continent')


# In[29]:


select_box_variabelen_box = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 30)


# In[30]:


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


    


# ## 4.2 Code voor de kaart

# In[31]:


st.header('Kaart over Corona gevallen, testen, vaccinaties en stergevallen per maand')


# In[32]:


select_box_variabelen = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 10)

st.write('Variabele: ', select_box_variabelen)



# In[33]:


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
        maxi = max_cases
    elif schaal == 'Corona gevallen per inwoner':
        kolom = 'cases_person'
        maxi = max_cases_person
    elif schaal == 'Corona gevallen per miljoen inwoners':
        kolom = 'per_milion'
        maxi = max_cases_milion
    elif schaal =='Corona gevallen per tien miljoen inwoners':
        kolom = 'per_ten_million'
        maxi = max_cases_ten_milion
    
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



# ## 4.3 Code voor de lijnplotten

# ### Code voor streamlit lijnplots wereld

# In[34]:


st.header('Lijnplot over Corona gevallen, testen, vaccinaties en stergevallen per continent')


# In[35]:


select_box_variabelen_lijn = st.selectbox('Variabelen',
                                    options = ['Corona gevallen', 'Corona testen', 'Corona doden', 'Corona vaccinaties'], key = 22)

st.write('Variabele: ', select_box_variabelen_lijn)


# In[36]:


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
        


# ### Code voor lijnplots Europa

# In[37]:


st.header('Lijnplot over Corona gevallen, testen, vaccinaties en sterfgevallen in Europa')


# In[38]:


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
    
    
    


# ## 4.4 Voorspelling

# In[39]:


st.header('Sterfgevallen ten op zichte van vaccinaties')


# In[40]:


#Dataframes voor voorspelling
continenten_ziek = test_merge[['iso_code', 'continent']].drop_duplicates(subset = 'iso_code')
totale_vaccinaties = df_covid[['iso_code','date', 'total_vaccinations', 'total_deaths']]
totale_vaccinaties = totale_vaccinaties[totale_vaccinaties['total_vaccinations'].isna()==False]

total_vac_cont = totale_vaccinaties.merge(continenten_ziek, on = 'iso_code', how = 'left')
total_vac_cont = total_vac_cont[total_vac_cont['continent']=='Europa']
total_vac_cont['month_year'] = total_vac_cont['date'].dt.to_period('M')
total_vac = total_vac_cont.groupby(['iso_code', 'month_year'])[['total_vaccinations', 'total_deaths']].sum().reset_index()
total_vac_europa = total_vac.groupby(['month_year'])[['total_vaccinations', 'total_deaths']].sum().reset_index()

total_vac_europa['month_year'] = total_vac_europa['month_year'].astype(str)


# In[41]:


fig_scatter = px.scatter(total_vac_europa, x = 'total_vaccinations', y = 'total_deaths', hover_data = ['month_year'])
fig_scatter.update_layout(xaxis_title = 'Totale vaccinaties', yaxis_title = 'Totaal sterftegevallen', title_text = 'Verband tussen vaccinaties en sterfgevallen')
st.plotly_chart(fig_scatter)


# In[ ]:




