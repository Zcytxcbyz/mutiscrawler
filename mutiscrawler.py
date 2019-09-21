# -*- coding: UTF-8 -*-

import os
import re
import requests
import lxml
import time
import random
import sqlite3
import webbrowser
import threading
import multiprocessing
from multiprocessing import Process
from bs4 import BeautifulSoup

#https://www.curseforge.com/minecraft/mc-mods
baseurl = "https://www.curseforge.com"

def download(url, path):
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)
        f.close()

def gethtml(url):
    try:
        response = requests.get(url)
        content = response.content.decode("utf-8")
        soup = BeautifulSoup(content, "lxml")
        return soup
    except:
        print('Raised an exception')

def FirstGrasp(page, databasefilename, ProcessId):
    try:
        thread = []
        url = baseurl + "/minecraft/mc-mods?page=" + str(page)
        result = gethtml(url).find_all("h3", class_ = "text-primary-500 font-bold text-lg hover:no-underline")
        threadId = 0
        for item in result:
            modname = item.text
            modaddress = item.parent['href']
            td =  threading.Thread(target = SecondGrasp, args = (modname, modaddress, databasefilename, page, threadId))
            td.start()
            thread.append(td)
            threadId += 1
        for trd in thread:
            trd.join()
        thread.clear()
    except:
        print('Raised an exception')

def SecondGrasp(modname, modaddress, databasefilename, page, threadId):
    try:   
        url = baseurl + modaddress + "/files"
        downloads = gethtml(url).find('span', class_ = "mr-2 text-sm text-gray-500").text
        downloads = re.sub(re.compile('[^0-9]'), '', downloads)
        result = gethtml(url).find('h3', class_ = "text-primary-500 text-lg")
        url = baseurl + result.parent['href']
        result = gethtml(url).find('span', text = "Filename")
        result = result.parent.find('span', text = re.compile('\.jar'))
        filename = result.text
        fileaddress = re.sub('files', 'download', url) + "/file"
        url = re.sub(re.compile('files.*'), 'relations/dependencies?filter-related-dependencies=3', url)
        result = gethtml(url).find_all('h3', class_ = 'text-primary-500 font-bold text-lg hover:no-underline')
        dependencies = ""
        for item in result:
            dependencies += item.text + ","
        dependencies = re.sub(re.compile(',(?!.)'), '', dependencies)
        modaddress = baseurl + modaddress
        modsname = re.sub("'", "''", modname)
        dependencie = re.sub("'", "''", dependencies)
        filenames = re.sub("'", "''", filename)
        try:
            conn = sqlite3.connect(databasefilename)
            c = conn.cursor()
            sqlcommand = "INSERT INTO ModList(Modname,Modaddress,Filename,Fileaddress,Dependencies,Downloads) VALUES('%s','%s','%s','%s','%s','%s');"%(modsname, modaddress, filenames, fileaddress, dependencie, downloads)
            c.execute(sqlcommand)
            conn.commit()
            conn.close()
        except:
            print('Raised an exception')
            fo = open("errinfo.txt", "a")
            fo.write("Error Mod:" + modname + "," + modaddress + "," + filename + "," + fileaddress + "," + dependencies + "," + downloads + "\n")
            fo.close()
        info = str(page) + ':' + modname + '\n' + modaddress + '\n' + filename + '\n' + fileaddress + '\n' + dependencies
        print(info)
    except:
        print('Raised an exception')

if __name__ == '__main__':
    try:
        databasefilename = str(int(time.time()))
        for j in range(3):
            databasefilename += str(random.randint(0, 9))
        databasefilename += ".db"
        conn = sqlite3.connect(databasefilename)
        c = conn.cursor()
        c.execute('''CREATE TABLE ModList(
            Modname  TEXT,
            Modaddress TEXT,
            Filename TEXT,
            Fileaddress TEXT,
            Dependencies TEXT,
            Downloads TEXT
            );''')
        conn.commit()
        conn.close()
        page = int(input('page:'))
        openpage = input('Do you want to open a web page?')
        start = time.time()
        match = re.match(r'(yes)|y', openpage, re.I)
        if match:
            webbrowser.open("https://www.curseforge.com/minecraft/mc-mods")
        i = 1
        cpucount = multiprocessing.cpu_count() // 2
        threads = []
        if page > cpucount:
            while i <= page - cpucount: 
                for item in range(cpucount):
                    p = Process(target = FirstGrasp, args = (i + item, databasefilename, item,))
                    p.start()
                    threads.append(p)
                for t in threads:
                    t.join()
                threads.clear()
                i += cpucount
        else:
            FirstGrasp(page , databasefilename)
        elapsed = round(time.time() - start, 3)
        print("Time used:", elapsed, "s")
    except:
        print('Raised an exception')
    finally:
        input('Press any key to continue.')
    
