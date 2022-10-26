import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','webApp.settings')
django.setup()
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from DBApp.models import News,Crime_News,City,Casualties,Crime_Type,Extracted_Info,Ext_Crime,Ext_Casual
import datetime




class LoaderRetriever:
    
    def populateCities(self,folderName):
        data = pd.read_csv(folderName)
        cityData = data.iloc[:].values
        for row in cityData:
            self.addCrimeCity(str(row[0]).lower(),row[1],row[2])
    
    def populateNews(self,folderName):
        csvFiles = os.getcwd()+"\\"+folderName
        colList = ["Title","Publication Date","Link","Description","GUID"]

        i=1
        for filename in os.listdir(csvFiles):
            currFile = pd.read_csv(os.path.join(csvFiles,filename),usecols=colList)
            currFileData = currFile.to_dict('list')

            print(i/len(os.listdir(csvFiles)),"%")
            i+=1

            j=1
            for entry in range(len(currFileData[colList[0]])):                
                newsTitle = (currFileData[colList[0]])[entry]
                newsPubDate = (currFileData[colList[1]])[entry]
                newsLink = (currFileData[colList[2]])[entry]
                newsDescription = (currFileData[colList[3]])[entry]
                newsGuid = (currFileData[colList[4]])[entry]
                news = News.objects.get_or_create(news_title=newsTitle,news_description=newsDescription,
                                                news_pubdate=newsPubDate,news_link=newsLink,news_guid=newsGuid)[0]


    def getLocations(self):
        cityLocations = City.objects.all()
        return cityLocations

    def addCasualty(self,crimecasualty):
        try:
            crimecasualty = Casualties.objects.get_or_create(casualty=crimecasualty)[0]
        except:
            crimecasualty = Casualties.objects.get_or_create(casualty="null")[0]
        crimecasualty.save()
        return crimecasualty

    def addCrimeCity(self,crimecity,citylongitude,citylatitude):
        try:
            crimecity = City.objects.get_or_create(city_name=crimecity,city_lng=citylongitude,city_lat=citylatitude)[0]
        except:
            crimecity = City.objects.get_or_create(city_name="null",city_lng=citylongitude,city_lat=citylatitude)[0]
        crimecity.save()
        return crimecity

    def addCategory(self,category):
        addedCategory = Crime_Type.objects.get_or_create(crime_type = category)[0]
        addedCategory.save()
        return addedCategory
    
    def populateExtInfo (self,crimeNewsId,crimeCity,cityLat,cityLong,casualities,categories):

        addCrimeCity = self.addCrimeCity(crimecity=crimeCity,citylatitude=cityLat,citylongitude=cityLong)
        extinfo=Extracted_Info.objects.get_or_create(crime_news_id=crimeNewsId,city_id=addCrimeCity)[0]
        extinfo.save()

        for c in range(len(casualities)):
            addCasualty=self.addCasualty(crimecasualty=casualities[c])
            extCasual=Ext_Casual.objects.get_or_create(ex_id=extinfo,casual_id=addCasualty)
        
        for ct in range(len(categories)):
            addCategory=self.addCategory(category=categories[ct])
            extcrime=Ext_Crime.objects.get_or_create(ex_id=extinfo,crime_type_id=addCategory)[0]
            extcrime.save()

    def getMonthInt(self,month):
        mon = 0
        if month=="Jan":   
            mon=1
        elif month=="Feb":   
            mon=2
        elif month=="Mar":   
            mon=3
        elif month=="Apr":   
            mon=4
        elif month=="May":   
            mon=5
        elif month=="Jun":   
            mon=6
        elif month=="Jul":   
            mon=7
        elif month=="Aug":   
            mon=8
        elif month=="Sep":   
            mon=9
        elif month=="Oct":   
            mon=10
        elif month=="Nov":   
            mon=11
        elif month=="Dec":   
            mon=12 
        return mon       
                
    def getWrtDate(self,startDate,endDate):
        crimeNews = Crime_News.objects.values_list('id', 'crime_pubdate')
        idList = []
        startDay = int(startDate[:2])
        startMonth = self.getMonthInt(str(startDate[2:-4]))
        startYear = int(startDate[-4:])
        endDay = int(endDate[:2])
        endMonth = self.getMonthInt(str(endDate[2:-4]))
        endYear = int(endDate[-4:])
        for news in crimeNews:
            date = (((news[1].split(','))[1]).strip()).split(" ")[:3]
            compMonth = self.getMonthInt(date[1])
            start = datetime.datetime(startYear,startMonth,startDay)
            end = datetime.datetime(endYear,endMonth,endDay)
            toCompare = datetime.datetime(int(date[2]),int(compMonth),int(date[0]))

            if toCompare>=start and toCompare<=end:
                idList.append(news[0])
        print(idList)
            


    def populateCrimeNews(self,newsTitle,newsLink,newsPubDate,newsGuid,newsDescription):
        #for i in range(len(newsTitle)):
        crimeNews = Crime_News.objects.get_or_create( crime_guid = newsGuid, crime_title = newsTitle, crime_link = newsLink,
                                                      crime_pubdate = newsPubDate, crime_description = newsDescription )[0]
        return crimeNews