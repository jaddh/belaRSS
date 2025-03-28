import pandas as pd
import os
import requests
import json
import re
import sqlite3
from dotenv import load_dotenv

def google_location(name):
    load_dotenv()
    call = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
        str(name) + "&key={}".format(os.getenv("GOOGLE_GEOLOCATE_API_KEY")) + "&region=sy"
    response = requests.get(call)
    if response.status_code == 200:
        try:
            response = response.json()
            if response:
                # get the geometry
                geometry = response["results"][0]["geometry"]["location"]
                # add the geometry to the locations json
                point = "POINT (" + str(geometry["lng"]) + \
                    " " + str(geometry["lat"]) + ")"
                data = {"WKT": point,
                        "LOCATION_API": "geonames"}
                return data
        except:
            return None

def geonames_location(name):
    # use jadious2 or jadious or jadious 3
    call = "http://api.geonames.org/searchJSON?q={}&maxRows=1&username=jadious3".format(
        name)
    response = requests.get(call)
    if response.status_code == 200:
        print(response.json())
        response = response.json()
        if response:
            # get the geometry
            if response["geonames"] == []:
                point = "POINT EMPTY"
            else:
                geometry = response["geonames"][0]
                point = "POINT (" + str(geometry["lng"]) + \
                        " " + str(geometry["lat"]) + ")"
            georeference.locations[name] = point
            data = {"WKT": point,
                    "LOCATION_API": "geonames"}
            return data

def osm_location(name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        # Replace with your app name and contact info
        'User-Agent': 'MyAppName/1.0 (contact@example.com)',
        # Optional: Replace with your app's website
        'Referer': 'http://www.yourappwebsite.com'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        response = response.json()
        if response:
            # get the geometry
            if response == []:
                georeference.locations[name] = ""
            else:
                geometry = response[0]
                point = "POINT (" + str(geometry["lon"]) + \
                    " " + str(geometry["lat"]) + ")"
                georeference.locations[name] = point
                # add the geometry to the locations json
                if response != []:
                    data = {"WKT": "POINT (" + str(geometry["lon"]) + " " + str(geometry["lat"]) + ")",
                            "LOCATION_API": "osm"}
                    print(data)
                return data

class Geolocate():
    
    def __init__(self, cursor):
        self.cursor = cursor
        self.existing_locations = [row[0] for row in self.cursor.execute("select label from locations").fetchall()]    
    
    def geolocate(self, locations):
        print("getting locations")
        for location in locations: 
            if not location in self.existing_locations: 
                print(location)
                geometry = google_location(location)
                print(geometry)
                if geometry:
                    self.cursor.execute("insert into locations(label, geometry, location_api) values('{}','{}','{}')".format(str(location), str(geometry["WKT"]), str(geometry["LOCATION_API"])))
                self.existing_locations.append(location)
