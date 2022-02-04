#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 21:04:49 2022

@author: poff
"""
import login
#from getRowFromExcel import itemInfo
import pandas as pd

global prodList
prodList = []
global errorLog
errorLog = []
global successLog
successLog = []
global datesScanned
datesScanned = []

def addEntries(log, entry):
    log.append(entry)

addEntries(errorLog, ['asdf','something went wrong'])
print(type(errorLog) == list)

def recordLogs():
    logs = {
        'productsFound.csv': prodList,
        'errorLog.csv': errorLog,
        'successLog.csv': successLog,
        'lastScanDates.csv': datesScanned,
        }
    for filename,log  in logs.items():
        df = pd.DataFrame(log, columns=['QR code', 'message'])
        df['Time'] = str(pd.Timestamp.now())
        df.to_csv(login.logPath + filename, mode='a', header=False)
        # for entry in log:     
        #     df = df.append(
        #         {
        #         'QR code':entry[0], 
        #         'message':entry[1], 
        #         'Time':str(pd.Timestamp.now())
        #         }, ignore_index=True)
    #errorDR.loc[len(errorDR.index)] = pd.Series({'QR code':entry[0], 'message':entry[1], 'Time':2})
       # df.to_csv(login.logPath + filename, mode='a', header=False)    
#addEntries(successLog,['code','it has been done'])
#recordLogs()

a = [0,1,2,3,4,5]
for num in a:
    print(num)
    if num >= 5:
        print('got to end')
print(login.logPath)