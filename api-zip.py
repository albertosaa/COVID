#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:30:02 2020

@author: asaa
"""

import csv
import requests
import zipfile
import io

git_url = 'https://raw.githubusercontent.com/albertosaa/COVID/master/data/20200612.csv.zip'
r = requests.get(git_url)
zip_file = zipfile.ZipFile(io.BytesIO(r.content))
files = zip_file.namelist()
with open(files[0], 'r') as csvfile:
    cr = csv.reader(csvfile)
    linecsv = list(cr)
