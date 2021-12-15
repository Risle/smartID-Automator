#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 11:21:15 2021

@author: poff
"""
import pandas as pd
#/home/poff/Projects/Technology/python/2021AutomateWeb/SAMPLE_2021_DH_lead_codes.xlsx


counter = 0

def getData():
    pathToExcel = '/home/poff/Projects/Technology/python/2021AutomateWeb/SAMPLE_2021_DH_lead_codes.xlsx'
    data = pd.read_excel (pathToExcel)
    url = 'https://yoursmartid.com/'
    #getDateColumn(pathToExcel, columnLabel) 
    iterator(processInfo, data, url, counter)
    iterator(processInfo, data, url, counter)
    #processInfo(data, url, row)
    
def getItemInfo(data, row):
    thisRow = data.iloc[row]
    date = thisRow['Date']
    hospital = str(thisRow['Hospital'])
    department = str(thisRow['Department'])
    QRcode = str(thisRow['QR code'])
    lookup = 'page ' + str(thisRow['Page']) + ', # ' + str(thisRow['#'])
    return [date, hospital, department, QRcode, lookup]

#def processItem(f1, f2, f3, itemInfo):
    #for each row:
    #appendToUrl
    #check hospital
    #check department
    #check last date
    #input date

def appendToUrl(data, row, url):
    itemArray = getItemInfo(data, row)
    print(url + itemArray[3])
    return url + itemArray[3]

def findDate(data, row):
    print(str(pd.Timestamp.date(getItemInfo(data, row)[0])))
    return str(pd.Timestamp.date(getItemInfo(data, row)[0]))

def iterator(f, data, url, row):
    f(data, url, row) 
    global counter
    counter += 1

def processInfo(data, url, row):
    getItemInfo(data, row)
    appendToUrl(data, row, url)
    findDate(data, row)
    
getData()

