#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import login
#from getRowFromExcel import itemInfo
import pandas as pd

#from getRowFromExcel import getData

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

#chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

global prodList
prodList = []
global errorLog
errorLog = []
global successLog
successLog = []
global datesScanned
datesScanned = []

def recordLogs():
    logs = {
        'productsFound.csv': prodList,
        'errorLog.csv': errorLog,
        'successLog.csv': successLog,
        'lastScanDates.csv': datesScanned,
        }
    for filename,log  in logs.items():
        if log == prodList:
            df = pd.DataFrame.from_dict(prodList)
        else:
            #TODO fix prodList log
            df = pd.DataFrame(log, columns=['QR code', 'message'])
        df['Time'] = str(pd.Timestamp.now())
        df.to_csv('/home/poff/Projects/Technology/python/2021AutomateWeb/smartid/logs/' + filename, mode='a', header=False)   
        

#This example requires Selenium WebDriver 3.13 or newer
# =============================================================================
with webdriver.Chrome(ChromeDriverManager().install()) as driver:
    wait = WebDriverWait(driver, 3)
    url = login.url
    user = login.user
    pwd = login.pwd
    dataPath = login.dataPath
    rowInitial = login.rows[0]-2
    rowFinal = login.rows[1]
    date = login.date
            
    def getQRCodes(dataPath, rowStart, rowEnd):
        #TODO Figure out which log recording is the one actually working
            if (rowStart <= rowFinal) and (rowStart <= rowEnd):
                data = pd.read_excel (dataPath)
                #thisRow = data.iloc[row]
                QRCodes = data.values.T[4].tolist()
                for row in range(rowStart, rowEnd):
                    try:
                        qrcode = QRCodes[row].lower()
                        goForward(url, qrcode, date, row)
                    except AttributeError:
                        print('AttributeError: it appears the code in row' + str(row) + ' may not actually be a code')
            else:
                print('all requested rows are complete')
                successLog.append(['0', ', all requested rows are complete'])
            recordLogs()
        

    def goForward(url, code, date, row):
        try:
            print(code + ', going forward on row, ' + str(row))
            driver.get(url+code)
            expectedpage = wait.until(EC.presence_of_element_located((By.ID, 'id')))
            if (expectedpage):
                createProdDict(code, row)
                addScanDate(date, code)  
                print (code + ', matches url')
            else:
                spans = driver.get_elements_by_tagname('span')
                for span in spans:
                    print(span.text)
                print(code + ', not found')
        except TimeoutException:
            print(code + ', not found; timeout exception')
            errorLog.append([code, ', not found; timeout exception'])
            

    def login(url, user, pwd, f):
        driver.get(url+'account/login')
        #time.sleep(5)
        elUsername = wait.until(EC.presence_of_element_located((By.ID, 'un')))
        elUsername.clear()
        elUsername.send_keys(user)
        elPwd = driver.find_element(By.ID, 'pw')
        elPwd.send_keys(pwd + Keys.RETURN)
        getQRCodes(dataPath, rowInitial, rowFinal)
        
    
    def createProdDict(code, row):
        prodDict = {}
        #print([driver.find_element(By.ID, 'id').get_attribute('innerHTML'), code, bool(driver.find_element(By.ID, 'id').get_attribute('innerHTML') == code)])
        print(driver.find_element(By.ID, 'id').text + ', found by createProdDict')
        #print(driver.find_element(By.ID, 'id').value)
        #print(driver.find_element(By.ID, 'id').get_property('attributes'))
        if code == driver.find_element(By.ID, 'id').get_attribute('innerHTML').lower():
            prodDict['qrcode'] = code
            prodDict['description'] = wait.until(EC.presence_of_element_located((By.ID, 'name'))).text or 'no description'
            prodDict['company'] = wait.until(EC.presence_of_element_located((By.ID, 'company_id'))).text or 'no company'
            prodDict['location'] = driver.find_element(By.ID, 'location_id').text or 'no location'
            prodDict['department'] = driver.find_element(By.ID, 'department_id').text or 'no department'
            prodDict['type'] = driver.find_element(By.ID, 'type_id').text or 'no type'
            successLog.append([code, ' found'])
            checkProdDetails(prodDict)
            
        else:
            print(code + ', not found by createProdDict')
            #print(driver.wait.until(EC.presence_of_element_located((By.ID, 'id'))).text + ' was found instead')
            errorLog.append([code, ', not found'])
        prodList.append(prodDict)
        

    def checkProdDetails(product):
        
        
        
    def addScanDate(date, code):    
        try:
            dateTable = driver.find_element(By.ID, 'tbl_scan') or ''
            dateText = dateTable.find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML') or ''
            #dateFormat = '%Y-%m-%d'
            if dateText >= date:
                print(code + ', already has scan date recorded, ' + dateText)
                successLog.append([code, ', already has scan date recorded for, ' + dateText])
                datesScanned.append([code, ', already has recent scan recorded for, ' + dateText])
                #goForward(code,date)
            else:
                print(code + ', is having scan date added')
                driver.find_element(By.ID, 'btn_scan_log').click()
                elDate = wait.until(EC.presence_of_element_located((By.ID, 'date')))
                elDate.click()
                elDate.clear()
                elDate.send_keys(date + Keys.ENTER)
                elDate.submit()
                #wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Update Scan Results'))).click()
                checkScanDate(date, code)
        except NoSuchElementException:
            checkProdDetails()
            print(code + ', does not have a scan log')
            errorLog.append([code, ', does not have a scan log'])
    
    def checkScanDate(date, code):
        #time.sleep(1)
        #driver.find_element(By.ID, 'btn_scan_log').click()
        #wait.until(EC.visibility_of_element_located((By.ID, 'btn_scan_log'))).click()
        dateTable = driver.find_element(By.ID, 'tbl_scan') or ''
        dateText = dateTable.find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML')
        #dateText = elScanDate.get_attribute('innerHTML')
        # scanDates = []
        # for elDate in elScanDates:
        #     dateText = elDate.get_attribute('innerHTML')
        #     #print(elDate.tag_name)
        #     #print(elDate.text)
        #     #print(elDate.get_attribute('value'))
        #     print(elDate.get_attribute('innerHTML'))
        #     #print(elDate.get_attribute('outerHTML'))
        #     #print(elDate.get_property('attributes'))
        #     #print(date)
        #     scanDates.append(elDate.get_attribute('innerHTML'))
        if dateText >= date:
            print(code + ', new scan date, ' + dateText + ' added')
            successLog.append([code, ', has new scan date recorded, ' + dateText])
            datesScanned.append([code, ', successfully has new scan date recorded for, ' + dateText])
        elif dateText < date:
            print(code + 'new scan date not added. Last scan was, ' + dateText)
            errorLog.append([code, ', Date not added; last date was, ' + dateText])
        else:
            print(code + ', Date not added; No scan dates available.')
            errorLog.append([code, ' Date not added; No scan dates available.'])
                                                        
    login(url, user, pwd, goForward) 
    recordLogs()

        

# print(prodList)    
# print(errorLog)  
# print(successLog) 
# print(datesScanned)
        
    
