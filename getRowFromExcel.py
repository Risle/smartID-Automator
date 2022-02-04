#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 11:21:15 2021

@author: poff
"""
import pandas as pd
import login


counter = 0
itemInfo = {}

def getData(url, row, dataPath):
    #dataPath = login.pathToData
    data = pd.read_excel (dataPath)
    #url = login.url
    #getDateColumn(pathToExcel, columnLabel) 
    #iterator(processInfo, data, url, counter)
    return processInfo(data, url, row)
    
def getItemInfo(data, row):
    thisRow = data.iloc[row]
    date = thisRow['Date']
    hospital = str(thisRow['Hospital'])
    department = str(thisRow['Department'])
    QRcode = str(thisRow['QR code'])
    lookup = 'page ' + str(thisRow['Page']) + ' #' + str(thisRow['#'])
    return [date, hospital, department, QRcode, lookup]

#def processItem(f1, f2, f3, itemInfo):
    #for each row:
    #appendToUrl
    #check hospital
    #check department
    #check last date
    #input date

def appendToUrl(data, row, url):
    qrcode = getItemInfo(data, row)
    #print(url + qrcode[3])
    return url + qrcode[3]

def findDate(data, row):
    #print(str(pd.Timestamp.date(getItemInfo(data, row)[0])))
    return str(pd.Timestamp.date(getItemInfo(data, row)[0]))

# def iterator(f, data, url, row):
#     f(data, url, row) 
#     global counter
#     counter += 1

def processInfo(data, url, row):
    info = ({
        'qrcode': getItemInfo(data, row)[3].lower(),
        'location': getItemInfo(data, row)[1].upper(),
        'department': getItemInfo(data, row)[2],
        'url': appendToUrl(data, row, url),
        'date': findDate(data, row),
        'lookup': getItemInfo(data, row)[4]
        })
    itemInfo.update(info)
    return info
    

#getData(login.url, 1, login.dataPath)
#getData(login.url, 2, login.dataPath)
#print(itemInfo)
