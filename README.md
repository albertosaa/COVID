# COVID

Análise automática do Painel Coronavírus publicado diariamente pelo Ministério da Saúde (MS) aqui: 
https://covid.saude.gov.br/

O resultado das análises são publicados aqui:
http://vigo.ime.unicamp.br/COVID/

Para os detalhes técnicos da análise, leia o arquivo covid.pdf

O código python para as análises está nos diversos arquivos .py

Os arquivos CSV necessários estão todos aqui. O MS publica os dados numa planilha excel. O arquivo CSV pode ser gerado, por exemplo, usando-se o LibreOffice. 

Importante: a partir de 21/05, o formato da planilha foi alterado, e leitura dos dados por cidade foi prejudicada. Para poder continuar fazendo as análises para as cidades de São Paulo e Campinas, a planilha do MS deve ser editada e compatibilizada com as publicadas antes de 21/05.

A partir de 25/5, as cidades voltaram ao formato anterior. Porém, uma nova coluna redundante (novos casos) foi introduzida. Ela deve ser eliminada para que (a versão antiga do) covid.py funcione. 

A partir de 12/6, o arquivo csv passou a exceder os 25MB permitidos no github, por isso está zipado. As instruçes para manipulação de arquivos .zip com a interface API estão no arquivo api-zip.py

A partir de 13/6, o sistema utiliza os dados da plataforma brasil.io (https://brasil.io/dataset/covid19/caso_full/), que tem se mostrado muito superior tecnicamente e também mais estável que a plataforma do MS (bye bye MS).


