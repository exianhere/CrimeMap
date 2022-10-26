import requests 
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os

titles = []
links = []
pubDates = []
guids = []
descriptions = []



class Scraper:
    #Scraper constructor takes filename consisting links of the websites to be scraped and extracts them
    def __init__(self,filename):
        self.crawlinglinks = []
        reader = open(filename,"r")
        lines = reader.readlines()
        for line in lines:
            currentLine  = line.split(",")
            for value in currentLine:
                self.crawlinglinks.append(value)

    #crawl function takes soup object as an argument to scrape data from it and store it in a required format
    def crawl(self,soup,tribuneCheck=False):
        if tribuneCheck:
            for item in soup.find_all('item'):
                item = item.text.split('\n')
                for value in item:
                    if value == '':
                        item.pop(item.index(value))
                date = item[3]
                date = ((date.split(','))[1]).strip()
                date = date[:2]+date[3:6]
                if date==todayDate[:5]:
                    titles.append(item[0])
                    links.append(item[1])
                    pubDates.append(item[3])
                    guids.append(item[6])
                    descriptions.append(item[7])
                
        else:
            for item in soup.find_all('item'):
                item = item.text.split('\n')
                for value in item:
                    if value == '':
                        item.pop(item.index(value))
                date = item[2]
                date = ((date.split(','))[1]).strip()
                date = date[:2]+date[3:6]+date[7:11]
                if date==todayDate:
                    titles.append(item[0])
                    links.append(item[1])
                    pubDates.append(item[2])
                    guids.append(item[3])
                    descriptions.append(item[5])


if __name__=='__main__':
    #Getting Current Date
    today = datetime.datetime.today()
    daysToGoBack = 1
    flag = False
    todayDate = today.strftime('%d%b%Y')
    if (int(todayDate[:2])-daysToGoBack)<10:
        flag = True
    todayDate = str(int(todayDate[:2])-daysToGoBack)+todayDate[2:]
    if flag:
        todayDate = '0'+todayDate
    #Specifying pages for each news website
    geoNewsPages = 7
    theNewsPages = 12
    
    #Generating News Scraper's soup object and making scraper crawl over it 
    scraper = Scraper("crawlingLinks.csv")
    for i in range(len(scraper.crawlinglinks)):
        if i==0:
            for j in range(1,geoNewsPages+1):
                url = f"{scraper.crawlinglinks[i]}/{j}"
                page = requests.get(url)
                soup = BeautifulSoup(page.content,'html.parser')
                scraper.crawl(soup)
        elif i==1:
            for k in range(1,theNewsPages+1):
                url = f"{scraper.crawlinglinks[i]}/{k}"
                page = requests.get(url)
                soup = BeautifulSoup(page.content,'html.parser')
                scraper.crawl(soup)
        else:
            url = scraper.crawlinglinks[i]
            page = requests.get(url)
            soup = BeautifulSoup(page.content,'html.parser')
            scraper.crawl(soup,tribuneCheck=True)

    #Converting all the separate lists of entities to a single pandas dataframe
    final = pd.DataFrame({
        'Title' : titles,
        'Link' : links,
        'Publication Date' : pubDates,
        'GUID' : guids,
        'Description' : descriptions
        })

    #Saving the all the scraped data to the directory if it exits, creating it otherwise
    cwd = os.getcwd()
    path =  os.path.join(cwd,"NewsCSVFiles")
    filename = "AllNews"+todayDate
    if (os.path.exists("NewsCSVFiles")):
        final.to_csv(path+"\\"+filename+".csv",index=False)
    else:
        os.mkdir(path)
        final.to_csv(path+"\\"+filename+".csv",index=False)