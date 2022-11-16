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
    rowInitial = login.rows[0]-2
    rowFinal = login.rows[1]
    date = login.date
    healthSystem = login.HealthSystem
    location = login.Hospital
    rejectedItems = login.rejectedItems
 
# Access QR codes from Excel sheet of scanned items         
    def getQRCodes(dataPath, rowStart, rowEnd):
        if (rowStart <= rowFinal) and (rowStart <= rowEnd):
            data = pd.read_excel (dataPath)
            QRCodes = data.values.T[4].tolist()
            DEPT = data.values.T[2].tolist()
            for row in range(rowStart, rowEnd):
                print(row)
                try:
                    qrcode = QRCodes[row].lower()
                    dept = DEPT[row].upper()
                    print(qrcode)
                    if hasPassedInspection(qrcode):
                        goForward(url, qrcode, date, row, dept)
                    else:
                        print(qrcode + ' did not pass inspection.')
                except AttributeError:
                    print('AttributeError: it appears the code in row ' + str(row) + ' may not actually be a code')
                    recordLogs()
                except IndexError:
                    print('IndexError: Remove empty row ' + str(row))
                    recordLogs()
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
        driver.get(url+'account/login')
        elUsername = wait.until(EC.presence_of_element_located((By.ID, 'un')))
        elUsername.clear()
        elUsername.send_keys(user)
        elPwd = driver.find_element(By.ID, 'pw')
        elPwd.send_keys(pwd + Keys.RETURN)
        getQRCodes(dataPath, rowInitial, rowFinal)

# Filter elements by a specified class
    def match_class(target):                                                        
        def do_match(tag):                                                          
            classes = tag.get('class', [])                                          
            return all(c in classes for c in target)                                
        return do_match 

    def addInfoHelper(fixedInfo, IDToFix):
        print('editing required info...')
        try:
            elReq = wait.until(EC.element_to_be_clickable((By.ID, IDToFix)))
            elReq.click()
            print('found edit button')
            form = driver.find_element_by_tag_name('form')
            select = Select(form.find_element_by_tag_name('select'))
            select.select_by_visible_text(fixedInfo)
            form.submit()
            print('made it. Added ' + fixedInfo)
        except AttributeError:
            print('cant find edit button')   
            
    def addRequiredInfo(code, row, toFix, dept):
        print('got to the fixin')
        editBtn = driver.find_element_by_id('btn_edit')
        editBtn.click()
        try:
            for info in toFix:
                print(info[0] + ' has value of ' + info[1])
                if info[0] == 'Health System':
                    print('adding ' + healthSystem + '...')
                    addInfoHelper(healthSystem, 'company_id')
                    print('added ' + info[1])
                elif info[0] == 'Location':
                    print('adding' + location)
                    addInfoHelper(location, 'location_id')
                    print('added' + location)
                elif info[0] == 'Department':
                    print('adding' + dept + '...')
                    addInfoHelper(dept, 'department_id')
                    print('added' + dept)
                else:
                    print('no required info added for ' + info[0] + ' ' + info[1])
        except AttributeError:
            print('AttributeError. No required info added')
        editBtn.click()
        print('ended fixins')
                
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
                for string in child.parent.parent.strings:
                    text.append(string)
                if text[len(text)-1] == 'Not Selected':
                    print(text[0] + 'has no value')
                    needsFixin.append(text)
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
            prodDict['location'] = driver.find_element(By.ID, 'location_id').text or 'no location'
            prodDict['department'] = driver.find_element(By.ID, 'department_id').text or 'no department'
            prodDict['type'] = driver.find_element(By.ID, 'type_id').text or 'no type'
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

        
    
