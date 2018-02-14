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

#Get the XML data from the reactorfeeds 
url_str = 'http://205.221.97.102/Iowa.Sims.AllSites.C2C/IADOT_SIMS_AllSites_C2C.asmx/OP_ShareTrafficDetectorInventoryInformation?MSG_TrafficDetectorInventoryRequest=UseLocationReference%HTTP/1.1'
request = urllib.request.Request(url_str,headers={"Accept":"text/xml"})
contents = urllib.request.urlopen(request).read()
root = ET.fromstring(contents)

stream=[]
z = root[2].getchildren()
length = len(z)

for i in range (0,length):
    x = root[2].getchildren()[i]
    try:
        sensor_name = x[2].text
        route = x[5].text
        lat = float(x[3][0].text)/1000000
        long = float(x[3][1].text)/1000000
        lane_type = x[8][0][2].text  
    except IndexError:
        pass
    else:
        approach_number = len(x[8].getchildren())
        
        for j in range (0, approach_number):
            x2 = root[2][i][8].getchildren()[j]
            try:
                lane_id = x2[3][0][0].text
                lane_name = x2[3][0][1].text
            except IndexError:
                pass
            else:
                info = (sensor_name+','+route+','+str(lat)+','+str(long)+','+lane_type+','+lane_id +','+lane_name)
                stream.append(info)

def want_format(stream):
    df_stream = pd.DataFrame(stream)
    
    columns = ['sensor','road', 'latitude','longtitude', 'lane_type','lane_id1','lane_name']
    df = pd.DataFrame(df_stream[0].str.split(',').tolist(),columns = columns)
    
    df['lane'] = df[['lane_id1', 'lane_name']].apply(lambda x: ','.join(x), axis=1)
    data = df.drop(['lane_id1', 'lane_name'], axis=1)
    data_mod = data.groupby(by=['sensor','road', 'latitude','longtitude', 'lane_type'])['lane'].apply(','.join).reset_index()
    
    # Split laneid and name
    data_mod[['lane1','name1', 'lane2','name2', 'lane3','name3','lane4','name4']]= data_mod['lane'].str.split(',',expand=True)
    data_mod = data_mod.drop(['lane'],axis=1)
    # remove space ahead
    data_mod.sensor = data_mod.sensor.str.strip()
    data_mod.fillna(value='nan', inplace=True)
    return data_mod
	
	
df = want_format(stream)
df.to_csv('sensor_info.csv', index = None)