from classes.airportFootprintManager import AirportFootprintManager


class footprintCalculator:
    def __init__(self, data):
        self.data = data
        self.number_of_days = self.data['number_of_days']
        self.shopping_profile = 0
        self.refurbished = 0
        self.plastic = 0
        self.glass = 0
        self.paper = 0
        self.aluminium = 0

    def computeCarbonFootprint(self):
        diet = self.computeDietCarbonFootprint()
        transportation =  self.computeTransportationCarbonFootprint()
        housing = self.computeHousingCarbonFootprint()
        consumption = self.computeConsumptionCarbonFootprint()
        waste = self.computeWasteCarbonFootprint()
        total = diet + transportation + housing + consumption + waste

        car = self.computeCarCarbonFootprint()
        plane = self.computerPlaneCarbonFootprint()
        bustrain = self.computeBusTrainCarbonFootprint()

        carbonFootprint = {
            'start_date': self.data['start_date'],
            'end_date': self.data['end_date'],
            'diet': diet,  
            'transportation': transportation,
            'car': car,
            'bustrain': bustrain,
            'plane': plane,
            'housing': housing,
            'consumption': consumption,
            'shopping_profile': self.shopping_profile,
            'refurbished': self.refurbished,
            'waste': waste,
            'plastic': self.plastic,
            'glass': self.glass,
            'paper': self.paper,
            'aluminium': self.aluminium,
            'number_of_days': self.number_of_days,
            'average_per_day': total/self.number_of_days,
            'total': total
        }

        return carbonFootprint
    
    def computeDietCarbonFootprint(self):
        diet = self.data['answerDiet']
        eatLocal = self.data['answerLocalFood']
        foodWastePercentage = int(self.data['answerWasteFoodPercentage'])
        
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

        #If you eat local it decreases 5%
        if eatLocal == "yes":
            value = value - (5/100)*value

        # If you waste food, add the percentage of food you waste to the already existing carbon footprint
        value = value + (foodWastePercentage/100)*value

        return value * self.number_of_days

    def computeTransportationCarbonFootprint(self):
        value = 0
        
        value = value + self.computeCarCarbonFootprint()
        value = value + self.computeBusTrainCarbonFootprint()
        value = value + self.computerPlaneCarbonFootprint()

        return value

    def computeCarCarbonFootprint(self):
        value = 0
        if self.data['answerCarType'] and self.data['answerCarTime'] != '':
            carType = self.data['answerCarType']
            carTime = int(self.data['answerCarTime'])
            
            #kgCo2/km
            car_type_footprints = {
                'Gasoline': 0.148,
                'Diesel': 0.146,
                'Plug-in Hybrid Electric':0.049,
                'Electric': 0.005,
                "I don't know": 0.148
            }

            value = car_type_footprints.get(carType, 0)
            # 55 km/h on average
            return value*carTime*55
        
        return value

    def computeBusTrainCarbonFootprint(self):
        value = 0

        if self.data['answerCityBusTime']:
            # 0.03kgCo2/km , 22 km/h average
            value = value + 0.03*22*int(self.data['answerCityBusTime'])
        
        if self.data['answerInterCityBusTime']:
            # 0.03kgCo2/km , 80 km/h average
            value = value + 0.03*80*int(self.data['answerInterCityBusTime'])

        if self.data['answerTrainTime']:
            # 0.041kgCo2/km, 100 km/h average
            value = value + 0.041*100*int(self.data['answerTrainTime'])

        return value

    def computerPlaneCarbonFootprint(self):
        value = 0
        if self.data['origin_airports'] != ['']:
            origin_airports = self.data['origin_airports']
            destination_airports = self.data['destination_airports']
            cabin_classes = self.data['cabin_classes']
            round_trips = self.data['round_trips']
            

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
        howmanypeople = self.data['answerHowManyPeople']
        heatingType = self.data['anwerHeatingType']

        # Kwh_per_day
        number_of_people_Kwh_per_day = {
            '1': 4,
            '2': 6,
            '3': 7.5,
            '4': 9,
            '5more': 10
        }
        # kgCo2/KwH
        heating_type_footprints = {
            'electric': 0.34,
            'gas_methane': 0.18,
            'heating_oil': 0.25,
            'pellet': 0.0029,
            'lpg': 0.21,
            'notKnow': 0.18, # most common, gas
        }

        value = number_of_people_Kwh_per_day.get(howmanypeople, 0)*heating_type_footprints.get(heatingType, 0)
        return value*self.number_of_days

    def computeConsumptionCarbonFootprint(self):

        current_shopping_profile = self.data['answerShoppingProfile']
        EU_shopping_average_footprint = 2955*(1/365) # kg/day
        shopping_footprint_factors = {
            'lowShoppingProfile': 0.5,
            'averageShoppingProfile': 1.0,
            'highShoppingProfile': 1.5
        }

        if current_shopping_profile == 'lowShoppingProfile':
            self.shopping_profile = -1
        elif current_shopping_profile == 'averageShoppingProfile':
            self.shopping_profile = 0
        else: 
            self.shopping_profile = 1

        current_shopping_facotr = shopping_footprint_factors.get(current_shopping_profile, 0)
        shopping_footprint = (EU_shopping_average_footprint*current_shopping_facotr)*(self.number_of_days)

        if self.data['answerPhoneLaptop']:
            current_electronics_buy = self.data['answerPhoneLaptop']
            electronics_footprint_factors = {
                'phone': 70,
                'refurbishedphone': 7,
                'laptop': 300,
                'refurbhisedLaptop': 30
            }

            if ('phone' in current_electronics_buy) or ('laptop' in current_electronics_buy):
                self.refurbished = 1
            else:
                self.refurbished = -1

            for product in current_electronics_buy:
                shopping_footprint = shopping_footprint + electronics_footprint_factors.get(product,0)


        return shopping_footprint

    def computeWasteCarbonFootprint(self):
        value = 0
        waste_vector = self.data['anwerWasteMaterials']
        # Average kg waste generation per inhabitant in eu per day 
        average_kg_waste_generation_per_day= {
            'Plastic': (34.6)/365,
            'Glass': (33.9)/365,
            'Paper': (72.9)/365,
            'Aluminium': (26.5)/365
        }

        if 'Plastic' in waste_vector:
            self.plastic = 1
        if 'Glass' in waste_vector:
            self.glass = 1
        if 'Paper' in waste_vector:
            self.paper = 1
        if 'Aluminium' in waste_vector:
            self.aluminium = 1

        # kgCo2/kg material
        GHG_of_materials_not_recicled = {
            'Plastic': 2.1,
            'Glass': 0.9,
            'Paper': 1.1,
            'Aluminium': 11.0
        }

        # kgCo2/kg material
        GHG_of_materials_recicled = {
            'Plastic': 1.3,
            'Glass': 0.5,
            'Paper': 0.7,
            'Aluminium': 0.4
        }

        for material in average_kg_waste_generation_per_day:
            if material in waste_vector: #recycled
                value = value + GHG_of_materials_recicled[material]*average_kg_waste_generation_per_day[material]
            else: #not recycled
                value = value + GHG_of_materials_not_recicled[material]*average_kg_waste_generation_per_day[material]

        return value*self.number_of_days
    