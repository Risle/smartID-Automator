#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 23:49:27 2021

@author: poff
"""
import pandas as pd
import fillSmartID as web
import login
from getRowFromExcel import itemInfo
from getRowFromExcel import getData
#import test
#from test import testArray


def startUp():
    url = login.url
    user = login.user
    pwd = login.pwd
    web.login(url, user, pwd) 
    
def startItem(url, qrcode, date):
    #qrcode = itemInfo['qrcode']
    #date = itemInfo['date']
    web.goForward(url, qrcode, date)

def iterateData(url):
    counter = 6
    itemData = []
    #for i in range
    itemData.append(getData(url, counter, login.dataPath))
    #qrcode = itemData[len(itemData)-1]['qrcode']
    print(itemData)
    startItem(url, itemData[len(itemData)-1]['qrcode'], itemData[len(itemData)-1]['date'])
    
def addTimeStamp(df):
    df['time stamp'] = str(pd.Timestamp.now())
    
def makeLogs(log, filename):
    #data = pd.read_excel(login.dataPath)
    # Convert lists and dicts to dataframes
    if type(log[0]) is dict:
        df = pd.DataFrame.from_dict(log)
    else:
        df = pd.DataFrame(log, columns=['QR codigo', 'mensaje', 'Ultima Fecha'])
    df['time stamp'] = str(pd.Timestamp.now())
    df.to_csv(login.logPath + filename, mode='a')
    
    # dfProdList = pd.DataFrame.from_dict(prodList)
    # dfSuccessLog = pd.DataFrame(successLog, columns=['QR codigo', 'mensaje', 'Ultima Fecha'])
    # dfErrorLog = pd.DataFrame(errorLog, columns=['QR codigo', 'mensaje', 'Ultima Fecha'])
    # dfDatesScanned = pd.DataFrame.from_dict(datesScanned, columns=['QR codigo', 'Ultima Fecha'])
    # # Add timestapm and append to log files
    # dfProdList.addTimeStamp().to_csv(login.logPath + 'prodlist.csv', mode='a')
    # dfSuccessLog.addTimeStamp().to_csv(login.logPath + 'successlog.csv')

#makeLogs(testArray, 'prodList.csv')


    
#iterateData(login.url)
#print(itemInfo)