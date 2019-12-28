import http
import http.client
import json
import lib.resource as resource
import lib.text as text

import urllib.parse

from sql_lite_process import sql_connection

con = sql_connection()

with open('texts.txt', 'r') as file:
    for line in file:
        if len(line) < 5:
            continue
        else:
            text_to_process = text.Text.text_from_string(line)
            locations = text_to_process.get_locations()
            if len(locations) == 0:
                continue
            text_to_process.export_data(con)

con.close()