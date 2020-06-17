#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 10:45:57 2020

@author: asaa
"""



import numpy as np
import matplotlib.pyplot as plt
import requests
import csv
from datetime import datetime
import time 
import io
import zipfile

def read_github(date,reglist):

    git_url = 'https://raw.githubusercontent.com/albertosaa/COVID/master/data/'+date+'.csv.zip'
    r = requests.get(git_url)
    zip_file = zipfile.ZipFile(io.BytesIO(r.content))
    files = zip_file.namelist()
    with zip_file.open(files[0], 'r') as csvfile_byte:
        with io.TextIOWrapper(csvfile_byte) as csv_file:
            cr = csv.reader(csv_file)
            linecsv = list(cr)
        
    update_string = ""      

    dict_estados = {}
    for reg in reglist:  
        dict_estados.update({ reg : ""})
        
        
    return linecsv , update_string , dict_estados

def read_brasil_io(lista_estados,lista_cidades):
    
    
    brasil_io_url ='https://brasil.io/dataset/covid19/caso_full/?format=csv'
    

    print('Lendo os dados do repositório brasil.io......')    
    start = time.time()    
    with requests.Session() as s:
        download = s.get(brasil_io_url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        linecsv_brasil_io = list(cr)
    end = time.time()
    print('Feito. '+'{0:.1f}'.format(end - start)+" segundos.")
    
    now = datetime.now()
    
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    update_string = 'Últimas atualizações nos arquivos <a href="https://brasil.io/dataset/covid19/caso_full/">brasil.io</a>  (dados importados em '+dt_string+"): <br> "
    
    dict_estados = {}
    
    for reg in lista_estados:
        for row in linecsv_brasil_io:
            if row[6] == "state" and row[3] == reg:   
                if row[14] == 'True':
                    update_string = update_string+reg+" = "+row[1]+", "
                    if row[14] == 'True': 
                        dict_estados.update({ reg : row[1]})
    
    update_string = update_string[:-2]
    
    update_string = update_string+". <br> Estados com dados desatualizados terão a análise prejudicada."

    linecsv = []


    N_max = 0
    for reg in lista_estados:
    
        linecsv_reg = []

        for row in linecsv_brasil_io:
            if row[6] == "state" and row[3] == reg:     
                newrow = ["",reg,"","","","","",row[1],"",row[13],row[7],"",row[10]]
                linecsv_reg.append(newrow)
        N_l = len(linecsv_reg)
        if N_l > N_max:
            N_max = N_l
        
        for i in range (0,N_l):
            linecsv.append(linecsv_reg[N_l-1-i])
        
    R_brasil = np.zeros(N_max,dtype=int)
    D_brasil = np.zeros(N_max,dtype=int)

    for reg in lista_estados:
    
        reg1 = [reg,""]

        res = read_csv_data(reg1,linecsv)

        R_raw = res['R_raw'] 
        D_raw = res['D_raw'] 
    
        if R_raw.size < N_max:
            R_brasil += np.concatenate((np.zeros(N_max - R_raw.size,dtype=int),R_raw))
            D_brasil += np.concatenate((np.zeros(N_max - R_raw.size,dtype=int),D_raw))
        else:
            R_brasil +=  R_raw
            D_brasil +=  D_raw        


    datas = []

    for row in linecsv_brasil_io:
        if row[6] == "state" and row[3] == "SP":     
            datas.append(row[1])
        
    for i in range (0,N_max):
        newrow = ["Brasil","","","","","","",datas[N_max-1-i],"","210147125",str(R_brasil[i]),"",str(D_brasil[i])]
        linecsv.append(newrow)
    
    


    for reg in lista_cidades:
    
        linecsv_reg = []

        for row in linecsv_brasil_io:
            if row[3] == reg[0] and row[4] == reg[1]:     
                newrow = ["",reg[0],reg[1],"","","","",row[1],"",row[13],row[7],"",row[10]]
                linecsv_reg.append(newrow)
        N_l = len(linecsv_reg)

        
        for i in range (0,N_l):
            linecsv.append(linecsv_reg[N_l-1-i]) 
            
    return linecsv , update_string , dict_estados

def read_csv_data(reg,linecsv):
#
#    
# Lê o arquivo CSV e retorna a série temporal para os casos acumulados, número de elementos na série,
#  série de óbitos, datas do primeiro e últimos casos e população
#
#
    Y = []
    YD = []
    k = 0 
    
    if reg[0] == "Brasil":
        for row in linecsv:
            if (row[0] == reg[0]) :
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))
                
                k += 1
                Last_Day = row[7]
 
    elif  reg[1] == "":    
        for row in linecsv:
            if (row[1] == reg[0]) and (row[2] == "") and ( row[9] != "" ):
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))

                k += 1
                Last_Day = row[7]
 
    else:
        for row in linecsv:
            if (row[1] == reg[0]) and (row[2] == reg[1]):
                if k == 0:
                    First_Day = row[7]
                    Pop = int(row[9])
                    
                Y.append(int(row[10]))
                YD.append(int(row[12]))

                k += 1
            Last_Day = row[7]
  
    dict_return = {'R_raw' : np.array(Y), \
                   'D_raw' :np.array(YD), \
                    'N_k' : k, \
                 'First_Day' : First_Day,\
                 'Last_Day'  : Last_Day, \
                   'Popul' : Pop   }
    
    return dict_return


def write_opening(html_file,date,date1,update_string):
     
    html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
    html_file.write('<html><head> \n')
    html_file.write('<link rel="icon" type="image/x-icon"  href="favicon.ico">  \n')
    html_file.write('<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Painel Coronavirus</title><meta http-equiv="content-type" content="text/html; charset=utf-8"></head><body> \n')
    html_file.write('<div style="text-align: center;"><big><big><big><span style="font-weight: bold;">Painel Coronavírus</span></big></big></big><br> \n')
    html_file.write(date[6:8]+"/"+date[4:6]+"/"+date[0:4] + "<br></div> \n")
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    html_file.write('<div style="text-align: center;">  <big> <big> Alberto Saa </big> </big> <br></div> \n')
    html_file.write('<div style="text-align: center;"> <big> <big> UNICAMP </big> </big></div> \n')
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    html_file.write('<br>Esta página apresenta uma análise automática dos casos de COVID-19 a partir de dados públicos. (Clique <a href="dadosCOVID.html">aqui</a> para saber mais sobre a importação destes dados). Todos os detalhes técnicos sobre a análise estão <a href="covid.pdf">aqui</a>. A análise do dia anterior está <a href="'+date1+'.html">aqui</a>.') 
    html_file.write('O objetivo deste sistema é puramente educacional, com foco na análise de dados e programação em Python, e não em epidemiologia. Não obstante, todos os dados tratados aqui são reais e, portanto, os resultados talvez possam ter alguma relevância para se entender a dinâmica real da epidemia de COVID-19, a qual está muito bem analisada, por exemplo, <a href="https://covid19br.github.io/">aqui</a>.  ')
    html_file.write('Os dados e códigos necessários para gerar esta página estão <a href="https://github.com/albertosaa/COVID">aqui</a>, sinta-se à vontade para utilizá-los como quiser. <br> \n')
    html_file.write('<br> \n')
    if update_string == "":
        html_file.write('Análise realizada a partir dos dados do Ministério da Saúde, clique <a href="dadosCOVID.html">aqui</a> para mais detalhes. <br> \n')
    else: 
        html_file.write(update_string + ' <br> \n' )
    html_file.write('<br> \n')
    html_file.write('<hr> \n')

    
    return 

def write_analise(write_dict,update_date):
    
    
    html_file = write_dict['html_file']
    reg = write_dict['reg']
    regfile = write_dict['regfile']
    date = write_dict['date']
    
    R_raw = write_dict['res']['R_raw']
    D_raw = write_dict['res']['D_raw'] 
    N_k = write_dict['res']['N_k']
    First_Day = write_dict['res']['First_Day']
    Last_Day = write_dict['res']['Last_Day']
    Popul = write_dict['res']['Popul'] 
  
    N_s = write_dict['N_s']
    N_d = write_dict['N_d']
    
    r_avg = write_dict['r_avg']
    std_err = write_dict['std_err']
    
    R01 = write_dict['R01']
    R02 = write_dict['R02']
    nR = write_dict['nR']
    R_prev = write_dict['R_prev']
    

    html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
    html_file.write('<html><head> \n')
    html_file.write('<link rel="icon" type="image/x-icon"  href="favicon.ico">  \n')
    html_file.write('<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Painel Coronavirus</title><meta http-equiv="content-type" content="text/html; charset=utf-8"></head><body> \n')
    html_file.write('<big><big><span style="font-weight: bold;"> '+reg+' - '+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+'. </span></big></big> <br> \n')    
    html_file.write('Detalhes técnicos, <a href="covid.pdf">aqui</a>. Clique <a href='+regfile+'.pdf>aqui</a> para uma versão em PDF desta análise. \n')

    html_file.write('<br> \n')
    html_file.write('<br> \n')

    html_file.write('População: '+format(Popul,",d").replace(",", ".")+'.   \n')

    if N_d == 0:    
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas). <br> \n')
    elif N_d == 1:
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas e '+str(N_d)+' dia). <br> \n')
    else:
        html_file.write('Início e fim da série: '+First_Day+' e '+Last_Day+'. ('+str(N_k)+' elementos - '+str(N_s)+' semanas e '+str(N_d)+' dias). <br> \n')
        
    if update_date != "":
        html_file.write('Última atualização na plataforma <a href="https://brasil.io/dataset/covid19/caso_full/">brasil.io</a>: '+update_date+'. <br> \n')
        
    html_file.write('Número de casos totais e mortes: '+format(R_raw[N_k-1],",d").replace(",", ".")+' e '+format(D_raw[N_k-1],",d").replace(",", ".")+'. ('+format(int(round(1e6*R_raw[N_k-1]/Popul)),",d").replace(",", ".")+' e '+format(int(round(1e6*D_raw[N_k-1]/Popul)),",d").replace(",", ".") + ' por milhão de habitantes, respectivamente.) <br> \n')
    html_file.write('<i>r<sub>0</sub></i> efetivo médio (duas últimas semanas - três dias de atraso): '+'{0:.2f}'.format(r_avg).replace(".",",")+' (std = '+'{0:.2f}'.format(std_err).replace(".",",")+').  \n')                      
    html_file.write('Último intervalo para  <i>r<sub>0</sub></i> (três dias de atraso): ('+'{0:.2f}'.format(R01).replace(".",",")+' : '+'{0:.2f}'.format(R02).replace(".",",")+'). <br> \n')                      
    
    html_file.write('Limiar imunidade de grupo  <i>n<sub>R</sub> </i> (baseado no valor de <i>r<sub>0</sub></i> efetivo médio) = '+'{0:.2f}'.format(nR).replace(".",",")+".  <br> \n")
    
    prevstr = ""
    for i in range (0,4):
        prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+', '    
    prevstr = prevstr+format(int(R_prev[4]),",d").replace(",", ".")+"."
    
    html_file.write('Previsão do número total de casos para os próximos 5 dias: '+prevstr+' <br> \n')

    html_file.write('<br> \n')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+regfile+"CA.jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+regfile+"NC.jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos e morter por milhao" src="'+regfile+"pm.jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Previsão novos casos" src="'+regfile+"PR.jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos por semana" src="'+regfile+"CAS.jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="mu" src="'+regfile+"mu.jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 604px; height: 403px;" alt="r0" src="'+regfile+"R0.jpg"+'"><br></div>')
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    

    
    return


def smooth(Y,n):
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

def R0(R_smooth,dR_smooth,d2R_smooth,Popul,gamma1,gamma2,alpha):
#
#
# Retorna o valor de R0, calculado nos limites extremos de gamma
#
#     
         
    
    M1 =  d2R_smooth + gamma1*dR_smooth 
    G1 = gamma1*dR_smooth -  alpha*(dR_smooth**2 + gamma1*dR_smooth*R_smooth)/Popul 
    
    M2 =  d2R_smooth + gamma2*dR_smooth 
    G2 = gamma2*dR_smooth -  alpha*(dR_smooth**2 + gamma2*dR_smooth*R_smooth)/Popul 
    
    return  M1/G1 ,  M2/G2



def drawCA(R_raw,R_smooth,reg,regfile,date):
#
# Gráfico Casos acumulados
#

    N_k = R_raw.size
    
    plt.grid(False)    
    plt.bar(np.linspace(0,N_k-1,N_k),R_raw)
    plt.plot(np.linspace(0,N_k-1,N_k),R_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Casos acumulados - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"CA.jpg",bbox_inches="tight") 

    plt.close()
        
    return

def drawNC(dR_raw,dR_smooth,reg,regfile,date):
#
# Gráfico Novos Casos  
#

    N_k = dR_raw.size  

    plt.grid(False)    
    plt.bar(np.linspace(0,N_k-1,N_k),dR_raw)
    plt.plot(np.linspace(0,N_k-1,N_k) , dR_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Novos casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"NC.jpg",bbox_inches="tight") 
    
    plt.close()
    
    return
    

def drawPM(R_raw,D_raw,Popul,reg,regfile,date):
    
    N_k = R_raw.size
    
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    
    ax1.plot(np.linspace(0,N_k-1,N_k),1.0e6*R_raw/Popul,linewidth=4,color='b')
    ax2.plot(np.linspace(0,N_k-1,N_k),1.0e6*D_raw/Popul,linewidth=4,color='r')    
    
    ax1.set_yscale("log")
    ax2.set_yscale("log")
    
    ax1.set_xlabel('Dias')
    ax1.set_ylabel('Casos por milhão', color = 'b')
    ax2.set_ylabel('Mortes por milhão', color='r' )
    plt.title("Casos e mortes por milhão - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"pm.jpg",bbox_inches="tight") 

    plt.close()
        
    return

def drawR0(R0_est_0,R0_est_1,reg,regfile,date):
#
# Gráfico r0 efetivo
#     
    N_k = R0_est_0.size
    T = np.linspace(0,N_k-1,N_k)
    
    plt.grid(True)    
    plt.fill_between(T[N_k-5:],np.zeros(5),4*np.ones(5), color = "bisque")
    plt.plot(T[3:],np.ones(N_k-3),"c",linewidth=4)
    plt.plot(T[3:] , R0_est_0[3:],"r--")
    plt.plot(T[3:] , R0_est_1[3:], "r--")
    plt.fill_between(T[3:] , R0_est_0[3:], R0_est_1[3:] , color = "lightcoral")
    plt.ylim(0,4)
    plt.xlabel("Dias")
    plt.ylabel("$r_0$")
    plt.title("$r_0$ efetivo - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(regfile+"R0.jpg",bbox_inches="tight") 
 
    plt.close()
    
    return
    
def drawR0thumb(R0_est_0,R0_est_1,reg,regfile,date):
    
    N_k = R0_est_0.size
    T = np.linspace(0,N_k-1,N_k)
        
    plt.figure(figsize=(4,2.2))
    plt.grid(True)  
    plt.fill_between(T[N_k-5:],np.zeros(5),4*np.ones(5), color = "bisque")
    plt.plot(T[3:],np.ones(N_k-3),"c",linewidth=4)
    plt.plot(T[3:] , R0_est_0[3:],"r--")
    plt.plot(T[3:] , R0_est_1[3:], "r--")  
    plt.fill_between(T[3:] , R0_est_0[3:], R0_est_1[3:] , color = "lightcoral")
    plt.ylim(0.5,2.5)
    plt.title(reg,fontsize=18)
    plt.savefig(regfile+"R0thumb.jpg",bbox_inches="tight") 

    plt.close()
                 
    
    return

def drawPR(R_raw,T_prev,R_prev,reg,regfile,date):
    
    N_k = R_raw.size
    T = np.linspace(0,N_k-1,N_k)
    
    plt.grid(False)    
    plt.bar(T,R_raw)
    plt.bar(T_prev,R_prev,color="g")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Previsão de casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.xlim(N_k-20,)
    plt.savefig(regfile+"PR.jpg",bbox_inches="tight") 

    plt.close()
        
    return 
        
   

def drawMU(R_smooth,dR_smooth,Popul,gamma1,gamma2,alpha,reg,regfile,date):
#
# Gráfico mu 
#      
    N_k = R_smooth.size
    T = np.linspace(0,N_k-1,N_k)

    mu_0 = alpha*(dR_smooth + gamma1*R_smooth)/(Popul*gamma1)
    mu_1 = alpha*(dR_smooth + gamma2*R_smooth)/(Popul*gamma2)
    
    mu_max = max(np.max(mu_0),np.max(mu_1))
    
    plt.grid(True)    
    plt.fill_between(T[N_k-5:],np.zeros(5),mu_max*np.ones(5), color = "bisque")
    plt.plot(T[3:] , mu_0[3:],"r--")
    plt.plot(T[3:] , mu_1[3:], "r--")
    plt.fill_between(T[3:] , mu_0[3:], mu_1[3:] , color = "lightcoral")
    plt.xlabel("Dias")
    plt.ylabel("μ")
    plt.title("Razão μ - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (α = "+'{0:.1f}'.format(alpha).replace(".",",")+")")
    plt.savefig(regfile+"mu.jpg",bbox_inches="tight") 
 
    plt.close()
    
    return

def drawCAS(R_raw,D_raw,N_s,N_d,reg,regfile,date):
    
    N_k = R_raw.size
    
    if N_d == 0:
        R_week = np.zeros(N_s)
        D_week = np.zeros(N_s)
        T_week = np.linspace(0,N_s-1,N_s)
    else:
        R_week = np.zeros(N_s+1)
        D_week = np.zeros(N_s+1)
        T_week = np.linspace(0,N_s,N_s+1)
        
    R_week[0] = R_raw[6]
    D_week[0] = D_raw[6]

    for i in range (1,N_s):
        R_week[i] = R_raw[7*(i+1)-1] - R_raw[7*i-1]       
        D_week[i] = D_raw[7*(i+1)-1] - D_raw[7*i-1]    
        
    R_week_rem = R_raw[N_k-1] - R_raw[7*N_s-1]   
    
    if N_d == 0:
        
        #
        # Novos casos por semana
        #
        plt.grid(False)    
        plt.bar(T_week,R_week)
        plt.xlabel("Semanas desde o primeiro caso")
        plt.ylabel("Casos")
        plt.title("Casos por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(regfile+"CAS.jpg",bbox_inches="tight") 

        plt.close()
            
    else:
        
        #
        # Novos casos por semana
        #
        plt.grid(False)    
        plt.bar(T_week,R_week)
        plt.bar(T_week,np.concatenate((np.zeros(N_s),np.array([R_week_rem]))),color = "lightblue")
        plt.xlabel("Semanas desde o primeiro caso")
        plt.ylabel("Casos")
        plt.title("Casos por semana - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
        plt.savefig(regfile+"CAS.jpg",bbox_inches="tight") 

        plt.close() 
            
    return 


def write_js(html_file,R_permil_global,D_permil_global,reglist,R0list,N_max,date):
    
    
    T = np.linspace(0,N_max-1,N_max)
    Y = np.zeros((N_max,len(reglist)))

    arg = np.argsort(R0list) 

    for i in range (0,len(reglist)):
        Y1 = R_permil_global[i]
        if Y1.size < N_max:
            Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
        else:
            Y[:,i] = Y1

    html_file.write('<br> \n')

    html_file.write('<hr> \n')

    html_file.write('<big><big><span style="font-weight: bold;"> Casos e mortes por milhão por estados. Explore com o mouse, clique para realçar. </span></big></big><br> \n')


    html_file.write('<html> \n')
    html_file.write('<head> \n')
    html_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
    html_file.write('<script> \n')
    html_file.write(' \n')
    html_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
    html_file.write('google.charts.setOnLoadCallback(drawChart); \n')
    html_file.write(' \n')
    html_file.write("function drawChart() { \n");
    html_file.write("      var data = new google.visualization.DataTable(); \n")
    html_file.write("      data.addColumn('number', 'Dias'); \n");
    for i in range (0,len(reglist)):
        html_file.write("      data.addColumn('number', '"+reglist[arg[len(reglist)-1-i]]+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",",")+"'); \n")
    html_file.write(' \n')

    html_file.write("      data.addRows([  \n")
    for i in range(0,N_max):
        linedata = str(T[i])
        for j in range (0,len(reglist)):
            linedata = linedata+","+str(Y[i,arg[len(reglist)-1-j]])
        html_file.write("        ["+linedata+"], \n")
    html_file.write('      ]); \n')
    html_file.write(' \n')
    html_file.write("      var options = {\n")
    html_file.write("        title: 'Casos por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+"',\n")
    html_file.write("	width: 900,\n")
    html_file.write("        height: 700,\n")
    html_file.write("	       series: { \n") 
    for i in range (0,len(reglist)-1):
        html_file.write(str(i)+": { lineWidth: 1 }, \n")
    html_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
    html_file.write("        },\n")
    html_file.write("        hAxis: {title: 'Dias'},\n")
    html_file.write("        vAxis: {title: 'Casos por milhão', scaleType: 'log'} \n")
    html_file.write("        };\n")
    html_file.write(' \n')
    html_file.write("      var chart = new google.visualization.LineChart(document.getElementById('casos_div'));\n")
    html_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
    html_file.write("      chart.draw(data,  options);\n")
    html_file.write("    }\n")
    html_file.write("function highlightLine(chart,data,options) {\n")
    html_file.write("    var selectedLineWidth = 6;\n")
    html_file.write("    var selectedItem = chart.getSelection()[0];\n")
    html_file.write("    //reset series line width to default value\n")
    html_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
    html_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
    html_file.write("    chart.draw(data, options);   //redraw\n")
    html_file.write("}\n")
    html_file.write("</script>\n")
    html_file.write("</head>\n")
    html_file.write('<div id="casos_div"></div>\n')



    for i in range (0,len(reglist)):
        Y1 = D_permil_global[i]
        if Y1.size < N_max:
            Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
        else:
            Y[:,i] = Y1
        
        
    html_file.write('<html> \n')
    html_file.write('<head> \n')
    html_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
    html_file.write('<script> \n')
    html_file.write(' \n')
    html_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
    html_file.write('google.charts.setOnLoadCallback(drawChart); \n')
    html_file.write(' \n')
    html_file.write("function drawChart() { \n");
    html_file.write("      var data = new google.visualization.DataTable(); \n")
    html_file.write("      data.addColumn('number', 'Dias'); \n");
    for i in range (0,len(reglist)):
        html_file.write("      data.addColumn('number', '"+reglist[arg[len(reglist)-1-i]]+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",",")+"'); \n")
    html_file.write(' \n')

    html_file.write("      data.addRows([  \n")
    for i in range(0,N_max):
        linedata = str(T[i])
        for j in range (0,len(reglist)):
            linedata = linedata+","+str(Y[i,arg[len(reglist)-1-j]])
        html_file.write("        ["+linedata+"], \n")
    html_file.write('      ]); \n')
    html_file.write(' \n')
    html_file.write("      var options = {\n")
    html_file.write("        title: 'Mortes por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+"',\n")
    html_file.write("	width: 900,\n")
    html_file.write("        height: 700,\n")
    html_file.write("	       series: { \n") 
    for i in range (0,len(reglist)-1):
        html_file.write(str(i)+": { lineWidth: 1 }, \n")
    html_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
    html_file.write("        },\n")
    html_file.write("        hAxis: {title: 'Dias'},\n")
    html_file.write("        vAxis: {title: 'Mortes por milhão', scaleType: 'log'} \n")
    html_file.write("        };\n")
    html_file.write(' \n')
    html_file.write("      var chart = new google.visualization.LineChart(document.getElementById('mortes_div'));\n")
    html_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
    html_file.write("      chart.draw(data,  options);\n")
    html_file.write("    }\n")
    html_file.write("function highlightLine(chart,data,options) {\n")
    html_file.write("    var selectedLineWidth = 6;\n")
    html_file.write("    var selectedItem = chart.getSelection()[0];\n")
    html_file.write("    //reset series line width to default value\n")
    html_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
    html_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
    html_file.write("    chart.draw(data, options);   //redraw\n")
    html_file.write("}\n")
    html_file.write("</script>\n")
    html_file.write("</head>\n")
    html_file.write('<div id="mortes_div"></div>\n')



    return
