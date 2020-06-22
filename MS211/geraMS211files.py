#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 09:34:58 2020

@author: asaa
"""
 

import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
import io
import zipfile
import codecs
import sys

from datetime import datetime , timedelta



r = requests.get('https://raw.githubusercontent.com/albertosaa/COVID/master/data/20200621.csv.zip')

zip_file = zipfile.ZipFile(io.BytesIO(r.content))

files = zip_file.namelist()
with zip_file.open(files[0], 'r') as csvfile_byte:
    with io.TextIOWrapper(csvfile_byte) as csv_file:
        cr = csv.reader(csv_file)
        linecsv = list(cr)


Y = []
YD = []
k = 0 
    
html_file = codecs.open("BR.csv","w", encoding="utf-8")

for row in linecsv:
    if (row[0] == "Brasil") :
        html_file.write(datetime.strptime(row[7], "%m/%d/%Y").strftime("%d/%m/%Y")+','+row[10]+','+row[12]+' \n')
        
                    
html_file.close()




reglist = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]


for reg in reglist:
    
    html_file = codecs.open(reg+".csv","w", encoding="utf-8")
    
    for row in linecsv:
        if (row[1] == reg) and (row[2] == "") and ( row[9] != "" ):
            html_file.write(datetime.strptime(row[7], "%m/%d/%Y").strftime("%d/%m/%Y")+','+row[10]+','+row[12]+' \n')

    
    
    html_file.close()
    
    
    
    
    
    
    


