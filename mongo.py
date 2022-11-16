#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 19:31:06 2022

@author: poff
"""
import pymongo
import pandas as pd
import login

client = pymongo.MongoClient('localhost', 27017)
db = client['smartID']
s = db['s2022']
#data = pd.read_excel(dataPath)

logPath = login.logPath
errorLog = logPath + 'errorLog.csv' #QR codes on column 2
successLog = logPath + 'successLog.csv' #QR codes on column 2. Must contain 'scan date' in column 3
successNote = 'scan date'
# From website. QR code (col2), description (col 3), dept (col 4), type (col 7)
prodList = logPath + 'productsFound.csv'
rejectedItems = login.rejectedItems



# Mark failed scan items (run once)
def passedScan(coll, failList):
    for item in rejectedItems:
        coll.update_many({'scanned_QR': item}, {'$set': {'passed2022': False}})

# Find duplicate QR codes in database
def notUnique(coll):
    codes = []
    cursors = coll.find({'scanned_QR': {'$exists': True}})
    for cursor in cursors:
        codes.append(cursor['scanned_QR'])
    # #l = [item for item in cursors]
    # for i, code in enumerate(codes):
    #     if codes.count(code['scanned_QR']) > 1:
    #         notUniq.append(doc)
    notUniq = [code for code in codes if codes.count(code) > 1]
    for code in notUniq:
        for doc in coll.find({'scanned_QR': code}):
            print(doc)
    return notUniq

def changeCD (coll, code):
    CDnum = []
    for doc in coll.find({'scanned_QR': code}):
        if 'scanned_CD' in doc:
            CD = doc['scanned_CD']
            if 'scanned_Cdnum' in doc:
                num = doc['scanned_Cdnum']
        #print('Code: ' + code + ' was scanned on CD ' + CD + ', no. ' + num)
                if type(CD) == 'string':
                    if CDnum.count({CD : num}) < 1: 
                        CDnum.append({CD : num})
    #print(str(CDnum[0][0]))
                if type(CD) == 'list':
                    coll.update_many({'scanned_QR': code}, {'$set': {'scanned_CD': CDnum}})
                    coll.update_many({'scanned_QR': code}, {'$unset': {'scanned_CDnum': ''}})
        
        
def rmDuplicates(coll, duplicates):
    for code in duplicates:
        changeCD(coll, code)
        duplDocs = []
        for doc in coll.find({'scanned_QR': code}):
            print('Code: ' + code)
            print('Dept: ' + doc['scanned_dept'])    
            #print('Dept specific: ' + doc['scanned_dept_specific'])
            duplDocs.append(doc['_id'])
        for doc in duplDocs:
            if len(duplDocs) > 1:
                coll.delete_one({'_id': doc})
                duplDocs.pop()

def isRecorded(coll, qr, answer):
    if coll.find({'scanned_QR': qr}):
        coll.update_many({'scanned_QR': qr}, {'$set': {'recorded2022': answer}})

def recordLog(log, bl):
    df = pd.read_csv(log) 
    logD = df.to_dict('records')
    recorded = []
    for i, record in enumerate(logD):
        #print(i, record)
        if bl == True:
            codeP = record['l4g0']
            if record[' found'].__contains__('scan date'):
                alreadyRecorded = False
                for item in recorded:
                    if item == {codeP: True}:
                        alreadyRecorded = True
                        print(str(i) + ': ' + 'success already recorded for ' + codeP)
                    elif item == {codeP: False}:
                        alreadyRecorded = True
                        item = {codeP: True}
                        print('new success for ' + codeP)
                if not alreadyRecorded:
                    recorded.append({codeP: True})
                    print(str(i) + ': ' + codeP + ' is now recorded')
        elif bl == False:
            codeF = record['zwdr']
            if record[', does not have a scan log'].__contains__('not'):
                alreadyRecorded = False
                if len(recorded) > 0:
                    for item in recorded:
                        print(item)
                        if item == codeF:
                            alreadyRecorded = True
                            print(str(i) + ': ' + codeF + 'already recorded as ' + str(recorded[item]))
                if not alreadyRecorded:
                    #print(str(i) + ': ' + codeF + ' has not been successfully recorded')
                    recorded.append({codeF: False})
    return recorded #array of {codeF, bool} if item has been recorded correctly in website

def recordToDB(coll, log):
    for item in log: 
        for key in item.keys():
            code = key.upper()
            print(code)
        if coll.find_one({'$and':[{'scanned_QR': code}, {'scan_recorded': {'$nin': [True]}}]}):
            print('found ' + code)
            coll.update_one({ 'scanned_QR' : code}, {'$set': {'scan_recorded': item[key]}})
    
recordToDB(s, recordLog(successLog, True))
#passedScan(s, rejectedItems)
#print(s.find_one({'scanned_QR':'L4G0'}))
#recordLog(successLog, True)