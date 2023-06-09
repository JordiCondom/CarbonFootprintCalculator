# CarbonFootprintCalculator
Carbon Footprint Calculator for Big Data Technologies course of University of Trento

# Project description
Carbon Footprint Calculator: In this project, your task will involve developing a platform that **calculates individual carbon footprints** based on **user input** regarding lifestyle habits, transportation choices, dietary preferences, waste production and consumption patterns. The system should allow users to **track** and **compare** their annual emissions against **national averages** and **global targets**. Additionally, it could include features such as **personalised suggestions** on reducing greenhouse gas emissions and displaying potential offsets through purchases of renewable energy certificates or planted trees. 

# Conversion Factors
The following section highlights the conversion factors and choices adopted in the project. A “conversion factor”, in the context of a carbon footprint calculator, is the fundamental tool used to convert habits into kg of CO2e. The computation of those factors has been extracted from various sources and, when possible, double-checked to ensure scientific accuracy. The issues and limitations of those sources will be later discussed.

## Food section
### Diet
Following the decision made by GoClimate Calculator, we have based the categories and values for the users diet from a study by Scarborough et al (2014):
	
| **Diet**                    | **Kg CO2e/day** |
|-----------------------------|-----------------|
| Vegan                       | 2,89            |
| Vegetarian                  | 3,81            |
| Pescetarian                 | 3,91            |
| Some meat (< 50 g/day)      | 4,67            |
| Regular meat (50-100 g/day) | 5,63            |
| Heavy meat (> 100 g/day)    | 7,19            |


