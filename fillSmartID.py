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
#import random
import time
import login
from getRowFromExcel import itemInfo

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
#This example requires Selenium WebDriver 3.13 or newer
# =============================================================================
with webdriver.Chrome(ChromeDriverManager().install()) as driver:
    wait = WebDriverWait(driver, 10)
    url = login.url
    user = login.user
    pwd = login.pwd
    def addCode(f):
        qrcode = itemInfo['qrcode']
        date = itemInfo['date']
        f(qrcode, date)

    def goForward(code, date):
        driver.get(url+code)
        expectedpage = wait.until(EC.presence_of_element_located((By.ID, 'id')))
        if (expectedpage):
            createProdDict(code)
            addToScanLog(date, code)    
        else:
            spans = driver.get_elements_by_tagname('span')
            for span in spans:
                print(span.text)

    def login(url, user, pwd, f):
        driver.get(url+'account/login')
        #time.sleep(5)
        elUsername = wait.until(EC.presence_of_element_located((By.ID, 'un')))
        elUsername.clear()
        elUsername.send_keys(user)
        elPwd = driver.find_element(By.ID, 'pw')
        elPwd.send_keys(pwd + Keys.RETURN)
        addCode(f)
        
    
    def createProdDict(code):
        prodDict = {}
        #print([driver.find_element(By.ID, 'id').get_attribute('innerHTML'), code, bool(driver.find_element(By.ID, 'id').get_attribute('innerHTML') == code)])
        print(driver.find_element(By.ID, 'id').text)
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
            
        else:
            #print(driver.wait.until(EC.presence_of_element_located((By.ID, 'id'))).text + ' was found instead')
            errorLog.append([code, ' not found'])
        prodList.append(prodDict)
        #return prodDict

    def addToScanLog(date, code):
        dateTable = driver.find_element(By.ID, 'tbl_scan')
        dateText = dateTable.find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML') or ''
        if dateText >= date:
            successLog.append([code, 'already has scan date recorded', dateText])
            datesScanned.append({
                'qrcode': code,
                'scanDate': dateText
                })
            #goForward(code,date)
        else:
            driver.find_element(By.ID, 'btn_scan_log').click()
            elDate = wait.until(EC.presence_of_element_located((By.ID, 'date')))
            elDate.click()
            elDate.clear()
            elDate.send_keys(date + Keys.ENTER)
            elDate.submit()
            #wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Update Scan Results'))).click()
            checkScanDate(date, code)
    
    def checkScanDate(date, code):
        #time.sleep(1)
        #driver.find_element(By.ID, 'btn_scan_log').click()
        #wait.until(EC.visibility_of_element_located((By.ID, 'btn_scan_log'))).click()
        dateTable = driver.find_element(By.ID, 'tbl_scan')
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
            print('new scan date ' + dateText + ' added for ' + code)
            successLog.append([code, 'has new scan date recorded', dateText])
            datesScanned.append({
                'qrcode': code,
                'scanDate': dateText
                })
        elif dateText < date:
            print('new scan date not added. Last scan was' + dateText)
            errorLog.append([code, 'Date not added; last date = ' + dateText])
        else:
            errorLog.append([code, 'Date not added; No scan dates available.'])
        
                                                        
                                                        
    login(url, user, pwd, goForward) 

        

print(prodList)    
print(errorLog)  
print(successLog) 
print(datesScanned)
        
    
