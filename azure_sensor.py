import os
import sys
import time
import urllib.request
from urllib.request import urlopen
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np
from numpy import nan
import csv

url = "http://reactorfeeds.org/feeds/stations"
request = urllib.request.Request(url, headers={"Accept" : "text/xml"})
contents = urllib.request.urlopen(request).read()
root = ET.fromstring(contents)

try:
    os.remove("streamlist.csv")
except OSError:
    pass

stream=[]
z = root.getchildren()
length = len(z)

for i in range (0,length):
    x = root.getchildren()[i]
    try:
        Station = x[0].text
        Detectorid = x[1].text
        detectorName = x[2].text
        Direction = x[6].text
    except IndexError:
        pass
    else:
        info = (Station+','+Detectorid+','+detectorName+','+Direction)
        stream.append(info)

def streamlist(df):
    columns = ['stationName','detectorId', 'detectorName','direction']
    df_stream = pd.DataFrame(stream)
    df = pd.DataFrame(df_stream[0].str.split(',').tolist(),columns = columns)
    return df
	

df = streamlist(stream)
df.to_csv('streamlist.csv', index = None)



