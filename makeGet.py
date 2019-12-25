import requests
import urllib.parse
import json

text = "First documented in the 13th century, Berlin was the capital of the Kingdom of Prussia (1701–1918), the German Empire (1871–1918), the Weimar Republic (1919–33) and the Third Reich (1933–45). Berlin in the 1920s was the third largest municipality in the world. After World War II, the city became divided into East Berlin -- the capital of East Germany -- and West Berlin, a West German exclave surrounded by the Berlin Wall from 1961–89. Following German reunification in 1990, the city regained its status as the capital of Germany, hosting 147 foreign embassies." # Texto que se va a introducir  //  Posteriormente habrá que introducir un fichero de texto en vez de introducir un string

textParsed = urllib.parse.quote(text)  #  Parseado de texto normal de string a url

language = "en" # German --> de // Portuguese --> pt    ////// Lenguaje que se va a utilizar en la API

response = requests.get("https://api.dbpedia-spotlight.org/" + language + "/annotate?text=" + textParsed,headers={"accept": "application/json"})  #  Ejecución del GET

data = response.json()  #  Parseado del texto a diccionario de Json

print(data) # Diccionario Json con los datos de retorno de la API
