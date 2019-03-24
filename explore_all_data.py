#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 00:02:01 2018

@author: elenabg
"""
import sys
import time
import pickle
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import re
import csv

df_all = pickle.load(open("df_all.p", "rb")) # cargar dataframe con scraping 1990-2018
df_all.columns=['Description', 'Date', 'Location', 'Victim', 'Alleged_Responsible', 'Type']
df_all.to_csv('data_nn_with_dups.csv')

"""
Observaciones acerca de la base:
    1) El sitio tardar en cargar cada query
    2) Hay anios donde el website no entrega los datos completos y eso imposibiliota el scraping -- Se intento la busqueda por otros
    medios: csv, query bajo criterio regional o genero
    3) Hay observaciones repetidas (misma victima, mismo crimen) -- Se limpio el dataframe de filas con misma victima: paso
    de 43274 a 36131 obs.
    4) Hay una entrada de fecha erronea en la base: agosto 2018
"""
regex_pat = re.compile(r'\w:\d+:\d+', flags=re.IGNORECASE)
df = df_all.drop_duplicates(subset= df_all.columns, keep='first', inplace = False) # no duplicate rows
df['Type'] = df.Type.str.replace(regex_pat, '')

df_all['Dup'] = df_all.duplicated(subset= df_all.columns, keep = False)
df_dup =df_all[df_all.Dup == True]
df_dup.to_csv('data_dup.csv') # all duplicated PAIRS (the first was kept in the dataframe, the second dropped)

df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date') # order by date
df['year'] = pd.DatetimeIndex(df['Date']).year # year
df['month'] = df['Date'].apply(lambda x: x.strftime('%B')) # month
df['mnth_yr'] = df['Date'].apply(lambda x: x.strftime('%B-%Y')) # month-year
df.to_csv('data_nn.csv')

############### 1. DATA EXPLORATION ################################
# By Period
df_by_y = df['year'].value_counts().sort_index() # total count by year
df_by_y.plot(kind = 'bar')
plt.title("No. Cases by Year (1990-2018)")

# By Month
colors = plt.cm.GnBu(np.linspace(0, 1, 12))
df_gmth = pd.DataFrame({'Count' : df.groupby(['year', 'month']).size()}).reset_index()
df_gmth = df_gmth[df_gmth.Count >=0]
df_gmth_piv = df_gmth.pivot(index='year', columns='month', values='Count')
df_gmth_piv.plot(kind='bar', stacked=True, color = colors)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.title("No. Cases per Year by Month (1990-2018)")

## By Crime Type
# Total
df_by_type = df['Type'].value_counts() 
top10_type = df_by_type[:10]
top10_type.plot(kind = 'bar')
plt.title("No. Cases by Crime Type (1990-2018)")

# Per Year
colors = plt.cm.GnBu(np.linspace(0, 1, 65))
df_gtp = pd.DataFrame({'Count' : df.groupby(['year', 'Type']).size()}).reset_index()
df_gtp = df_gtp[df_gtp.Count >=20]
df_gtp_piv = df_gtp.pivot(index='year', columns='Type', values='Count')
df_gtp_piv.plot(kind='bar', stacked=True, color = colors)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.title("No. Cases per Year by Crime Type (1990-2018)")

## By Location

# Total
df_by_loc = df['Location'].value_counts() 
df_by_loc.sort_values(ascending=False)
top10_loc = df_by_loc[:20]
top10_loc.plot(kind = 'bar')
plt.title("No. Cases by Location (1990-2018)")

# Per Year
colors = plt.cm.GnBu(np.linspace(0, 1, 90))
df_locy = pd.DataFrame({'Count' : df.groupby(['year', 'Location']).size()}).reset_index()
df_locy = df_locy[df_locy.Count >=20] # this slightly changes the distribution over time (lower bound by loc)
df_locy_piv = df_locy.pivot(index='year', columns='Location', values='Count')
df_locy_piv.plot(kind='bar', stacked=True, color=colors)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.title("No. Cases per Year by Location (1990-2018)")

## By Responsible Group
# Total
df_by_resp = df['Alleged_Responsible'].value_counts() 
df_by_resp.sort_values(ascending=False)
top10_resp = df_by_resp[:10]
top10_resp.plot(kind = 'bar')
plt.title("No. Cases by Responsible Group (1990-2018)")

# Per Year
colors = plt.cm.GnBu(np.linspace(0, 1, 22))
df_gy = pd.DataFrame({'Count' : df.groupby(['year', 'Alleged_Responsible']).size()}).reset_index()
df_gy = df_gy[df_gy.Count >=25]
df_gy_piv = df_gy.pivot(index='year', columns='Alleged_Responsible', values='Count')
df_gy_piv.plot(kind='bar', stacked=True, color=colors)
plt.legend(bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.)
plt.title("No. Cases per Year by Responsible Group(1990-2018)")



               

d_pob ={}
for i, pob in enumerate(pob_nm):
    if pob not in d_pob:
        if len(str(pob_cd[i])) == 7:
            d_pob[pob] = '0' + str(pob_cd[i])
        else:
            d_pob[pob] = str(pob_cd[i])
            
