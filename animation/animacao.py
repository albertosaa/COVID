#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 10:23:44 2020

@author: asaa
"""

import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
import io
import zipfile
from datetime import datetime , timedelta
import imageio

#requisita o arquivo csv
r = requests.get('https://raw.githubusercontent.com/albertosaa/COVID/master/data/20200804.csv.zip')

#transforma em lista
zip_file = zipfile.ZipFile(io.BytesIO(r.content))
files = zip_file.namelist()
with zip_file.open(files[0], 'r') as csvfile_byte:
    with io.TextIOWrapper(csvfile_byte, encoding = "utf8") as csv_file:
        cr = csv.reader(csv_file)
        linecsv = list(cr)

####################
    
reglist = ["Brasil","SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]
namelist = {0: "Região",7: "data",10: "Casos Acumulados", 11: "Novos Casos",12: "Obitos Acumulados", 13: "Obitos Novos"}

####################

def smooth(Y,n):#define a suavização do grafico
    #
    #
    # Retorna a média móvel com janela (2n+1), com as bordas tratadas como descrito no texto
    #
    #    
        k = Y.size
        Y_smooth = np.zeros(k)
        Y_edge = np.concatenate( ( Y[0]*np.ones(n) , Y , Y[ k-n : k] + Y[k-1] - Y[k-n-1] )  )
        for i in range (0,k):
            Y_smooth[i]  =  np.sum(Y_edge[i:i+2*n+1])/(2*n+1)
        return Y_smooth
def mkgif(reg,col):
    filenames=[]
    C = []#casos acumulados
    dias = 0 
    for row in linecsv:#pega os casos da coluna da vez
        if reg == "Brasil":
            if (row[0] == reg) :
                if dias == 0:
                    First_Day = row[7]
                    
                C.append(int(row[col]))
                dias += 1
        else:
            if (row[1] == reg) :
                if dias == 0:
                    First_Day = row[7]
                    
                C.append(int(row[col]))
                dias += 1
                        
    R_raw = np.array(C)
    dR_raw = np.zeros(dias)
    for i in range (1,dias):#calcula a derivada numerica
        dR_raw[i] = R_raw[i] - R_raw[i-1] 
    
    #imagens
    for i in range(10,dias):#crio as imagens
        file_name = f"{reg}_{namelist[col]}_{i-10}.jpg"
        filenames.append(file_name)
        date = datetime.strptime(First_Day, "%m/%d/%Y") + timedelta(days = i)
        R_raw_k = R_raw[:i]
        if col != 11 and col != 13:
            #
            # Suavização: 4 iterações da média móvel   
            #
            R_smooth_k = smooth(R_raw_k,3)
            for j in range (0,3):#trunca a R_raw
                R_smooth_k = smooth(R_smooth_k,3)
        else:
            R_smooth_k = R_raw_k
        #dR é a derivada numerica
        dR_smooth_k = np.zeros(i)
        for j in range (1,i):
            dR_smooth_k[j] = R_smooth_k[j] - R_smooth_k[j-1]
        R_raw_p = np.concatenate((R_smooth_k[:i],np.zeros(dias-i)))
            
        ####Faz o gráfico
        plt.grid(False)    
        plt.ylim(0,np.amax(R_raw)) 
        plt.bar(np.linspace(0,dias-1,dias),abs(R_raw_p))
        plt.plot(np.linspace(0,i-1,i),R_smooth_k,"r")
        plt.xlabel("Dias")
        plt.ylabel(namelist[col])
        plt.title(namelist[col]+" -"+reg+"- "+date.strftime("%d/%m/%Y"))
        plt.savefig("fig_animacao/"+file_name,bbox_inches="tight") 
        
        plt.close()
    images = []
    for filename in filenames:# faz o gif
        images.append(imageio.imread("fig_animacao/"+filename))
    imageio.mimsave(f'gif_animacao/{reg}_{namelist[col]}.gif', images)
  
for reg in reglist:
    for col in [10,11,12,13]:
        mkgif(reg,col)
