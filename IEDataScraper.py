import requests
from bs4 import BeautifulSoup

class IEDataScraper:
    
    newssites = ['geo','thenews','https://tribune']

    def __init__(self,url):
        page = requests.get(url)
        self.soup = BeautifulSoup(page.content,'html.parser')
        self.website = -1
        urlcheck = url.split('.')
        for site in IEDataScraper.newssites:
            if site in urlcheck:
                self.website = IEDataScraper.newssites.index(site)


    def ScrapeContent(self):
        classval = ""
        tagval = ""
        if self.website == 0:
            classval = "content-area"
            tagval = "div"
        elif self.website == 1:
            classval = "story-detail"
            tagval = "div"
        elif self.website == 2:
            classval = "story-text"
            tagval = "span"
        
        content = self.soup.find(tagval,{"class":classval})
        children = content.findChildren( 'p', recursive = 'False' )
        text = ""
        for child in children:
            text += child.text
        text = text.strip()
        return text


