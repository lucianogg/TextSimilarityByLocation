import http
import http.client
import json

class Resource():
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.uri = None
        self.confidence = None
        self.detected_from = None

    @classmethod
    def resource_from_dbpedia_spotlight_annotation(cls, dbpedia_annotation_content):
        resource = cls()
        resource.uri = dbpedia_annotation_content['@URI']
        resource.confidence = dbpedia_annotation_content['@similarityScore']
        resource.detected_from = dbpedia_annotation_content['@surfaceForm']
        return resource

    def __str__(self):
        return "Resource has uri: " + self.detected_from + " with URI: " + self.uri + " with confidence: " + self.confidence

    def get_location(self):
        # if we already have them, retrieve:
        if self.latitude != None:
            return self.latitude, self.longitude

        # First try: check if it has geo:lat and geo:long or something in dbo:location that has geo:lat or geo:long
        query = """
            SELECT DISTINCT ?lat ?lon 
            WHERE {
                {
                    ?place geo:lat ?lat .
                    ?place geo:long ?lon .
                }
                UNION
                {
                    ?place dbo:location ?loc .
                    ?loc geo:lat ?lat .
                    ?loc geo:long ?lon .
                }
                
                FILTER (?place = <""" + self.uri + """>)
            }
            LIMIT 1
        """
        # The correct way to search for things without having to repeat names 3000 times!!!!!!
        # SELECT ?place ?id 
        #  WHERE {
        #      ?place ?whatever ?id.
        #      FILTER (?place = <http://dbpedia.org/resource/Paris>) 
        #  }
        # This was found at: https://stackoverflow.com/questions/27511519/sparql-query-to-get-the-information-of-a-specific-uri

        request = "https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org"
        conn = http.client.HTTPSConnection("dbpedia.org", 443)
        
        conn.request(
            "POST",
            url=request,
            body=query,
            headers={
                "Content-Type": "application/sparql-query",
                "Accept": "application/json"
            }
        )

        r1 = conn.getresponse()
        retrieved_text = r1.read()
        retrieved_json = json.loads(retrieved_text)
        conn.close()

        bindings = retrieved_json['results']['bindings']
        if len(bindings) > 0:
            # we found latitude and longitude
            lat_long = bindings[0]
            self.latitude = float(lat_long['lat']['value'])
            self.longitude = float(lat_long['lon']['value'])
        
        return self.latitude, self.longitude

    def get_latitude(self):
        if self.latitude != None:
            return self.latitude
        else:
            return self.get_location()[0]
    
    def get_longitude(self):
        if self.longitude != None:
            return self.longitude
        else:
            return self.get_location()[1]
