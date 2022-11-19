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
from selenium.webdriver.support.ui import Select
import login
import pandas as pd
from bs4 import BeautifulSoup
import pymongo
from mongo import qrCodesNotDone
from mongo import recordToDB


client = pymongo.MongoClient('localhost', 27017)
db = client['smartID']
s = db['s2022']

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

def recordLogs():
    # for success in successLog:
    #     if success[2].__contains__('has scan'):
    if len(successLog) > 0:
        success = []
        for item in successLog:
            print(item)
            if str(item[1]).__contains__('scan date'):
                success.append({str(item[0]): True})
        recordToDB(success)
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
            df = pd.DataFrame(log, columns=['QR code', 'message'])
        df['Time'] = str(pd.Timestamp.now())
        df.to_csv('/home/poff/Projects/Technology/python/2021AutomateWeb/smartid/logs/' + filename, mode='a', header=False)   
        
with webdriver.Chrome(ChromeDriverManager().install()) as driver:
    wait = WebDriverWait(driver, 3)
    url = login.url
    user = login.user
    pwd = login.pwd
    dataPath = login.dataPath
    date = login.date
    healthSystem = login.HealthSystem
    location = login.Hospital
    rejectedItems = login.rejectedItems
 
# Access QR codes from Excel sheet of scanned items         
    def getQRCodes(docs):
        for i, doc in enumerate(docs):
            code = doc['scanned_QR'].lower()
            dept = doc['scanned_dept']
            try:
                if hasPassedInspection(code):
                    goForward(url, code, date, i, dept)
                else:
                    print(code + ' did not pass inspection.')
            except AttributeError:
                print('AttributeError: it appears the code in row ' + str(i) + ' may not actually be a code')
                recordLogs()
            except IndexError:
                print('IndexError: Remove empty row ' + str(i))
                recordLogs()
        else:
            print('all requested rows are complete')
            successLog.append(['0', ', all requested rows are complete'])
        recordLogs()

# Stop if items failed inspection
    def hasPassedInspection(code):
        if code.upper() in rejectedItems:
            return False
        else:
            return True
        
# Look up the lead item webpage that corresponding to the input QR code.
    def goForward(url, code, date, row, dept):
        try:
            print(code + ', going forward on row ' + str(row))
            driver.get(url+code)
            expectedpage = wait.until(EC.presence_of_element_located((By.ID, 'id')))
            print('got to expected page')
            if (expectedpage):
                createProdDict(code, row, dept)
                addScanDate(date, code)  
                print (code + ', matches url')
            else:
                spans = driver.get_elements_by_tagname('span')
                for span in spans:
                    print(span.text)
                print(code + ' not found')
        except TimeoutException:
            print(code + ' not found; timeout exception')
            errorLog.append([code, ' not found; timeout exception'])
            
# Log into Website
    def login(url, user, pwd, f):
        try:
            driver.get(url+'account/login')
            elUsername = wait.until(EC.presence_of_element_located((By.ID, 'un')))
            elUsername.clear()
            elUsername.send_keys(user)
            elPwd = driver.find_element(By.ID, 'pw')
            elPwd.send_keys(pwd + Keys.RETURN)
            getQRCodes(qrCodesNotDone())
        except KeyboardInterrupt:
            print('you stopped this')
            recordLogs()
            

# Filter elements by a specified class
    def match_class(target):                                                        
        def do_match(tag):                                                          
            classes = tag.get('class', [])                                          
            return all(c in classes for c in target)                                
        return do_match 

    def addInfoHelper(fixedInfo, IDToFix, code, elem):
        print('editing required info...')
        try:
            elReq = wait.until(EC.element_to_be_clickable((By.ID, IDToFix)))
            elReq.click()
            print('found edit button')
            #el = elem.wait.until(EC.presence_of_element_located(By.TAG_NAME, 'strong'))
            #driver.find_elements_by_tag_name('strong')
            form = wait.until(EC.element_to_be_clickable(By.TAG_NAME, 'form'))
               # elem.find_element_by_tag_name('form'))
            #driver.find_element_by_tag_name('form')
            select = Select(form.find_element_by_tag_name('select'))
            wait.until(EC.presence_of_element_located((By.ID, IDToFix)))
            select.select_by_value()
            form.submit()
            print('made it. Added ' + fixedInfo)
        except AttributeError:
            print('cant find edit button')   
        except NoSuchElementException:
            print('info for ' + code + 'not found')
            errorLog.append([code, 'could not add required info'])
            
    def addRequiredInfo(code, row, toFix, dept):
        print('got to the fixin')
        editBtn = driver.find_element_by_id('btn_edit')
        editBtn.click()
        try:
            for info in toFix:
                field = info[1][0]
                entry = info[1][1]
                elem = info[0]
                print(field + ' has value of ' + entry)
                if field == 'Health System':
                    print('adding ' + healthSystem + '...')
                    addInfoHelper(healthSystem, 'company_id', code, elem)
                    print('added ' + entry)
                elif field == 'Location':
                    print('adding' + location)
                    addInfoHelper(location, 'location_id', code, elem)
                    print('added' + location)
                elif field == 'Department':
                    print('adding' + dept + '...')
                    addInfoHelper(dept, 'department_id', code, elem)
                    print('added' + dept)
                else:
                    print('no required info added for ' + info[0] + ' ' + info[1])
        except AttributeError:
            print('AttributeError. No required info added')
        editBtn.click()
        print(code + 'ended fixins')
                
    def addToActiveInventory(code):
        btns = driver.find_elements_by_class_name('ui-controlgroup-controls')
        isInInventory = False
        for btn in btns:
            if btn.text.__contains__('Add to Active Inventory'):
                btn.click()
                print(code + ' added to inventory')
                isInInventory = True
            elif btn.text.__contains__('Remove'):
                print(code + ' already in active inventory')
                isInInventory = True
        print(code + ' is in inventory? ' + str(isInInventory))

# Fix any missing required info and read item details listed on the website          
    def createProdDict(code, row, dept):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prodDict = {}
        print(driver.find_element(By.ID, 'id').text + ' found by createProdDict')
        if code == driver.find_element(By.ID, 'id').get_attribute('innerHTML').lower():
            allInfo2 = soup.find(id='product-data')
            needsFixin = []
            for i, child in enumerate(allInfo2.find_all(match_class(['required']))):
                text = []
                li = child.parent.parent
                for string in li.strings:
                    text.append(string)
                if text[len(text)-1] == 'Not Selected':
                    print(text[0] + 'has no value')
                    needsFixin.append([li, text])
            if len(needsFixin) > 0:
                addRequiredInfo(code, row, needsFixin, dept)
            else:
                print('all required info present')
            # Add to active inventory if not already
            addToActiveInventory(code)
            # Log details for completed items
            prodDict['qrcode'] = code
            prodDict['description'] = wait.until(EC.presence_of_element_located((By.ID, 'name'))).text or 'no description'
            prodDict['company'] = wait.until(EC.presence_of_element_located((By.ID, 'company_id'))).text or 'no company'
            prodDict['location'] = wait.until(EC.presence_of_element_located((By.ID, 'location_id'))).text or 'no location'
            prodDict['department'] = wait.until(EC.presence_of_element_located((By.ID, 'department_id'))).text or 'no department'
            prodDict['type'] = wait.until(EC.presence_of_element_located((By.ID, 'type_id'))).text or 'no type'
            successLog.append([code, ' found'])   
        else:
            print(code + ', not found by createProdDict')
            errorLog.append([code, ', not found'])
        prodList.append(prodDict)

# Add new scan date on webpage for lead item
    def addScanDate(date, code):    
        print('adding new scan date for ' + code)
        try:
            dateTable = driver.find_elements_by_id('tbl_scan')
            if len(dateTable) > 0:
                dateText = dateTable[0].find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML') or ''
                # dateFormat = '%Y-%m-%d'
                if dateText >= date:
                    print(code + ', already has scan date recorded, ' + dateText)
                    successLog.append([code, ', already has scan date recorded for, ' + dateText])
                    datesScanned.append([code, ', already has recent scan recorded for, ' + dateText])
                else:
                    print('scan log is present. ' + code + ', is having scan date added')
                    driver.find_element(By.ID, 'btn_scan_log').click()
                    elDate = wait.until(EC.presence_of_element_located((By.ID, 'date')))
                    elDate.click()
                    elDate.clear()
                    elDate.send_keys(date + Keys.ENTER)
                    elDate.submit()
                    checkScanDate(date, code)
            else:
                print(code + ', is having scan date added')
                driver.find_element(By.ID, 'btn_scan_log').click()
                elDate = wait.until(EC.presence_of_element_located((By.ID, 'date')))
                elDate.clear()
                elDate.send_keys(date + Keys.ENTER)
                elDate.submit()
                checkScanDate(date, code)
        except NoSuchElementException:
            print(code + ', does not have a scan log')
            errorLog.append([code, ', does not have a scan log'])
    
# Verify if new scan date has been added
    def checkScanDate(date, code):
        dateTable = driver.find_element(By.ID, 'tbl_scan') or ''
        dateText = dateTable.find_element_by_css_selector('span.edit-scan-date').get_attribute('innerHTML')
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

        
    
