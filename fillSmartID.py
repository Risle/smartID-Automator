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
import pandas as pd
from bs4 import BeautifulSoup
# =============================================================================
# import pymongo
# import certifi
# import urllib3
# 
# #urllib3.contrib.pyopenssl.inject_into_urllib3()
# http = urllib3.PoolManager(
#     cert_reqs='CERT_REQUIRED',
#     ca_certs=certifi.where()
#     )
# 
# client = pymongo.MongoClient(
#     login.conn_str, 
#     serverSelectionTimeoutMS=5000,
#     ssl=True,
#     ssl_ca_certs=http)
# 
# =============================================================================


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--incognito")



global prodList
prodList = []
global errorLog
errorLog = []
global successLog
successLog = []
global datesScanned
datesScanned = []

# =============================================================================
# try:
#     print(client.server_info())
# except Exception:
#     print("Unable to connect to the server.")
# =============================================================================

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
    healthSystem = login.healthSystem
    rejectedItems = login.rejectedItems
 
# Access QR codes from Excel sheet of scanned items         
    def getQRCodes(dataPath, rowStart, rowEnd):
        #TODO Figure out which log recording is the one actually working
        if (rowStart <= rowFinal) and (rowStart <= rowEnd):
            data = pd.read_excel (dataPath)
            #thisRow = data.iloc[row]
            QRCodes = data.values.T[4].tolist()
            for row in range(rowStart, rowEnd):
                try:
                    qrcode = QRCodes[row].lower()
                    print(qrcode)
                    if hasPassedInspection(qrcode):
                        goForward(url, qrcode, date, row)
                    else:
                        print(qrcode + ' did not pass inspection.')
                except AttributeError:
                    print('AttributeError: it appears the code in row ' + str(row) + ' may not actually be a code')
                    return recordLogs()
                except IndexError:
                    print('IndexError: Remove empty row ' + str(row))
                    return recordLogs()
        else:
            print('all requested rows are complete')
            successLog.append(['0', ', all requested rows are complete'])
        recordLogs()

# Stop if items failed inspection
    def hasPassedInspection(code):
        if code in rejectedItems:
            return False
        else:
            return True
        
# Look up the lead item webpage that corresponding to the input QR code.
    def goForward(url, code, date, row):
        try:
            print(code + ', going forward on row ' + str(row))
            expectedpage = wait.until(EC.presence_of_element_located((By.ID, 'id')))
            print(str(expectedpage.text))
            if (expectedpage):
                createProdDict(code, row)
                addScanDate(date, code)  
                print (code + ', matches url')
            else:
                spans = driver.get_elements_by_tagname('span')
                for span in spans:
                    print(span.text)
                print(code + ' not found')
        except TimeoutException:
            print(code + ' not found; timeout exception')
            #getQRCodes(dataPath, row+1, rowFinal)
            errorLog.append([code, ' not found; timeout exception'])
            
# Log into Website
    def login(url, user, pwd, f):
        driver.get(url+'account/login')
        #time.sleep(5)
        elUsername = wait.until(EC.presence_of_element_located((By.ID, 'un')))
        elUsername.clear()
        elUsername.send_keys(user)
        elPwd = driver.find_element(By.ID, 'pw')
        elPwd.send_keys(pwd + Keys.RETURN)
        getQRCodes(dataPath, rowInitial, rowFinal)



# =============================================================================
# # Verify the lead item for that QR code is in inventory       
#     def inInventory(product):
#         editBtn = driver.find_element(By.ID, 'btn_edit')
#         editBtn.click()
#         print('editing item...')
#         wait.until(EC.element_to_be_clickable(By.ID, 'company_id'))
#         #wait.until(EC.presence_of_element_located(By.className, 'editable-input'))
#         elCompany = driver.find_element_by_xpath('//span[@id, "company_id"]/following-sibling::span')
#         optCompany = elCompany.find_elements_by_tag_name('option').text
#         print(optCompany)
# =============================================================================

# Filter elements by a specified class
    def match_class(target):                                                        
        def do_match(tag):                                                          
            classes = tag.get('class', [])                                          
            return all(c in classes for c in target)                                
        return do_match 

    def addRequiredInfo(code, row, toFix):
        print('got to the final')
        editBtn = driver.find_element_by_id('btn_edit')
        editBtn.click()
        for info in toFix:
            print(info)
            if info == 'Health System':
                addInfoHelper(login.healthSystem, info)
            elif info == 'Location':
                addInfoHelper('DEACONESS', info)
            elif info == 'Department':
                addInfoHelper('CATH LAB', info)
                
    def addInfoHelper(fixedInfo, IDToFix):
        elToFix = wait.until(EC.element_to_be_clickable((By.ID, IDToFix))).click()
        for option in elToFix.find_elements_by_tag_name('options'):
            if option.text() == fixedInfo():
                option.click()
        elToFix.send_keys(Keys.RETURN)
        print('made it')
        
# Read item details listed on the website          
    def createProdDict(code, row):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prodDict = {}
        #print([driver.find_element(By.ID, 'id').get_attribute('innerHTML'), code, bool(driver.find_element(By.ID, 'id').get_attribute('innerHTML') == code)])
        print(driver.find_element(By.ID, 'id').text + ', found by createProdDict')
        if code == driver.find_element(By.ID, 'id').get_attribute('innerHTML').lower():
            #allInfo1 = driver.find_element(By.ID, 'product-data')
            allInfo2 = soup.find(id='product-data')
            #for elem in allInfo1.find_elements(By.TAG_NAME, 'li'):
            needsFixin = []
            for child in allInfo2.find_all(match_class(['required'])):
                text = []
                for string in child.parent.parent.strings:
                    text.append(string)
                if len(text[len(text)-1]) > 1: # If required fields are complete
                    print(text[0])
                    needsFixin.append(text[0])
                else:
                    print('all required info present')
            #company = allInfo2.find(id='company_id')
            #print('got to company')
            if len(needsFixin) > 0:
                addRequiredInfo(code, row, needsFixin)
            return
            
# =============================================================================
#             prodDict['qrcode'] = code
#             prodDict['description'] = wait.until(EC.presence_of_element_located((By.ID, 'name'))).text or 'no description'
#             prodDict['company'] = wait.until(EC.presence_of_element_located((By.ID, 'company_id'))).text or 'no company'
#             prodDict['location'] = driver.find_element(By.ID, 'location_id').text or 'no location'
#             prodDict['department'] = driver.find_element(By.ID, 'department_id').text or 'no department'
#             prodDict['type'] = driver.find_element(By.ID, 'type_id').text or 'no type'
#             successLog.append([code, ' found'])
# =============================================================================
           # checkProdInfo(prodDict)   
        else:
            print(code + ', not found by createProdDict')
            #print(driver.wait.until(EC.presence_of_element_located((By.ID, 'id'))).text + ' was found instead')
            errorLog.append([code, ', not found'])
        prodList.append(prodDict)
        #return prodDict

# Add new scan date on webpage for lead item
    def addScanDate(date, code):    
        try:
            dateTable = driver.find_element(By.ID, 'tbl_scan') or ''
            dateText = dateTable.find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML') or ''
            #dateFormat = '%Y-%m-%d'
            if dateText >= date:
                print(code + ', already has scan date recorded, ' + dateText)
                successLog.append([code, ', already has scan date recorded for, ' + dateText])
                datesScanned.append([code, ', already has recent scan recorded for, ' + dateText])
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
            print(code + ', does not have a scan log')
            errorLog.append([code, ', does not have a scan log'])
    
# Verify if new scan date has been added
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
        
    
