#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 11:38:20 2020

@author: asaa
"""

import json
from time import localtime
import requests
import xlrd
import pandas as pd
import zipfile
import os

#informações do arquivo PainelGeral do site do ministério da saude
url = "https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/"
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "x-parse-application-id": "unAFkcaNDeXajurGB7LChj8SgQYS2ptm",
}


#pego o site
request = requests.get(url + "PortalGeral", headers=headers)

#faço o dowload do xlsx
content = request.content.decode("utf8")
data = json.loads(content)["results"][0]
xlsx_file = data["arquivo"]["url"]
print("obtendo os dados do MS....")
df = pd.read_excel(xlsx_file)
print("pronto!")

#converto para csv
df.to_csv(f"COVID{localtime().tm_year}{localtime().tm_mon:02d}{localtime().tm_mday:02d}.csv", index = None, header=True)
print("arq csv salvo")

#zipo o arquivo csv
jungle_zip = zipfile.ZipFile(f'COVID{localtime().tm_year}{localtime().tm_mon:02d}{localtime().tm_mday:02d}.zip', 'w')
jungle_zip.write(f"COVID{localtime().tm_year}{localtime().tm_mon:02d}{localtime().tm_mday:02d}.csv", compress_type=zipfile.ZIP_DEFLATED)
jungle_zip.close()
os.remove(f"COVID{localtime().tm_year}{localtime().tm_mon:02d}{localtime().tm_mday:02d}.csv")
