import csv

import pandas as pd
import requests


class AirportFootprintManager:
    def __init__(self):
        self.airports = self.read_airports_from_csv("./airports.csv")
        self.api_url = 'https://api.goclimate.com/v1/flight_footprint'
        self.api_key = '5b40202bc9109126deca9e32'


    def read_airports_from_csv(self,filename):
        df = pd.read_csv(filename, usecols=['code', 'name'])
        return df
    
    def get_airport_code_from_name(self,airport_name):
        matching_row = self.airports[self.airports['name'] == airport_name]
        if not matching_row.empty:
            airport_code = matching_row.iloc[0]['code']
            return airport_code
        return None
    
    def list_airport_names(self):
        airport_names = self.airports['name'].tolist()
        airport_names.sort()  # Sort the airport names in alphabetical order
        return airport_names

    def compute_flight_footprint(self, origin, destination, cabin_class, is_round_journey):
        # API endpoint URL
        params = {}

        origin_code = self.get_airport_code_from_name(origin)
        destination_code = self.get_airport_code_from_name(destination)

        if is_round_journey:
            params = {
                'segments[0][origin]': origin_code,
                'segments[0][destination]': destination_code,
                'segments[1][origin]': origin_code,
                'segments[1][destination]': destination_code,
                'cabin_class': cabin_class,
                'currencies[]': ['EUR']
            }
        else:
            params = {
                'segments[0][origin]': origin_code,
                'segments[0][destination]': destination_code,
                'cabin_class': cabin_class,
                'currencies[]': ['EUR']
            }

        # Make the GET request
        response = requests.get(self.api_url, params=params, auth=(self.api_key, ''))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Access the response data
            data = response.json()
            footprint = data['footprint']
            print("Successfully calculated carbon footprint of flight from " + origin + " to " + destination)

            return footprint
        else:
            # Request was unsuccessful, handle the error
            print('Error:', response.status_code)
            print('Response:', response.text)
            return None