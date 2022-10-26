import spacy
from LoaderRetriever import LoaderRetriever
from unidecode import unidecode
import string

class InformationExtractor:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.load = LoaderRetriever()

    def extractCity(self,detailInfo):
        locations = []

        doc = self.nlp(detailInfo)
        locs = self.load.getLocations()

        for l in locs:
            for ent in doc.ents:
                if str(ent.text).lower() == l.city_name:
                    locations.append(l)

        return locations
    
    def getCasualitySentence(self,detailInfo,crime_words):
        detailInfo = unidecode(detailInfo).replace("'",'')
        detailInfo = detailInfo.strip()
        sentences = detailInfo.split('.')
        count = 0
        for sent in sentences:
            if ":" in sent:
                sent = sent.split(":")
                sent.pop(0)
                sent = [x.strip() for x in sent]
                sent = "".join(sent)

            doc = self.nlp(sent)
            for word in doc:
                if count==1:
                    continue
                if (word.lemma_ in crime_words) and word.pos_=="VERB":
                    count+=1
                    sent = "".join([x for x in sent if x not in string.punctuation])
                    return sent
        return ""
    
    def getBiGramCasualitySentence(self,detailInfo,crime_words):
        detailInfo = unidecode(detailInfo).replace("'",'')
        detailInfo = detailInfo.strip()
        sentences = detailInfo.split('.')
        count = 0
        for sent in sentences:
            if ":" in sent:
                sent = sent.split(":")
                sent.pop(0)
                sent = [x.strip() for x in sent]
                sent = "".join(sent)

            doc = self.nlp(sent)
            for word in crime_words:
                if count==1:
                    continue
                if (word in doc.text):# and word.pos_=="VERB":
                    count+=1
                    sent = "".join([x for x in sent if x not in string.punctuation])
                    return sent
        return ""