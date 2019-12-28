import http
import http.client
import json
import lib.resource as resource

import urllib.parse


import sqlite3
from sqlite3 import Error

from sklearn.cluster import DBSCAN
import numpy as np
from scipy import stats

class Text():
    def __init__(self):
        self.raw_text = None
        self.locations = []
        self.latitude = None
        self.longitude = None

    @classmethod
    def text_from_string(cls, string):
        text = cls()
        text.raw_text = string
        return text

    def get_locations(self):
        processed_text = urllib.parse.quote(self.raw_text)
        # -----transform text into something like this: -------- 
        # processed_text = "First+documented+in+the+13th+century%2C+Berlin+was+the+capital+of+the+Kingdom+of+Prussia+(1701%E2%80%931918)%2C+the+German+Empire+(1871%E2%80%931918)%2C+the+Weimar+Republic+(1919%E2%80%9333)+and+the+Third+Reich+(1933%E2%80%9345).+Berlin+in+the+1920s+was+the+third+largest+municipality+in+the+world.+After+World+War+II%2C+the+city+became+divided+into+East+Berlin+--+the+capital+of+East+Germany+--+and+West+Berlin%2C+a+West+German+exclave+surrounded+by+the+Berlin+Wall+from+1961%E2%80%9389.+Following+German+reunification+in+1990%2C+the+city+regained+its+status+as+the+capital+of+Germany%2C+hosting+147+foreign+embassies."

        confidence_threshold = 0.8

        query = "/en/annotate?text=" + processed_text + "&confidence=" + str(confidence_threshold) + "&support=0&spotter=Default&disambiguator=Default&policy=whitelist&types=&sparql="

        conn = http.client.HTTPSConnection("api.dbpedia-spotlight.org", 443)
        conn.request('GET', query, headers={
            'Accept': 'application/json'
        })
        r1 = conn.getresponse()
        retrieved_text = r1.read()
        retrieved_json = json.loads(retrieved_text)
        conn.close()

        # print(json.dumps(retrieved_json, indent=4))

        resources_detected = [resource.Resource.resource_from_dbpedia_spotlight_annotation(res) for res in retrieved_json['Resources']]
        self.resources = resources_detected

        locations_detected = list(filter(lambda x: x[0] is not None, [res.get_location() for res in resources_detected]))
        self.locations = locations_detected
        # print(locations_detected)
        return locations_detected


    def get_main_location(self):
        # Do the clustering stuff to get the "predominant location"
        if self.locations == None:
            self.get_locations()
        
        db = DBSCAN(eps=0.05, min_samples=1).fit(self.locations)

        predominant_cluster = stats.mode(db.labels_)[0][0]
        entities_of_cluster = db.components_[db.labels_ == predominant_cluster]
        mean_predominant_location = np.mean(entities_of_cluster, axis=0)

        self.latitude = mean_predominant_location[0]
        self.longitude = mean_predominant_location[1]
        return self.latitude, self.longitude


    def export_data(self, con):
        cursorObj = con.cursor()
        if self.longitude is None or self.latitude is None:
            self.get_main_location()
        cursorObj.execute("INSERT INTO locations(texts, latitude, longitude) VALUES('%s', %f, %f)"%(self.raw_text, self.latitude, self.longitude))
        con.commit()
    
    def get_nearby_texts(self, con):

        cursorObj = con.cursor()

        tamLatitude = 10
        tamLongitude = 10

        rangeLatitudeMax = self.latitude + tamLatitude
        rangeLatitudeMin = self.latitude - tamLatitude

        rangeLongitudeMax = self.longitude + tamLongitude
        rangeLongitudeMin = self.longitude - tamLongitude

        cursorObj.execute("SELECT * FROM locations WHERE latitude BETWEEN %f AND %f AND longitude BETWEEN %f AND %f ORDER BY POW((latitude - %f),2) + POW((longitude - %f),2) LIMIT 10"%(rangeLatitudeMin, rangeLatitudeMax, rangeLongitudeMin, rangeLongitudeMax, self.latitude, self.longitude))


    

