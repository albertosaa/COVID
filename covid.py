#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:47:39 2020

@author: asaa
"""


 


import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate 
import scipy.stats
import codecs 



def read_csv_data(reg):
#    
# Lê arquivo CSV e retorna a série temporal para os casos acumulados, número de elementos na série,
#   data do primeiro caso e população
#
    Y = np.zeros(1000)
    
    k = 0 
    
    if reg == "Brasil":
        for row in linecsv:
            if (row[0] == reg) :
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                k += 1
        Y1 = Y[:k]        
        
    elif (reg == "São Paulo") or (reg == "Campinas"): 
        for row in linecsv:
            if (row[2] == reg) :
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                k += 1
        Y1 = Y[:k]
        
    else:     
        for row in linecsv:
            if (row[1] == reg) and (row[2] == "") and ( row[9] != "" ):
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                k += 1
        Y1 = Y[:k]
    
    
    return Y1,k,FirstDay,Pop 




def smooth(Y,n):
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

def R0(gamma1,gamma2):
#
# Retorna o valor de R0, calculado nos limites extremos de gamma
#
#     
       
    M1 =  d2R_smooth + gamma1*dR_smooth 
    G1 = dR_smooth -  (dR_smooth**2/gamma1 + dR_smooth*R_smooth)/Popul 
    
    M2 =  d2R_smooth + gamma2*dR_smooth 
    G2 = dR_smooth -  (dR_smooth**2/gamma2 + dR_smooth*R_smooth)/Popul 

    
    return (M1/G1)/gamma1, (M2/G2)/gamma2


###################################################################


#
# Data da análise. Será o nome do arquivo CSV a ser lido
date = "20200514"
#



#
# Data da última análise (somente para o link no html)
date1 = "20200514"
#

html_file = codecs.open(date+".html","w", encoding="iso-8859-1")

html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
html_file.write('<html><head> \n')
html_file.write('<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Painel Coronavirus</title><meta http-equiv="content-type" content="text/html; charset=utf-8"></head><body> \n')

html_file.write('<div style="text-align: center;"><big><big><big><span style="font-weight: bold;">Painel Coronavírus</span></big></big></big><br> \n')
html_file.write(date[6:8]+"/"+date[4:6]+"/"+date[0:4] + "<br></div> \n")

html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write('<div style="text-align: center;">  <big> <big> Alberto Saa </big> </big> <br></div> \n')
html_file.write('<div style="text-align: center;"> <big> <big> UNICAMP </big> </big></div> \n')
html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write('<br>Esta página apresenta uma análise automática dos dados do Painel Coronavirus do Ministério da Saúde, publicados diariamente <a href="https://covid.saude.gov.br/">aqui</a>. Todos os detalhes técnicos sobre a análise estão <a href="http://vigo.ime.unicamp.br/COVID/covid.pdf">aqui</a>. A análise do dia anterior está <a href="http://vigo.ime.unicamp.br/COVID/'+date1+'.html">aqui</a>.') 
html_file.write(' Se prefir, há <a href="http://vigo.ime.unicamp.br/COVID/'+date+'.pdf">aqui</a> uma versão PDF desta análise. <br>')
html_file.write(' O objetivo deste sistema é puramente educacional, com foco na análise de dados e programação em Python, e não em epidemiologia. Não obstante, todos os dados tratados aqui são reais e, portanto, os resultados talvez possam ter alguma relevância para se entender a dinâmica real da epidemia de COVID-19.  ')
html_file.write('Os dados e códigos necessários para gerar esta página estão <a href="https://github.com/albertosaa/COVID">aqui</a>, sinta-se à vontade para utlizá-los como quiser. <br> \n')

html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write('<hr> \n')
html_file.write('<br> \n')
html_file.write('<br> \n')

reglist = ["Brasil","SP","São Paulo","Campinas","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]

#reglist = ["ES"]



for reg in reglist: 
    
    csvfile = open(date+".csv",newline='')
    linecsv = csv.reader(csvfile)
    R_raw,N_k,First_Day,Popul = read_csv_data(reg)
    csvfile.close()

    print(reg+" "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    print(" N_k = ",N_k," First day = ",First_Day,"Pop = ",Popul)
    
    T = np.linspace(0,N_k-1,N_k)
    dR_raw = np.zeros(N_k)
    dR_smooth = np.zeros(N_k)
    d2R_smooth = np.zeros(N_k)
    R_prev = np.zeros(5)
    T_prev = np.zeros(5)
    
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]
    
    
    #
    #
    # Suavização: 4 iterações da média móvel     
    R_smooth = smooth(R_raw,3)
    for i in range (0,3):
        R_smooth = smooth(R_smooth,3)
    
    for i in range (1,N_k):
        dR_smooth[i] = R_smooth[i] - R_smooth[i-1]

    for i in range (1,N_k):
        d2R_smooth[i] = dR_smooth[i] - dR_smooth[i-1]

                
    a,b,r_value, p_value, std_err =  scipy.stats.linregress(np.linspace(-9,0,10),R_raw[N_k-10:N_k])
        
    for j in range (0,5):
        T_prev[j] = N_k+j
        R_prev[j] = a*(j+1) + R_raw[N_k-1]
            

    plt.grid(False)    
    plt.bar(T,R_raw)
    plt.plot(T,R_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Casos acumulados - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"CA"+date+".jpg")
    plt.show()
 

    plt.grid(False)    
    plt.bar(T,dR_raw)
    plt.plot(T , dR_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Novos casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"NC"+date+".jpg")
    plt.show() 
    
    
    R0_est_0 , R0_est_1 = R0(1/10,1/20)
    beta = np.mean(np.concatenate( (R0_est_0[N_k-14:] , R0_est_1[N_k-14:] ) ) )
    std_err = np.std(np.concatenate( (R0_est_0[N_k-14:] , R0_est_1[N_k-14:])  ) )
    print(beta,std_err)
    
    plt.grid(True)    
    plt.plot(T[3:N_k-3],np.ones(N_k-6),"c",linewidth=4)
    plt.plot(T[3:N_k-3] , R0_est_0[3:N_k-3],"r--")
    plt.plot(T[3:N_k-3] , R0_est_1[3:N_k-3], "r--")
    plt.fill_between(T[3:N_k-3] , R0_est_0[3:N_k-3], R0_est_1[3:N_k-3] , color = "lightcoral")
    plt.ylim(0,4)
    plt.xlabel("Dias")
    plt.ylabel("r0")
    plt.title("r0 efetivo - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+' (três dias de atraso)')
    plt.savefig(reg+"R0"+date+".jpg") 
    plt.show()  


   
    
    
      
    
    plt.grid(False)    
    plt.bar(T,R_raw)
    plt.bar(T_prev,R_prev,color="g")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Previsão de casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.xlim(N_k-20,)
    plt.savefig(reg+"PR"+date+".jpg")
    plt.show()


    html_file.write("<div style='page-break-before: always;'></div> \n")


    html_file.write('<big><big><span style="font-weight: bold;">' + reg + '</span></big></big><br> \n')
    html_file.write('<br> \n')
    html_file.write('População: '+format(Popul,",d").replace(",", ".")+' <br> \n')
    html_file.write('Data do primeiro elemento na série: '+First_Day+'<br> \n')
    html_file.write('Número de elementos na série: '+str(N_k)+'<br> \n')
    html_file.write('r0 efetivo (últimas 2 semanas): '+'{0:.4f}'.format(beta)+' (std = '+'{0:.4f}'.format(std_err)+ ').<br> \n')
    
    nr = 1 - 1/beta 
    nr1 = 1 - 1/(beta + std_err)
    nr2 = 1 - 1/(beta - std_err)
    
    
    html_file.write('Limiar imunidade de rebanho nR = '+'{0:.2f}'.format(nr)+" ("+'{0:.2f}'.format(nr2)+" : "+'{0:.2f}'.format(nr1)+")  <br> \n")
    
    prevstr = ""
    for i in range (0,4):
        prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+', '    
    prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+"."
    
    html_file.write('Previsão do número total de casos para os próximos 5 dias: '+prevstr+' <br> \n')
    html_file.write('<br> \n')

    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+reg+"CA"+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+reg+"NC"+date+".jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+reg+"R0"+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+reg+"PR"+date+".jpg"+'"><br></div>')
 

    html_file.write('<br> \n')
    html_file.write('<br> \n')
    



 
    
html_file.write('</body></html> \n')



html_file.close()










