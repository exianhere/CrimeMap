import os
import pandas as pd
import string
from unidecode import unidecode
import spacy
from IEDataScraper import IEDataScraper
from InformationExtractor import  InformationExtractor
from LoaderRetriever import LoaderRetriever
from DBApp.models import News,Crime_News,City,Casualties,Crime_Type,Extracted_Info,Ext_Crime,Ext_Casual



uni_crime_words = {
                "Assault": ["battery","assault","arrest","torture","beat","slap","remand","strike","hurt","punish","stab","amputate","violence","damage","attack"],
                "Theft":["robber","crime","larceny","embezzlement","shoplift","steal","burglar","fraud","money","thief","felony","loot","stealing","traffick","scam","misdemeanor"],
                "Drugs":["meth","cocaine","chars","hash","cannabis","drug","alcohol","pills","traffick","drink","beer","fizzy","liquor"],
                "Suicide":["drown","suicide","jump off","throw"],
                "Sexual Assault":["rape","sex","gang","prostitute","bisexual","harass"],
                "Homicide":["wound","kill","shoot","shooter","shot","death","burn","murder","manslaughter","assassinate","martyr","brutal","corpse",
                            "grenade","explode","torture","stab","fire"],
                "Kidnap":["kidnap","abduct","seize","ransom","hostage","smuggle","blackmail","hijack"],
              }

bi_gram_crime_words = {
                        "fire": ["set on fire","setting on fire","set on","setting on"],
                        "burn": ["stove burning"],
                        "child" : ["child marriage","child neglect","child porn","child pornography","child traffick","child trafficking","child abuse"],
                        "corporal" : ["corporal punishment","punishment","beating","mutilation","blinding","blind"],
                        "marriage": ["forced marriage","forced","holy quran","quran","early age marriage"],
                        "wani": ["vani","wani","sawara","forced marriage","minor"],
                        "brutal" : ["brutal beating","beating","beat","brutal punishment","punishment","punish"],
                        "honor": ["honor killing","honor kill","karo kari"]
                    }
                    

crime_word_keys = ["Assault","Theft","Drugs","Suicide","Sexual Assault","Homicide","Kidnap"]

stop_words = ['whence', 'here', 'show', 'were', 'why', 'n’t', 'the', 'whereupon', 'not', 'more', 'how', 'eight', 'indeed', 'i', 'only', 'via', 'nine',
              're', 'themselves', 'almost', 'to', 'already', 'front', 'least', 'becomes', 'thereby', 'doing', 'her', 'together', 'be', 'often', 'then',
              'quite', 'less', 'many', 'they', 'ourselves', 'take', 'its', 'yours', 'each', 'would', 'may', 'namely', 'do', 'whose', 'whether', 'side',
              'both', 'what', 'between', 'toward', 'our', 'whereby', "'m", 'formerly', 'myself', 'had', 'really', 'call', 'keep', "'re", 'hereupon', 
              'can', 'their', 'eleven', '’m', 'even', 'around', 'twenty', 'mostly', 'did', 'at', 'an', 'seems', 'serious', 'against', "n't", 'except', 
              'has', 'five', 'he', 'last', '‘ve', 'because', 'we', 'himself', 'yet', 'something', 'somehow', '‘m', 'towards', 'his', 'six', 'anywhere', 
              'us', '‘d', 'thru', 'thus', 'which', 'everything', 'become', 'herein', 'one', 'in', 'although', 'sometime', 'give', 'cannot', 'besides', 
              'across', 'noone', 'ever', 'that', 'over', 'among', 'during', 'however', 'when', 'sometimes', 'still', 'seemed', 'get', "'ve", 'him', 
              'with', 'part', 'beyond', 'everyone', 'same', 'this', 'latterly', 'no', 'regarding', 'elsewhere', 'others', 'moreover', 'else', 'back', 
              'alone', 'somewhere', 'are', 'will', 'beforehand', 'ten', 'very', 'most', 'three', 'former', '’re', 'otherwise', 'several', 'also', 
              'whatever', 'am', 'becoming', 'beside', '’s', 'nothing', 'some', 'since', 'thence', 'anyway', 'out', 'up', 'well', 'it', 'various', 
              'four', 'top', '‘s', 'than', 'under', 'might', 'could', 'by', 'too', 'and', 'whom', '‘ll', 'say', 'therefore', "'s", 'other', 'throughout', 
              'became', 'your', 'put', 'per', "'ll", 'fifteen', 'must', 'before', 'whenever', 'anyone', 'without', 'does', 'was', 'where', 'thereafter', 
              "'d", 'another', 'yourselves', 'n‘t', 'see', 'go', 'wherever', 'just', 'seeming', 'hence', 'full', 'whereafter', 'bottom', 'whole', 'own', 
              'empty', 'due', 'behind', 'while', 'onto', 'wherein', 'off', 'again', 'a', 'two', 'above', 'therein', 'sixty', 'those', 'whereas', 'using', 
              'latter', 'used', 'my', 'herself', 'hers', 'or', 'neither', 'forty', 'thereupon', 'now', 'after', 'yourself', 'whither', 'rather', 'once', 
              'from', 'until', 'anything', 'few', 'into', 'such', 'being', 'make', 'mine', 'please', 'along', 'hundred', 'should', 'below', 'third', 
              'unless', 'upon', 'perhaps', 'ours', 'but', 'never', 'whoever', 'fifty', 'any', 'all', 'nobody', 'there', 'have', 'anyhow', 'of', 'seem', 
              'down', 'is', 'every', '’ll', 'much', 'none', 'further', 'me', 'who', 'nevertheless', 'about', 'everywhere', 'name', 'enough', '’d', 'next', 
              'meanwhile', 'though', 'through', 'on', 'first', 'been', 'hereby', 'if', 'move', 'so', 'either', 'amongst', 'for', 'twelve', 'nor', 'she', 
              'always', 'these', 'as', '’ve', 'amount', '‘re', 'someone', 'afterwards', 'you', 'nowhere', 'itself', 'done', 'hereafter', 'within', 'made', 
              'ca', 'them']

class Classifier:

    currFileData = {}

    crimeNewsTitles = []
    crimeNewsLinks = []
    crimeNewsPubDates = []
    crimeNewsGuids = []
    crimeNewsDescriptions = []

    crimeNewsCity = []
    crimeNewsCasualities = []
    crimeNewsCategories = []

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def preprocessor(self,newsTitle):
        result = str(newsTitle)
        result = unidecode(result).replace("'",'')
        result = "".join([x for x in result if x not in string.punctuation])
        result = result.strip()
        result = result.split()
        return " ".join(result)

    def classify(self,newsTitle,ind):
        news = self.preprocessor(newsTitle)
        news = self.nlp(news)
        if (Classifier.currFileData['GUID'])[ind] not in Classifier.crimeNewsGuids:
            for category in crime_word_keys:    
                for word in news:
                    if word.lemma_ in uni_crime_words[category]:
                        
                        ieScraper = IEDataScraper((Classifier.currFileData['Link'])[ind])
                        print(news)
                        data = ieScraper.ScrapeContent()
                        doc = self.nlp(data)
                        
                        if self.confirmCrime(data,category):
                            ie = InformationExtractor()
                            extCasuality = ie.getCasualitySentence(data,uni_crime_words[category])
                            extCity= ie.extractCity(data) 
                            
                            if extCasuality and len(extCity):
                                
                                preExist,index = self.checkPreExisting(newsTitle)
                                if preExist==True and category in Classifier.crimeNewsCategories[index]:
                                    self.updateCasualityLists(extCasuality,index)
                                elif preExist==True and category not in Classifier.crimeNewsCategories[index]:
                                    self.updateCategoryLists(category,index)
                                elif preExist==False:
                                    extCasual = [extCasuality]
                                    categoryList = [category]
                                    self.prepareExportLists( (Classifier.currFileData['Title'])[ind], (Classifier.currFileData['Link'])[ind],
                                                            (Classifier.currFileData['Publication Date'])[ind], (Classifier.currFileData['GUID'])[ind],
                                                            (Classifier.currFileData['Description'])[ind],extCity[0],extCasual,categoryList)
                                break
                        
                                
                    if word.lemma_ in bi_gram_crime_words.keys():
                        ieScraper = IEDataScraper((Classifier.currFileData['Link'])[ind])
                        data = ieScraper.ScrapeContent()
                        doc = self.nlp(data)

                        if self.confirmBiWordCrime(data):
                            ie = InformationExtractor()
                            extCasuality = ie.getBiGramCasualitySentence(data,bi_gram_crime_words[word.lemma_])
                            extCity= ie.extractCity(data)
                            
                            if extCasuality and len(extCity):
                                cat = ""
                                if word.lemma_ == "fire" or word.lemma_=="burn" or word.lemma_=="brutal":
                                    cat = "Assault"
                                elif word.lemma_ == "child":
                                    cat = "Child Abuse"
                                elif word.lemma_ == "corporal":
                                    cat = "Corporal Crime"
                                elif word.lemma_ == "marriage" or word.lemma_ == "vani":
                                    cat = "Marriage Crime"
                                elif word.lemma_ == "honor":
                                    cat = "Homicide"

                                preExist,index = self.checkPreExisting(newsTitle)
                                if preExist and category in Classifier.crimeNewsCategories[index]:
                                    self.updateCasualityLists(extCasuality,index)
                                elif preExist and category not in Classifier.crimeNewsCategories[index]:
                                    self.updateCategoryLists(cat,index)
                                elif preExist==False:
                                    extCasual = [extCasuality]
                                    categoryList = [cat]
                                    self.prepareExportLists( (Classifier.currFileData['Title'])[ind], (Classifier.currFileData['Link'])[ind],
                                                            (Classifier.currFileData['Publication Date'])[ind], (Classifier.currFileData['GUID'])[ind],
                                                            (Classifier.currFileData['Description'])[ind],extCity[0],extCasual,categoryList)
                                
                            

    def checkPreExisting(self,news):
        if len(Classifier.crimeNewsTitles)>0:
            for title in Classifier.crimeNewsTitles:
                count = 0
                text1 = news.lower()
                text2 = title.lower()
                
                if ":" in text1:
                    text1 = text1.split(":")
                    text1.pop(0)
                    text1 = [x.strip() for x in text1]
                    text1 = "".join(text1)
                
                text1 = text1.split(" ")
                text1 = [word for word in text1 if not word in stop_words]
                text2 = text2.split(" ")

                if title.lower() == news.lower():
                    continue
                for word in text2:
                    if word in text1:
                        count+=1
                count = count/len(text1)
                if count>0.5:
                    return True,Classifier.crimeNewsTitles.index(title)
        return False,-1
    
    def prepareExportLists(self, title, link, pubDate, guid, description, cityInfo ,casualityList, category):
        Classifier.crimeNewsTitles.append(title)
        Classifier.crimeNewsLinks.append(link)
        Classifier.crimeNewsPubDates.append(pubDate)
        Classifier.crimeNewsGuids.append(guid)
        Classifier.crimeNewsDescriptions.append(description)
                            
        Classifier.crimeNewsCity.append(cityInfo)
        Classifier.crimeNewsCasualities.append(casualityList)
        Classifier.crimeNewsCategories.append(category)    

    def updateCasualityLists(self, casuality, index):
        Classifier.crimeNewsCasualities[index].append(casuality)        
    
    def updateCategoryLists(self, category, index):
        Classifier.crimeNewsCategories[index].append(category)        

    def confirmCrime(self,detailInfo,category):
        THRESHOLD = 2
        doc = self.nlp(detailInfo)
        count = 0
        for token in doc:
            if token.lemma_ in uni_crime_words[category]:
                count+=1
        if count>=THRESHOLD:
            return True
        return False

    def confirmBiWordCrime(self,detailInfo):
        THRESHOLD = 2
        doc = self.nlp(detailInfo)
        count = 0
        for key in bi_gram_crime_words.keys():
            for word in bi_gram_crime_words[key]:
                if word in doc.text:
                    count+=1
        if count>=THRESHOLD:
            return True
        return False  

                 
        
    def loadData(self,csv_urls):
        colList = ["Title","Publication Date","Link","Description","GUID"]
        i = 1
        for filename in os.listdir(csv_urls):
            print("Loading: ",i,":::",filename,"::: of ",len(os.listdir(csv_urls)))
            i+=1

            currFile = pd.read_csv(os.path.join(csv_urls,filename),usecols=colList)
            Classifier.currFileData = currFile.to_dict('list')
            j=0
            for currData in Classifier.currFileData['Title']: 
                self.classify(currData,Classifier.currFileData['Title'].index(currData))
            
            for i in range(len(Classifier.crimeNewsTitles)):
                print(i/len(Classifier.crimeNewsTitles),"%")
                loadCrimeNews = crimeNewsLoader.populateCrimeNews(Classifier.crimeNewsTitles[i],Classifier.crimeNewsLinks[i],Classifier.crimeNewsPubDates[i],
                                Classifier.crimeNewsGuids[i],Classifier.crimeNewsDescriptions[i])
                cityToExport = Classifier.crimeNewsCity[i]
                crimeNewsLoader.populateExtInfo(loadCrimeNews,cityToExport.city_name,cityToExport.city_lat,cityToExport.city_lng,
                                                Classifier.crimeNewsCasualities[i],Classifier.crimeNewsCategories[i])
            Classifier.crimeNewsTitles = []
            Classifier.crimeNewsLinks = []
            Classifier.crimeNewsPubDates = []
            Classifier.crimeNewsGuids = []
            Classifier.crimeNewsDescriptions = []

            Classifier.crimeNewsCity = []
            Classifier.crimeNewsCasualities = []
            Classifier.crimeNewsCategories = []        


if __name__=="__main__":
    folderName = "NewsCSVFiles"

    crimeNewsLoader = LoaderRetriever()

    #crimeNewsLoader.populateNews(folderName)
    
    #crimeNewsLoader.populateCities("city.csv")
    
    csv_urls = os.getcwd()+"\\"+folderName
    
    classifier = Classifier()
    classifier.loadData(csv_urls)
    print("Classification and Extraction Done")   

    #for i in range(len(crimeNewsTitles)):
    #    print(i/len(crimeNewsTitles),"%")
    #    loadCrimeNews = crimeNewsLoader.populateCrimeNews(crimeNewsTitles[i],crimeNewsLinks[i],crimeNewsPubDates[i],crimeNewsGuids[i],crimeNewsDescriptions[i])
    #    cityToExport = crimeNewsCity[i]
    #    crimeNewsLoader.populateExtInfo(loadCrimeNews,cityToExport.city_name,cityToExport.city_lat,cityToExport.city_lng,crimeNewsCasualities[i],crimeNewsCategories[i])