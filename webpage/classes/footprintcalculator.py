

from classes.airportFootprintManager import AirportFootprintManager


class footprintCalculator:
    def __init__(self, data):
        self.data = data
        self.number_of_days = self.data['number_of_days']

    def computeCarbonFootprint(self):
        diet = self.computeDietCarbonFootprint()
        transportation =  self.computeTransportationCarbonFootprint()
        housing = self.computeHousingCarbonFootprint()
        consumption = self.computeConsumptionCarbonFootprint()
        waste = self.computeWasteCarbonFootprint()
        unavoidable_footprint = 1240*(1/365)*(self.number_of_days)
        total = diet + transportation + housing + consumption + waste + unavoidable_footprint

        carbonFootprint = {
            'diet': diet,  
            'transportation': transportation,
            'housing': housing,
            'consumption': consumption,
            'waste': waste,
            'total': total 
        }

        return carbonFootprint
    
    def computeDietCarbonFootprint(self):
        diet = self.data['answerDiet']
        
        # kg/day
        diet_footprints = {
            'Vegan': 2.89,
            'Vegetarian': 3.81,
            'Pescetarian': 3.91,
            'Some_meat': 4.67,
            'Regular_meat': 5.63,
            'Heavy_meat': 7.19
        }
        
        value = diet_footprints.get(diet, 0)
        return value * self.number_of_days

    def computeTransportationCarbonFootprint(self):
        value = 0
        if self.data['answerCarType'] and self.data['answerCarDistance'] != '':
            value = value + self.computeCarCarbonFootprint()
        
        if self.data['answerBusDistance']:
            value = value + 0.105*int(self.data['answerBusDistance'])
        
        if self.data['answerTrainDistance']:
            value = value + 0.041*int(self.data['answerTrainDistance'])

        if self.data['origin_airports'] != ['']:
            value = value + self.computerPlaneCarbonFootprint()

        return value
    
    def computeCarCarbonFootprint(self):
        #g/km
        carType = self.data['answerCarType']
        carDistance = int(self.data['answerCarDistance'])

        car_type_footprints = {
            'Gasoline': 148,
            'Diesel': 146,
            'Plug-in Hybrid Electric':49,
            'Electric': 5,
            "I don't know": 148
        }

        value = car_type_footprints.get(carType, 0)
        return (value*carDistance)/1000

    def computerPlaneCarbonFootprint(self):
        origin_airports = self.data['origin_airports']
        destination_airports = self.data['destination_airports']
        cabin_classes = self.data['cabin_classes']
        round_trips = self.data['round_trips']
        value = 0

        for i in range(len(origin_airports)):
            current_origin_airport = origin_airports[i]
            current_destination_airport = destination_airports[i]
            current_cabin_class = cabin_classes[i]
            current_round_trip = round_trips[i] == "yes"

            current_footprint = AirportFootprintManager().compute_flight_footprint(current_origin_airport,
                                                                                   current_destination_airport,
                                                                                   current_cabin_class,
                                                                                   current_round_trip)
            
            if current_footprint:
                value = value + current_footprint

        return value




    def computeHousingCarbonFootprint(self):
        value = 0
        return value

    def computeConsumptionCarbonFootprint(self):

        current_shopping_profile = self.data['answerShoppingProfile']
        EU_shopping_average_footprint = 2955*(1/365) # kg/day
        shopping_footprint_factors = {
            'lowShoppingProfile': 0.5,
            'averageShoppingProfile': 1.0,
            'highShoppingProfile': 1.5
        }

        current_shopping_facotr = shopping_footprint_factors.get(current_shopping_profile, 0)
        shopping_footprint = (EU_shopping_average_footprint*current_shopping_facotr)*(self.number_of_days)


        current_electronics_buy = self.data['answerPhoneLaptop']
        electronics_footprint_factors = {
            'phoneAndLaptop': 70 + 300,
            'phone': 70,
            'Laptop': 300,
            'None': 0
        }

        shopping_footprint = shopping_footprint + electronics_footprint_factors.get(current_electronics_buy,0)


        return shopping_footprint


    def computeWasteCarbonFootprint(self):
        value = 0
        return value