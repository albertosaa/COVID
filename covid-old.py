#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 18:56:14 2020

@author: asaa
"""


import codecs 
import numpy as np
import scipy.stats
import hashlib
import os
import painelCOVID as painel




date  = "20200617"   # data dos dados da análise 
date1 = "20200616"   # data dos dados da última análise 

gamma1 = 0.119
gamma2 = 0.182
alpha =  15



reglist = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]
reglistcid = [["SP","São Paulo"],["SP","Campinas"],["SP","Guarulhos"],["SP","São Bernardo do Campo"],\
              ["SP","São José dos Campos"],["SP","Santo André"],["SP","Ribeirão Preto"],\
              ["SP","Osasco"],["SP","Sorocaba"], ["SP","Mauá"], ["SP","Santos"], ["SP","Diadema"],\
              ["SP","São Caetano do Sul"],["SP","Jundiaí"],["SP","Piracicaba"],\
              ["RJ","Rio de Janeiro"],["BA","Salvador"],["CE","Fortaleza"],["MG","Belo Horizonte"],\
              ["AM","Manaus"],["PR","Curitiba"], ["PE","Recife"], ["RS","Porto Alegre"], ["PA","Belém"],["GO","Goiânia"],\
              ["MA","São Luís"],["AL","Maceió"], ["PI","Teresina"],  ["RN","Natal"],\
              ["MS","Campo Grande"], ["PB","João Pessoa"],["PB","Campina Grande"],\
              ["SE","Aracaju"],["MT","Cuiabá"],["RO","Porto Velho"],["SC","Florianópolis"],\
              ["AP","Macapá"],["AC","Rio Branco"],["ES","Vitória"], ["RR","Boa Vista"],["TO","Palmas"]]
#
#
#   Leitura API brasil.io
# #
#linecsv , update_string , dict_estados  = painel.read_brasil_io(reglist, reglistcid)

#
#
#   Leitura API github (dados MS)
#
 
linecsv , update_string , dict_estados  = painel.read_github(date,reglist)
 

#
# Abertura do html base 
#
html_file = codecs.open(date+".html","w", encoding="iso-8859-1")




painel.write_opening(html_file,date,date1,update_string)


    
reg = ["Brasil",""]

res = painel.read_csv_data(reg,linecsv)

R_raw = res['R_raw'] 
D_raw = res['D_raw'] 
N_k = res['N_k']
First_Day = res['First_Day']
Last_Day = res['Last_Day']
Popul = res['Popul'] 



N_s = int(N_k/7)
N_d = N_k-7*N_s

dR_raw = np.zeros(N_k)
for i in range (1,N_k):
    dR_raw[i] = R_raw[i] - R_raw[i-1]   
    

#
# Suavização: 4 iterações da média móvel   
#
R_smooth = painel.smooth(R_raw,3)
for i in range (0,3):
    R_smooth = painel.smooth(R_smooth,3)
        
    
dR_smooth = np.zeros(N_k)
for i in range (1,N_k):
    dR_smooth[i] = R_smooth[i] - R_smooth[i-1]
    
d2R_smooth = np.zeros(N_k)
for i in range (1,N_k):
    d2R_smooth[i] = dR_smooth[i] - dR_smooth[i-1]
    
    
R_prev = np.zeros(5)
T_prev = np.zeros(5)
a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
for j in range (0,5):
    T_prev[j] = N_k+j
    R_prev[j] = a*(j+1) + R_raw[N_k-1]

R0_est_0 , R0_est_1 = painel.R0(R_smooth,dR_smooth,d2R_smooth,Popul,gamma1,gamma2,alpha)
r_avg = np.mean(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3] ) ) )
std_err = np.std(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3])  ) )

print(r_avg)
   
R01 = min(R0_est_0[N_k-4],R0_est_1[N_k-4])
R02 = max(R0_est_0[N_k-4],R0_est_1[N_k-4])
    
nR = 1 - 1/r_avg 



regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  

if reg[1] == "":
    regstr = reg[0]
else:
    regstr = reg[1]+' - '+reg[0]

painel.drawCA(R_raw,R_smooth,regstr,regfile,date)
painel.drawNC(dR_raw,dR_smooth,regstr,regfile,date)
painel.drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
painel.drawR0(R0_est_0,R0_est_1,regstr,regfile,date)
painel.drawMU(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
painel.drawPR(R_raw,T_prev,R_prev,regstr,regfile,date)
painel.drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date)
    
write_dict = { \
     'html_file'  : html_file  , \
            'reg' :  regstr ,\
        'regfile' :  regfile ,\
            'date': date , \
            'res' :  res , \
            'N_s' : N_s ,\
            'N_d' : N_d ,\
          'r_avg' :  r_avg,\
        'std_err' : std_err ,\
           'R01'  : R01 , \
            'R02' : R02 ,\
            'nR'  :  nR , \
        'R_prev'  :  R_prev  }                  
    
update_date = ""
    
painel.write_analise(write_dict,update_date)

html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")

write_dict['html_file'] = html_file_local

painel.write_analise(write_dict,update_date)

html_file_local.close()

wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"
    
os.system(wkhtmltopdf)
    




reglist1 = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]
reglist = [["SP",""],["MG",""],["RJ",""],["BA",""],["PR",""],["RS",""],["PE",""],["CE",""],["PA",""],["SC",""],["MA",""],["GO",""],["AM",""],["ES",""],\
    ["PB",""],["RN",""],["MT",""],["AL",""],["PI",""],["DF",""],["MS",""],["SE",""],["RO",""],["TO",""],["AC",""],["AP",""],["RR",""]]



R_permil_global = []
D_permil_global = []
N_max = 0
R0list = np.zeros(len(reglist))


for reg in reglist:
    print(reg)
    res = painel.read_csv_data(reg,linecsv)

    R_raw = res['R_raw'] 
    D_raw = res['D_raw'] 
    N_k = res['N_k']
    First_Day = res['First_Day']
    Last_Day = res['Last_Day']
    Popul = res['Popul'] 

    N_s = int(N_k/7)
    N_d = N_k-7*N_s
    
    if N_k>N_max:
        N_max = N_k
    
    R_permil_global.append(1.0e6*R_raw/Popul)
    D_permil_global.append(1.0e6*D_raw/Popul)

    dR_raw = np.zeros(N_k)
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]   
    

#
# Suavização: 4 iterações da média móvel   
#
    R_smooth = painel.smooth(R_raw,3)
    for i in range (0,3):
        R_smooth = painel.smooth(R_smooth,3)
        
    
    dR_smooth = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth[i] = R_smooth[i] - R_smooth[i-1]
    
    d2R_smooth = np.zeros(N_k)
    for i in range (1,N_k):
        d2R_smooth[i] = dR_smooth[i] - dR_smooth[i-1]
    
    
    R_prev = np.zeros(5)
    T_prev = np.zeros(5)
    a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
    for j in range (0,5):
        T_prev[j] = N_k+j
        R_prev[j] = a*(j+1) + R_raw[N_k-1]

    R0_est_0 , R0_est_1 = painel.R0(R_smooth,dR_smooth,d2R_smooth,Popul,gamma1,gamma2,alpha)
    r_avg = np.mean(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3])  ) )
    
    
    R0list[reglist.index(reg)] = r_avg
   
    R01 = min(R0_est_0[N_k-4],R0_est_1[N_k-4])
    R02 = max(R0_est_0[N_k-4],R0_est_1[N_k-4])
    
    nR = 1 - 1/r_avg 

    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  

    if reg[1] == "":
        regstr = reg[0]
    else:
        regstr = reg[1]+' - '+reg[0]

    painel.drawCA(R_raw,R_smooth,regstr,regfile,date)
    painel.drawNC(dR_raw,dR_smooth,regstr,regfile,date)
    painel.drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
    painel.drawR0(R0_est_0,R0_est_1,regstr,regfile,date)
    painel.drawR0thumb(R0_est_0,R0_est_1,regstr,regfile,date)    
    painel.drawMU(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
    painel.drawPR(R_raw,T_prev,R_prev,regstr,regfile,date)
    painel.drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date)
    
    html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")
    
    write_dict = { \
     'html_file'  : html_file_local  , \
            'reg' :  regstr ,\
        'regfile' :  regfile ,\
            'date': date , \
            'res' :  res , \
            'N_s' : N_s ,\
            'N_d' : N_d ,\
          'r_avg' :  r_avg,\
        'std_err' : std_err ,\
           'R01'  : R01 , \
            'R02' : R02 ,\
            'nR'  :  nR , \
        'R_prev'  :  R_prev  }                  
    
    update_date = dict_estados[reg[0]]

    painel.write_analise(write_dict,update_date)

    html_file_local.close()

    wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"
    
    os.system(wkhtmltopdf)
    
painel.write_js(html_file,R_permil_global,D_permil_global,reglist1,R0list,N_max,date)    

html_file.write('<hr> \n')



html_file.write('<big><big><span style="font-weight: bold;">Estimativa de <i>r<sub>0</sub></i> para estados e algumas cidades - '+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+'. Para saber mais sobre estas estimativas e como interpretá-las, veja <a href="covid.pdf">aqui</a>. Clique nos gráficos para mais detalhes.  </span></big></big><br> \n')
html_file.write('<br> \n')
html_file.write('<big><big><span style="font-weight: bold;"> Estados  </span></big></big><br> \n')


for reg in reglist:
    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  
    fig = '<img style="width: 216px; height: 144px;" src="'+regfile+'R0thumb.jpg">'
    html_file.write('<a href="'+regfile+'.html">'+fig+"</a> ")       
 


html_file.write('<br> \n')
html_file.write('<br> \n')

html_file.write('<big><big><span style="font-weight: bold;"> Cidades  </span></big></big><br> \n')


reglist = [["SP","São Paulo"],["SP","Campinas"],["SP","Guarulhos"],["SP","São Bernardo do Campo"],\
              ["SP","São José dos Campos"],["SP","Santo André"],["SP","Ribeirão Preto"],\
              ["SP","Osasco"],["SP","Sorocaba"], ["SP","Mauá"], ["SP","Santos"], ["SP","Diadema"],\
              ["SP","São Caetano do Sul"],["SP","Jundiaí"],["SP","Piracicaba"],\
              ["RJ","Rio de Janeiro"],["BA","Salvador"],["CE","Fortaleza"],["MG","Belo Horizonte"],\
              ["AM","Manaus"],["PR","Curitiba"], ["PE","Recife"], ["RS","Porto Alegre"], ["PA","Belém"],["GO","Goiânia"],\
              ["MA","São Luís"],["AL","Maceió"], ["PI","Teresina"],  ["RN","Natal"],\
              ["MS","Campo Grande"], ["PB","João Pessoa"],["PB","Campina Grande"],\
              ["SE","Aracaju"],["MT","Cuiabá"],["RO","Porto Velho"],["SC","Florianópolis"],\
              ["AP","Macapá"],["AC","Rio Branco"],["ES","Vitória"], ["RR","Boa Vista"],["TO","Palmas"]]

    


for reg in reglist:
    print(reg)
    res = painel.read_csv_data(reg,linecsv)

    R_raw = res['R_raw'] 
    D_raw = res['D_raw'] 
    N_k = res['N_k']
    First_Day = res['First_Day']
    Last_Day = res['Last_Day']
    Popul = res['Popul'] 

    N_s = int(N_k/7)
    N_d = N_k-7*N_s
    
    dR_raw = np.zeros(N_k)
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]   
    

#
# Suavização: 4 iterações da média móvel   
#
    R_smooth = painel.smooth(R_raw,3)
    for i in range (0,3):
        R_smooth = painel.smooth(R_smooth,3)
        
    
    dR_smooth = np.zeros(N_k)
    for i in range (1,N_k):
        dR_smooth[i] = R_smooth[i] - R_smooth[i-1]
    
    d2R_smooth = np.zeros(N_k)
    for i in range (1,N_k):
        d2R_smooth[i] = dR_smooth[i] - dR_smooth[i-1]
    
    
    R_prev = np.zeros(5)
    T_prev = np.zeros(5)
    a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
    for j in range (0,5):
        T_prev[j] = N_k+j
        R_prev[j] = a*(j+1) + R_raw[N_k-1]

    R0_est_0 , R0_est_1 = painel.R0(R_smooth,dR_smooth,d2R_smooth,Popul,gamma1,gamma2,alpha)
    r_avg = np.mean(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3])  ) )
    
   
    R01 = min(R0_est_0[N_k-4],R0_est_1[N_k-4])
    R02 = max(R0_est_0[N_k-4],R0_est_1[N_k-4])
    
    nR = 1 - 1/r_avg 

    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  

    if reg[1] == "":
        regstr = reg[0]
    else:
        regstr = reg[1]+' - '+reg[0]

    painel.drawCA(R_raw,R_smooth,regstr,regfile,date)
    painel.drawNC(dR_raw,dR_smooth,regstr,regfile,date)
    painel.drawPM(R_raw,D_raw,Popul,regstr,regfile,date) 
    painel.drawR0(R0_est_0,R0_est_1,regstr,regfile,date)
    painel.drawR0thumb(R0_est_0,R0_est_1,regstr,regfile,date)    
    painel.drawMU(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha,regstr,regfile,date)
    painel.drawPR(R_raw,T_prev,R_prev,regstr,regfile,date)
    painel.drawCAS(R_raw,D_raw,N_s,N_d,regstr,regfile,date)
    
    html_file_local = codecs.open(regfile+".html","w", encoding="iso-8859-1")
    
    write_dict = { \
     'html_file'  : html_file_local  , \
            'reg' :  regstr ,\
        'regfile' :  regfile ,\
            'date': date , \
            'res' :  res , \
            'N_s' : N_s ,\
            'N_d' : N_d ,\
          'r_avg' :  r_avg,\
        'std_err' : std_err ,\
           'R01'  : R01 , \
            'R02' : R02 ,\
            'nR'  :  nR , \
        'R_prev'  :  R_prev  }                  
    

    update_date = dict_estados[reg[0]]

    painel.write_analise(write_dict,update_date)

    html_file_local.close()

    wkhtmltopdf = "wkhtmltopdf --quiet "+regfile+".html "+regfile+".pdf"
    
    os.system(wkhtmltopdf)
    



for reg in reglist:
    regfile = hashlib.md5(bytes(reg[0]+reg[1]+date,'utf-8')).hexdigest()  
    fig = '<img style="width: 216px; height: 144px;" src="'+regfile+'R0thumb.jpg">'
    html_file.write('<a href="'+regfile+'.html">'+fig+"</a> ")       

       
    
html_file.close()
