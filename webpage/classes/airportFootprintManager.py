import pandas as pd
import requests


class AirportFootprintManager:
    def __init__(self):
        self.airports = self.read_airports_from_csv("./airports.csv")
        self.api_url = 'https://api.goclimate.com/v1/flight_footprint'
        self.api_key = '5b40202bc9109126deca9e32'

    # Read airport data from a CSV file and return as a DataFrame
    def read_airports_from_csv(self,filename):
        df = pd.read_csv(filename, usecols=['code', 'name'])
        return df

    # Find the airport code for a given airport name
    def get_airport_code_from_name(self,airport_name):
        matching_row = self.airports[self.airports['name'] == airport_name]
        if not matching_row.empty:
            airport_code = matching_row.iloc[0]['code']
            return airport_code
        return None

    #Sort the airport names in alphabetical order
    def list_airport_names(self):
        airport_names = self.airports['name'].tolist()
        airport_names.sort()
        return airport_names

    # Calculate the carbon footprint of a flight using the GoClimate API
    def compute_flight_footprint(self, origin, destination, cabin_class, is_round_journey):
        params = {}             # Initialize the request parameters

        # Get the airport code for the origin and destination airport
        origin_code = self.get_airport_code_from_name(origin)
        destination_code = self.get_airport_code_from_name(destination)

        # Set parameters for round trip flight
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
            # Set parameters for one-way flight
            params = {
                'segments[0][origin]': origin_code,
                'segments[0][destination]': destination_code,
                'cabin_class': cabin_class,
                'currencies[]': ['EUR']
            }

        # Make the GET request for carbon footprint of the given flight
        response = requests.get(self.api_url, params=params, auth=(self.api_key, ''))

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse and extract carbon emission from the response data
            data = response.json()
            footprint = data['footprint']
            print("Successfully calculated carbon footprint of flight from " + origin + " to " + destination)

            return footprint
        else:
            # Request was unsuccessful: handle the error
            print('Error:', response.status_code)
            print('Response:', response.text)
            return None