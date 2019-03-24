import sys
import time
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import re
import csv
import bs4
import pickle
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urlparse
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "https://base.nocheyniebla.org/consulta_web.php"

GENERO = ['F', 'M', 'S']

SECTORES = [ 'CAMPESINO','INDIGENA','OBRERO','COMERCIANTE','EMPLEADO','TRABAJADOR INDEPENDIENTE',
 'PROFESIONAL','EMPRESARIO','INDUSTRIAL','HACENDADO','MARGINADO','TRABAJADOR (A) SEXUAL','DESEMPLEADO (A)',
 'OTRO', 'SIN INFORMACIÓN','TRANSPORTADOR','DESMOVILIZADO(A)','COLONOS','IGLESIAS','LGTB','VÍCTIMA','VENDEDOR AMBULANTE',
 'ETNIAS - NEGRITUDES','AMBIENTALISTA','GANADERO','MINERO']

MUNICIPIOS = ["AMAZONAS", "ANTIOQUIA", "ARAUCA",
"ARCHIPIÉLAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA", "ATLÁNTICO", "BOGOTÁ; D.C.", "BOLÍVAR",
"BOYACÁ;", "CALDAS","CAQUETÁ","CASANARE","CAUCA","CESAR","CHOCÓ","CÓRDOBA","CUNDINAMARCA","EXTERIOR","EXTERIOR","GUAINÍA", "GUAVIARE", 
"HUILA","LA GUAJIRA","MAGDALENA","META", "NARINO","NORTE DE SANTANDER","PUTUMAYO","QUINDIO","RISARALDA","SANTANDER","SUCRE",
"TOLIMA","VALLE DEL CAUCA","VAUPÉS","VICHADA"]

    
def nn_crawler(url, options):
    driver = webdriver.Firefox(executable_path='/Users/elenabg/geckodriver')
    driver.get(url)
    for op in options:
        op_elems= driver.find_elements_by_tag_name('option')
        for elem in op_elems:
            if op in MUNICIPIOS:
                if elem.text == op:
                    elem.click()
            else:
                if elem.get_attribute("value") == op:
                    elem.click()
    label_elems= driver.find_elements_by_tag_name('label')
    for elem in label_elems:
        if elem.text == "Tabla":
            elem.click()
    submit_elem = driver.find_elements_by_tag_name('input')[-1]
    submit_elem.click()
    WebDriverWait(driver, 2000).until(
       EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Consulta Web"))) # wait MAX 2000 seconds until query is complete

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find("table", border=1)
    driver.quit() #close browser
    
    return table
    
def parser(table, lst):
    
    for row in table.findAll('tr')[1:]:
        cols = row.findAll('td')
        
        descrip = cols[0].text
        fecha = cols[1].text
        ubic = cols[2].text
        vict = cols[3].text
        resp = cols[4].text
        tip = cols[5].text
    
        caso = (descrip, fecha, ubic, vict, resp, tip)
        lst.append(caso)

def options(init_year, fin_year, gen, reg, sect):
  
    ops_all = []
    years= []
    init = init_year
    if fin_year:
        for i in range(fin_year - init_year + 1):
            years.append(str(init))
            init += 1
    else:
        years = [init_year]

    for year in years:
        if gen and reg:
            for g in GENERO:
                for mun in MUNICIPIOS:                   
                    ops_all.append([year, g, mun])
        elif reg:
            for mun in MUNICIPIOS:
                ops_all.append([year, mun])
        elif gen:
            for g in GENERO:
                ops_all.append([year, g])
        else:
            ops_all.append([year])
                
    return ops_all

    
def join_cases(url, init_year, fin_year = None, filename,  gen = False, reg = False, sect = False):
    
    main_lst = []
    option_lst = options(init_year, fin_year, gen,  reg , sect)
    for opts in option_lst:
        try:
            table = nn_crawler(url, opts)
            parser(table, main_lst)
        except:
            pass
       
    with open(filename + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(main_lst)
        
    pickle.dump(main_lst,open(filename + '.p', 'wb'))
    
    df = pd.DataFrame(main_lst, columns=['Descripcion', 'Fecha', 'Ubic', 'Victima', 'Presunto Responsable', 'Tipo'])
    df = df.sort_values(by='Fecha')
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['year'] = pd.DatetimeIndex(df['Fecha']).year
    df['mnth_yr'] = df['Fecha'].apply(lambda x: x.strftime('%B-%Y'))  
    
    pickle.dump(df,open('df' + filename + '.p', "wb"))
    
    return main_lst
 
########################## DATA CLEANING ################################################################
    
# CSV Cleaner (in case data for some period has to be downloaded by hand as a csv and merged with the rest).
#              In this case: 2003, 2006, and 2013

def clean_csv(filename):
    'Takes a Noche y Niebla-generated csv and returns it as a list of tuples with clean dates and texts'
    
    with open(filename) as f:
        data =[tuple(line) for line in csv.reader(f)]
        
    data_clean = []
    for case in data:
        data_clean.append((case[0].replace('"', ''), case[1].replace('"', ''), case[2].replace('"', '').lstrip(), case[3].replace('"', ''), 
                           case[4].replace('"', '').lstrip(), case[5].replace('"', '')))
    return data_clean

data_clean03 = clean_csv('/Users/elenabg/2003.csv')
data_clean06 = clean_csv('/Users/elenabg/2006.csv')
data_clean13 = clean_csv('/Users/elenabg/2013.csv')

# Good 98,99,01 scrapes
lst_98, lst_99, lst_01 = pickle.load(open("lst_98.p", "rb")), pickle.load(open("lst_99.p", "rb")), pickle.load(open("lst_01.p", "rb"))

# Original full scrape (with bad 1998, 1999, 2001, 2003, 200 and 2013 data)
text_data = pickle.load(open("data99_18.p", "rb"))

# Remove bad years from original full scrape
data_no_bad = []   
for case in text_data:
    if '1998' not in case[1] and '1999' not in case[1] and '2001' not in case[1] and '2003' not in case[1] and '2006' not in case[1] and '2013' not in case[1]:
        data_no_bad.append(case)
        
pickle.dump(data_no_bad,open("data_no_bad.p", "wb"))
df_all = pickle.load(open("df_all.p", "rb")) # cargar dataframe con scraping 1990-2018

# Concatenate clean original scrape with good year lists
all_data = data_no_bad + lst_98 + lst_01 + lst_99 + data_clean03 + data_clean06 + data_clean13 
             
# Produce data frame with full data
df_all = pd.DataFrame(all_data, columns=['Description', 'Date', 'Location', 'Victim', 'Alleged_Responsible', 'Type'])

#Save df to sys
pickle.dump(df_all,open("df_all.p", "wb"))



