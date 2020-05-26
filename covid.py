#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 09:43:57 2020

@author: asaa
"""


import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import codecs 
import sys



def read_csv_data(reg):
#
#    
# Lê o arquivo CSV e retorna a série temporal para os casos acumulados, número de elementos na série,
#  série de óbitos, datas do primeiro e últimos casos e população
#
#
    Y = np.zeros(1000)
    YD = np.zeros(1000)
    
    k = 0 
    
    if reg == "Brasil":
        for row in linecsv:
            if (row[0] == reg) :
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                YD[k] = int(row[11])
                k += 1
                LastDay = row[7]
        Y1 = Y[:k]  
        YD1 = YD[:k]  
        
        
    elif (reg == "São Paulo") or (reg == "Campinas"): 
        for row in linecsv:
            if (row[2] == reg) :
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                YD[k] = int(row[11])
                k += 1
                LastDay = row[7]
        Y1 = Y[:k]
        YD1 = YD[:k]  
        
        
    else:     
        for row in linecsv:
            if (row[1] == reg) and (row[2] == "") and ( row[9] != "" ):
                if k == 0:
                    FirstDay = row[7]
                    Pop = int(row[9])
                Y[k] = int(row[10])
                YD[k] = int(row[11])
                k += 1
                LastDay = row[7]
        Y1 = Y[:k]
        YD1 = YD[:k]    
        
    
    return Y1,YD1,k,FirstDay,LastDay,Pop 


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

def R0(gamma1,gamma2):
#
#
# Retorna o valor de R0, calculado nos limites extremos de gamma
#
#     
       
    M1 =  d2R_smooth + gamma1*dR_smooth 
    G1 = gamma1*dR_smooth -  (dR_smooth**2 + gamma1*dR_smooth*R_smooth)/Popul 
    
    M2 =  d2R_smooth + gamma2*dR_smooth 
    G2 = gamma2*dR_smooth -  (dR_smooth**2 + gamma2*dR_smooth*R_smooth)/Popul 

    
    return  M1/G1 ,  M2/G2

###################################################################
###################################################################
###################################################################
###################################################################
###################################################################
###################################################################

#
# Data da análise. Será o nome do arquivo CSV a ser lido
# date  
#
# Data da última análise (somente para o link no html)
# date1  
#

if len(sys.argv) == 1:   # Execução via ipyhton ou assemelhados 
    date  = "20200526"   # data da análise 
    date1 = "20200525"   # data da última análise 
    ShowGraph = True     # mostra os gráficos 

if len(sys.argv) > 1 and len(sys.argv) < 3: # erro ao rodar em command line 
    sys.exit("Ops! Too few parameters.") 
   
if len(sys.argv) >= 3: # rodando em command line. Ex: python covid 20200525 20200524 1
    ShowGraph = True     # mostra os gráficos 
    date = sys.argv[1]   # data da análise. Ex.: 20200525
    date1 = sys.argv[2]  # data da última análise. Ex.: 20200524
    
if len(sys.argv) == 3: # rodando em command line. Ex: python covid 20200525 20200524
    ShowGraph = False  # como caso anterior, mas não mostra os gráficos. Execução em batch

############################################
#
# Primeira análise: comparação dos estados.
#
# Gera os javascripts dos gráficos interativos
#
############################################


reglist = ["SP","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]


R_permil_global = []
D_permil_global = []
dR_smooth_global = []
N_max = 0
R0list = np.zeros(len(reglist))

for reg in reglist: 
    
    csvfile = open(date+".csv")
    linecsv = csv.reader(csvfile)
    R_raw,D_raw,N_k,First_Day,Last_Day,Popul = read_csv_data(reg)
    csvfile.close()

    print(reg+" "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    print(" N_k = ",N_k," First day = ",First_Day,"Pop = ",Popul)
    
    if N_k>N_max:
        N_max = N_k
    
    R_permil_global.append(1.0e6*R_raw/Popul)
    D_permil_global.append(1.0e6*D_raw/Popul)

    dR_raw = np.zeros(N_k)
    dR_smooth = np.zeros(N_k)
    d2R_smooth = np.zeros(N_k)

    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]
    
#
#
# Suavização: 4 iterações da média móvel     
#
#
    R_smooth = smooth(R_raw,3)
    for i in range (0,3):
        R_smooth = smooth(R_smooth,3)
    
    for i in range (1,N_k):
        dR_smooth[i] = R_smooth[i] - R_smooth[i-1]
        
    dR_smooth_global.append(dR_smooth)
    
    for i in range (1,N_k):
        d2R_smooth[i] = dR_smooth[i] - dR_smooth[i-1]

                               
    R0_est_0 , R0_est_1 = R0(1/10,1/20)
    beta = np.mean(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3])  ) )
    print(beta,std_err)
    
    R0list[reglist.index(reg)] = beta 



T = np.linspace(0,N_max-1,N_max)
Y = np.zeros((N_max,len(reglist)))


arg = np.argsort(R0list) 

#
#   Gráfico novos casos suavizados compartivo
#
plt.grid(True)   
plt.xlabel("Dias")
plt.ylabel("Novos casos")
plt.yscale("log")
plt.title("Novos casos (suavizados) - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])

for i in range (0,len(reglist)):
    Y1 = dR_smooth_global[i]  
    if Y1.size < N_max:
        Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
    else:
        Y[:,i] = Y1
      
for i in range (0,len(reglist)):      
    plt.plot(T,Y[:,arg[len(reglist)-1-i]],label = reglist[arg[len(reglist)-1-i]]+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",","))
            
plt.legend(bbox_to_anchor=(1.05, 1.45), loc='upper left', borderaxespad=0.)
plt.savefig("novoscasos"+date+".jpg",bbox_inches="tight") 
if ShowGraph:
    plt.show() 
else:
    plt.close()
    
    
#
#   Gráfico Menor crescimento médio nas duas últimas semanas
#
plt.grid(True)   
plt.xlabel("Dias")
plt.ylabel("Novos casos")
plt.yscale("log")
plt.title("Menor crescimento médio nas duas últimas semanas \n "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])

for i in range (0,len(reglist)):  
    plt.plot(T,Y[:,i],c="lightgray")

for i in range (0,5):
    reg = reglist[arg[4-i]]
    plt.plot(T,Y[:,arg[4-i]],label = reg+", r0 = "+'{0:.2f}'.format(R0list[arg[4-i]]).replace(".",","))
    
plt.legend(bbox_to_anchor=(1.05, 0.7), loc='upper left', borderaxespad=0.)
plt.savefig("mincasos"+date+".jpg",bbox_inches="tight") 
if ShowGraph:
    plt.show() 
else:
    plt.close()


#
#   Gráfico Maior crescimento médio nas duas últimas semanas
#
plt.grid(True)   
plt.xlabel("Dias")
plt.ylabel("Novos casos")
plt.yscale("log")
plt.title("Maior crescimento médio nas duas últimas semanas \n"+date[6:8]+"/"+date[4:6]+"/"+date[0:4])

for i in range (0,len(reglist)):  
    plt.plot(T,Y[:,i],c="lightgray")

for i in range (0,5):
    reg = reglist[arg[len(reglist)-1-i]]
    plt.plot(T,Y[:,arg[len(reglist)-1-i]],label = reg+", r0 = "+'{0:.2f}'.format(R0list[arg[len(reglist)-1-i]]).replace(".",",") )
    
plt.legend(bbox_to_anchor=(1.05, 0.7), loc='upper left', borderaxespad=0.)
plt.savefig("maxcasos"+date+".jpg",bbox_inches="tight")  
if ShowGraph:
    plt.show() 
else:
    plt.close()


#
#   Gráfico novos casos suavizados compartivo
#   javascript interativo
#
js_file = codecs.open(date+"js.html","w", encoding="iso-8859-1")
js_file.write('<!DOCTYPE HTML> \n')
js_file.write('<html> \n')
js_file.write('<head> \n')
js_file.write('<link rel="icon" type="image/x-icon"  href="http://vigo.ime.unicamp.br/COVID/favicon.ico">  \n')
js_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
js_file.write('<script> \n')
js_file.write(' \n')
js_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
js_file.write('google.charts.setOnLoadCallback(drawChart); \n')
js_file.write(' \n')
js_file.write("function drawChart() { \n");
js_file.write("      var data = new google.visualization.DataTable(); \n")
js_file.write("      data.addColumn('number', 'Dias'); \n");
for reg in reglist:
    js_file.write("      data.addColumn('number', '"+reg+", r0 = "+'{0:.2f}'.format(R0list[reglist.index(reg)]).replace(".",",")+"'); \n")
js_file.write(' \n')

js_file.write("      data.addRows([  \n")
for i in range(0,N_max):
    linedata = str(T[i])
    for j in range (0,len(reglist)):
        linedata = linedata+","+str(Y[i,j])
    js_file.write("        ["+linedata+"], \n")
js_file.write('      ]); \n')
js_file.write(' \n')
js_file.write("      var options = {\n")
js_file.write("        title: 'Novos casos (suavizados) - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (explore com o mouse, cique para realçar)',\n")
js_file.write("	width: 900,\n")
js_file.write("        height: 700,\n")
js_file.write("	       series: { \n") 
for i in range (0,len(reglist)-1):
    js_file.write(str(i)+": { lineWidth: 1 }, \n")
js_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
js_file.write("        },\n")
js_file.write("        hAxis: {title: 'Dias'},\n")
js_file.write("        vAxis: {title: 'Novos casos', scaleType: 'log'} \n")
js_file.write("        };\n")
js_file.write(' \n')
js_file.write("      var chart = new google.visualization.LineChart(document.getElementById('chart_div'));\n")
js_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
js_file.write("      chart.draw(data,  options);\n")
js_file.write("    }\n")
js_file.write("function highlightLine(chart,data,options) {\n")
js_file.write("    var selectedLineWidth = 6;\n")
js_file.write("    var selectedItem = chart.getSelection()[0];\n")
js_file.write("    //reset series line width to default value\n")
js_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
js_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
js_file.write("    chart.draw(data, options);   //redraw\n")
js_file.write("}\n")
js_file.write("</script>\n")
js_file.write("</head>\n")
js_file.write('<div id="chart_div"></div>\n')
js_file.close()



#
#  Casos por milhão
#
for i in range (0,len(reglist)):
    Y1 = R_permil_global[i]
    
    if Y1.size < N_max:
        Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
    else:
        Y[:,i] = Y1

arg = np.argsort(Y[N_max-1,:])


#
#  Gráfico Casos por milhão
#
plt.grid(True)   
plt.xlabel("Dias")
plt.ylabel("Casos por milhão")
plt.yscale("log")
plt.title("Casos por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+' (ordem decrescente)')

for i in range (0,len(reglist)):
    plt.plot(T,Y[:,arg[len(reglist)-1-i]],label = reglist[arg[len(reglist)-1-i]])
            
plt.legend(bbox_to_anchor=(1.05, 1.45), loc='upper left', borderaxespad=0.)
plt.savefig("cpm"+date+".jpg",bbox_inches="tight") 
if ShowGraph:
    plt.show() 
else:
    plt.close()
    
    
#
#  Gráfico Casos por milhão
#  javascript para o gráfico interativo
#    
js_file = codecs.open(date+"cpmjs.html","w", encoding="iso-8859-1")
js_file.write('<!DOCTYPE HTML> \n')
js_file.write('<html> \n')
js_file.write('<head> \n')
js_file.write('<link rel="icon" type="image/x-icon"  href="http://vigo.ime.unicamp.br/COVID/favicon.ico">  \n')
js_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
js_file.write('<script> \n')
js_file.write(' \n')
js_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
js_file.write('google.charts.setOnLoadCallback(drawChart); \n')
js_file.write(' \n')
js_file.write("function drawChart() { \n");
js_file.write("      var data = new google.visualization.DataTable(); \n")
js_file.write("      data.addColumn('number', 'Dias'); \n");
for reg in reglist:
    js_file.write("      data.addColumn('number', '"+reg+"'); \n")
js_file.write(' \n')

js_file.write("      data.addRows([  \n")
for i in range(0,N_max):
    linedata = str(T[i])
    for j in range (0,len(reglist)):
        linedata = linedata+","+str(Y[i,j])
    js_file.write("        ["+linedata+"], \n")
js_file.write('      ]); \n')
js_file.write(' \n')
js_file.write("      var options = {\n")
js_file.write("        title: 'Casos por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (explore com o mouse, cique para realçar)',\n")
js_file.write("	width: 900,\n")
js_file.write("        height: 700,\n")
js_file.write("	       series: { \n") 
for i in range (0,len(reglist)-1):
    js_file.write(str(i)+": { lineWidth: 1 }, \n")
js_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
js_file.write("        },\n")
js_file.write("        hAxis: {title: 'Dias'},\n")
js_file.write("        vAxis: {title: 'Casos por milhão', scaleType: 'log'} \n")
js_file.write("        };\n")
js_file.write(' \n')
js_file.write("      var chart = new google.visualization.LineChart(document.getElementById('chart_div'));\n")
js_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
js_file.write("      chart.draw(data,  options);\n")
js_file.write("    }\n")
js_file.write("function highlightLine(chart,data,options) {\n")
js_file.write("    var selectedLineWidth = 6;\n")
js_file.write("    var selectedItem = chart.getSelection()[0];\n")
js_file.write("    //reset series line width to default value\n")
js_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
js_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
js_file.write("    chart.draw(data, options);   //redraw\n")
js_file.write("}\n")
js_file.write("</script>\n")
js_file.write("</head>\n")
js_file.write('<div id="chart_div"></div>\n')
js_file.close()


#
# Mortes por milhão
#
for i in range (0,len(reglist)):
    Y1 = D_permil_global[i]
    
    if Y1.size < N_max:
        Y[:,i] = np.concatenate( (np.zeros(N_max - Y1.size) ,Y1))
    else:
        Y[:,i] = Y1
        
arg = np.argsort(Y[N_max-1,:])


#
# Gráfico Mortes por milhão
#
plt.grid(True)   
plt.xlabel("Dias")
plt.ylabel("Mortes por milhão")
plt.yscale("log")
plt.title("Mortes por milhão - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (ordem decrescente)")

for i in range (0,len(reglist)):      
    plt.plot(T[20:],Y[20:,arg[len(reglist)-1-i]],label = reglist[arg[len(reglist)-1-i]])
            
plt.legend(bbox_to_anchor=(1.05, 1.45), loc='upper left', borderaxespad=0.)
plt.savefig("mpm"+date+".jpg",bbox_inches="tight") 
if ShowGraph:
    plt.show() 
else:
    plt.close()
    
    
#
# Gráfico Mortes por milhão
#  javascript para o gráfico interativo
#
js_file = codecs.open(date+"mpmjs.html","w", encoding="iso-8859-1")
js_file.write('<!DOCTYPE HTML> \n')
js_file.write('<html> \n')
js_file.write('<head> \n')
js_file.write('<link rel="icon" type="image/x-icon"  href="http://vigo.ime.unicamp.br/COVID/favicon.ico">  \n')
js_file.write('<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> \n')
js_file.write('<script> \n')
js_file.write(' \n')
js_file.write("google.charts.load('current', {packages: ['corechart', 'line']} ); \n");
js_file.write('google.charts.setOnLoadCallback(drawChart); \n')
js_file.write(' \n')
js_file.write("function drawChart() { \n");
js_file.write("      var data = new google.visualization.DataTable(); \n")
js_file.write("      data.addColumn('number', 'Dias'); \n");
for reg in reglist:
    js_file.write("      data.addColumn('number', '"+reg+"'); \n")
js_file.write(' \n')

js_file.write("      data.addRows([  \n")
for i in range(20,N_max):
    linedata = str(T[i])
    for j in range (0,len(reglist)):
        linedata = linedata+","+str(Y[i,j])
    js_file.write("        ["+linedata+"], \n")
js_file.write('      ]); \n')
js_file.write(' \n')
js_file.write("      var options = {\n")
js_file.write("        title: 'Mortes por milhão - Estados - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+" (explore com o mouse, cique para realçar)',\n")
js_file.write("	width: 900,\n")
js_file.write("        height: 700,\n")
js_file.write("	       series: { \n") 
for i in range (0,len(reglist)-1):
    js_file.write(str(i)+": { lineWidth: 1 }, \n")
js_file.write(str(len(reglist)-1)+": { lineWidth: 1 } \n")
js_file.write("        },\n")
js_file.write("        hAxis: {title: 'Dias'},\n")
js_file.write("        vAxis: {title: 'Mortes por milhão', scaleType: 'log'} \n")
js_file.write("        };\n")
js_file.write(' \n')
js_file.write("      var chart = new google.visualization.LineChart(document.getElementById('chart_div'));\n")
js_file.write("      google.visualization.events.addListener(chart, 'select', function() { highlightLine(chart,data, options); });\n")
js_file.write("      chart.draw(data,  options);\n")
js_file.write("    }\n")
js_file.write("function highlightLine(chart,data,options) {\n")
js_file.write("    var selectedLineWidth = 6;\n")
js_file.write("    var selectedItem = chart.getSelection()[0];\n")
js_file.write("    //reset series line width to default value\n")
js_file.write("    for(var i in options.series) {options.series[i].lineWidth = 1;}\n")
js_file.write("    options.series[selectedItem.column-1].lineWidth = selectedLineWidth; //set selected line width\n")
js_file.write("    chart.draw(data, options);   //redraw\n")
js_file.write("}\n")
js_file.write("</script>\n")
js_file.write("</head>\n")
js_file.write('<div id="chart_div"></div>\n')
js_file.close()

############################################
#
# fim da primeira análise
#
############################################




############################################
#
# Segunda análise: comparação dos estados, Brasil e cidades de SP e Campinas
#
# Gera o html base do dia
#
############################################


#
# Abertura do html base 
#
html_file = codecs.open(date+".html","w", encoding="iso-8859-1")
html_file.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"> \n')
html_file.write('<html><head> \n')
html_file.write('<link rel="icon" type="image/x-icon"  href="http://vigo.ime.unicamp.br/COVID/favicon.ico">  \n')
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
html_file.write(' O objetivo deste sistema é puramente educacional, com foco na análise de dados e programação em Python, e não em epidemiologia. Não obstante, todos os dados tratados aqui são reais e, portanto, os resultados talvez possam ter alguma relevância para se entender a dinâmica real da epidemia de COVID-19, a qual está muito bem analisada, por exemplo, <a href="https://covid19br.github.io/">aqui</a>.  ')
html_file.write('Os dados e códigos necessários para gerar esta página estão <a href="https://github.com/albertosaa/COVID">aqui</a>, sinta-se à vontade para utilizá-los como quiser. <br> \n')
html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write("<div style='page-break-before: always;'></div> \n")
html_file.write('<hr> \n')
html_file.write('<big><big><span style="font-weight: bold;"> Novos casos por estado (dados suavizados) </span></big></big><br> \n')
html_file.write('<div style="text-align: center;"> Clique aqui <a href="http://vigo.ime.unicamp.br/COVID/'+date+'js.html">aqui</a> uma versão interativa deste gráfico <br><br><br></div> \n')
html_file.write('<div style="text-align: center;"><img style="width: 864px; height: 700px;" alt="Novos casos" src="novoscasos'+date+".jpg"+'">&nbsp; <br></div>')
html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="maxcasos'+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="mincasos'+date+".jpg"+'"><br></div>')
html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write("<div style='page-break-before: always;'></div> \n")
html_file.write('<hr> \n')
html_file.write('<big><big><span style="font-weight: bold;"> Casos e mortes por milhão por estados </span></big></big><br> \n')
html_file.write('<div style="text-align: center;"> Clique aqui <a href="http://vigo.ime.unicamp.br/COVID/'+date+'cpmjs.html">aqui</a> uma versão interativa deste gráfico <br><br><br></div> \n')
html_file.write('<div style="text-align: center;"><img style="width: 864px; height: 700px;" alt="Novos casos" src="cpm'+date+".jpg"+'">&nbsp; <br></div>')
html_file.write("<div style='page-break-before: always;'></div> \n")
html_file.write('<hr> \n')
html_file.write('<div style="text-align: center;"> Clique aqui <a href="http://vigo.ime.unicamp.br/COVID/'+date+'mpmjs.html">aqui</a> uma versão interativa deste gráfico <br><br><br></div> \n')
html_file.write('<div style="text-align: center;"><img style="width: 864px; height: 700px;" alt="Novos casos" src="mpm'+date+".jpg"+'">&nbsp; <br></div>')
html_file.write('<br> \n')
html_file.write('<br> \n')
html_file.write("<div style='page-break-before: always;'></div> \n")



reglist = ["Brasil","SP","São Paulo","Campinas","MG","RJ","BA","PR","RS","PE","CE","PA","SC","MA","GO","AM","ES","PB","RN","MT","AL","PI","DF","MS","SE","RO","TO","AC","AP","RR"]

for reg in reglist: 
    csvfile = open(date+".csv")
    linecsv = csv.reader(csvfile)
    R_raw,D_raw,N_k,First_Day,Last_day,Popul = read_csv_data(reg)
    csvfile.close()

    print(reg+" "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    print(" N_k = ",N_k," First day = ",First_Day," Last day = ",Last_Day,"Pop = ",Popul)
    
    T = np.linspace(0,N_k-1,N_k)
    dR_raw = np.zeros(N_k)
    dR_smooth = np.zeros(N_k)
    d2R_smooth = np.zeros(N_k)
    R_prev = np.zeros(5)
    T_prev = np.zeros(5)
    
    
    for i in range (1,N_k):
        dR_raw[i] = R_raw[i] - R_raw[i-1]
    
    
    
#
# Suavização: 4 iterações da média móvel   
#
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
            
#
# Gráfico Casos acumulados
#
    plt.grid(False)    
    plt.bar(T,R_raw)
    plt.plot(T,R_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Casos acumulados - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"CA"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close()
 
#
# Gráfico Novos Casos  
#
    plt.grid(False)    
    plt.bar(T,dR_raw)
    plt.plot(T , dR_smooth,"r")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Novos casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"NC"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close()
    
#
# Gráfico Casos por milhao
#    
    plt.grid(True)    
    plt.xlabel("Dias")
    plt.ylabel("Casos por milhão")
    plt.yscale("log")
    plt.plot(T,1.0e6*R_raw/Popul,linewidth=4)
    plt.title("Casos por milhão - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"cpm"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close() 
    
#
# Gráfico Mortes por milhao
# 
    plt.grid(True)    
    plt.xlabel("Dias")
    plt.ylabel("Mortes por milhão")
    plt.yscale("log")
    plt.plot(T,1.0e6*D_raw/Popul,linewidth=4)
    plt.title("Mortes por milhão - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.savefig(reg+"mpm"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close()
    
    
    R0_est_0 , R0_est_1 = R0(1/10,1/20)
    beta = np.mean(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3] ) ) )
    std_err = np.std(np.concatenate( (R0_est_0[N_k-17:N_k-3] , R0_est_1[N_k-17:N_k-3])  ) )
    print(beta,std_err)
    
#
# Gráfico r0 efetivo
#     
    plt.grid(True)    
    plt.plot(T[3:N_k-3],np.ones(N_k-6),"c",linewidth=4)
    plt.plot(T[3:N_k-3] , R0_est_0[3:N_k-3],"r--")
    plt.plot(T[3:N_k-3] , R0_est_1[3:N_k-3], "r--")
    plt.fill_between(T[3:N_k-3] , R0_est_0[3:N_k-3], R0_est_1[3:N_k-3] , color = "lightcoral")
    plt.ylim(0,4)
    plt.xlabel("Dias")
    plt.ylabel("r0")
    plt.title("r0 efetivo - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4]+' (três dias de atraso)')
    plt.savefig(reg+"R0"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close()

#
# Gráfico Previsão de casos 
#    
    plt.grid(False)    
    plt.bar(T,R_raw)
    plt.bar(T_prev,R_prev,color="g")
    plt.xlabel("Dias")
    plt.ylabel("Casos")
    plt.title("Previsão de casos - "+reg+" - "+date[6:8]+"/"+date[4:6]+"/"+date[0:4])
    plt.xlim(N_k-20,)
    plt.savefig(reg+"PR"+date+".jpg",bbox_inches="tight") 
    if ShowGraph:
        plt.show() 
    else:
        plt.close()

#
# encerra o html base
# 
    html_file.write("<div style='page-break-before: always;'></div> \n")
    html_file.write('<hr> \n')
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    html_file.write('<big><big><span style="font-weight: bold;">' + reg + '</span></big></big><br> \n')
    html_file.write('<br> \n')
    html_file.write('População: '+format(Popul,",d").replace(",", ".")+' <br> \n')
    html_file.write('Datas do primeiro e do último elementos na série: '+First_Day+' e '+Last_Day+'<br> \n')
    html_file.write('Número de elementos na série: '+str(N_k)+'<br> \n')
    html_file.write('Número de casos totais e mortes por milhão de habitantes: '+format(int(round(1e6*R_raw[N_k-1]/Popul)),",d").replace(",", ".")+' e '+format(int(round(1e6*D_raw[N_k-1]/Popul)),",d").replace(",", ".") + '<br> \n')
    html_file.write('r0 efetivo (últimas 2 semanas - três dias de atraso): '+'{0:.2f}'.format(beta).replace(".",",")+' (std = '+'{0:.2f}'.format(std_err).replace(".",",")+'). <br> \n')                      

    R01 = min(R0_est_0[N_k-4],R0_est_1[N_k-4])
    R02 = max(R0_est_0[N_k-4],R0_est_1[N_k-4])
    html_file.write('Último intervalo para r0 (três dias de atraso): ('+'{0:.2f}'.format(R01).replace(".",",")+' : '+'{0:.2f}'.format(R02).replace(".",",")+'). <br> \n')                      
    
    nr = 1 - 1/beta 
    nr1 = 1 - 1/(beta + std_err)
    nr2 = 1 - 1/(beta - std_err)
    html_file.write('Limiar imunidade de rebanho nR (baseado nas últimas 2 semanas - três dias de atraso) = '+'{0:.2f}'.format(nr).replace(".",",")+" ("+'{0:.2f}'.format(nr2).replace(".",",")+" : "+'{0:.2f}'.format(nr1).replace(".",",")+")  <br> \n")
    
    prevstr = ""
    for i in range (0,4):
        prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+', '    
    prevstr = prevstr+format(int(R_prev[i]),",d").replace(",", ".")+"."
    html_file.write('Previsão do número total de casos para os próximos 5 dias: '+prevstr+' <br> \n')

    html_file.write('<br> \n')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+reg+"CA"+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+reg+"NC"+date+".jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+reg+"cpm"+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+reg+"mpm"+date+".jpg"+'"><br></div>')
    html_file.write('<div style="text-align: center;"><img style="width: 432px; height: 288px;" alt="Casos Acumulados" src="'+reg+"R0"+date+".jpg"+'">&nbsp; <img style="width: 432px; height: 288px;" alt="Novos casos" src="'+reg+"PR"+date+".jpg"+'"><br></div>')
    html_file.write('<br> \n')
    html_file.write('<br> \n')
    

 
html_file.write('</body></html> \n')
html_file.close()










