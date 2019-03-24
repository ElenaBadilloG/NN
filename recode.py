#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 12:10:18 2018

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

df_all = pickle.load(open("df_all.p", "rb")) # load dataframe with 1990-2018 scraping
df_all.columns=['Description', 'Date', 'Location', 'Victim', 'Alleged_Responsible', 'Type']

regex_pat = re.compile(r'\w:\d+:\d+', flags=re.IGNORECASE)
df = df_all.drop_duplicates(subset= df_all.columns, keep='first', inplace = False) # no duplicate rows
df['Type'] = df.Type.str.replace(regex_pat, '')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date') # order by date
df['year'] = pd.DatetimeIndex(df['Date']).year # year
df['month'] = df['Date'].apply(lambda x: x.strftime('%B')) # month
df['mnth_yr'] = df['Date'].apply(lambda x: x.strftime('%B-%Y')) # month-year

###############  MUNICIPAL RECODING ################################

mun_codes = pd.read_csv('mun_codes.csv')
mun_codes.columns=['Dep_code', 'Mun_code', 'Pob_code', 'Dep_name', 'Mun_name', 'Pob_name', 'Typ']
mun_codes['Dep_name'] = mun_codes['Dep_name'].str.upper()

dep_nm = list(mun_codes['Dep_name'])
dep_cd = list(mun_codes['Dep_code'])

mun_nm = list(mun_codes['Mun_name'])
mun_cd = list(mun_codes['Mun_code'])

pob_nm = list(mun_codes['Pob_name'])
pob_cd = list(mun_codes['Pob_code'])


df['Dep_name'] = df['Location'].str.split(' / ').str[0]
df['Dep_name'] = df['Dep_name'].str.replace('BOGOTÁ D.C.','BOGOTÁ, D.C.')
df['Mun_name'] = df['Location'].str.split(' / ').str[1].str.split('(', 1).str[0].str.strip()
df['Pob_name'] = df['Location'].str.split(' / ').str[2]
df['Mun_name'] = df['Mun_name'].str.replace('BOGOTÁ','BOGOTÁ, D.C.')


df['Mun_tup'] =  list(zip(df.Dep_name, df.Mun_name))
df['Pob_tup'] =  list(zip(df.Mun_name, df.Pob_name))

d ={}
for i, mun in enumerate(mun_nm):
    if len(str(dep_cd[i])) == 1:
        code = '0'  + str(mun_cd[i])
    else:
        code = str(mun_cd[i])
    if (dep_nm[i], mun) not in d:
        d[(dep_nm[i], mun)] = code
dp ={}
for i, pob in enumerate(pob_nm):
    if len(str(dep_cd[i])) == 1:
        code = '0'  + str(pob_cd[i])
    else:
        code = str(pob_cd[i])
    if (mun_nm[i], pob) not in dp:
        dp[(mun_nm[i], pob)] = code

df['Mun_code'] = df['Mun_tup'].map(d)
df['Pob_code'] = df['Pob_tup'].map(dp)

df_fin = df.drop(labels=['Mun_tup','Pob_tup'], axis=1)
pickle.dump(df_fin,open("df_fin.p", "wb")) # save dataframe
df_fin.to_csv('data_codes.csv') #save as csv

