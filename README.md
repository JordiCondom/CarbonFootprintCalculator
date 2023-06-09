# CarbonFootprintCalculator
Carbon Footprint Calculator for Big Data Technologies course of University of Trento

# Project description
Carbon Footprint Calculator: In this project, your task will involve developing a platform that **calculates individual carbon footprints** based on **user input** regarding lifestyle habits, transportation choices, dietary preferences, waste production and consumption patterns. The system should allow users to **track** and **compare** their annual emissions against **national averages** and **global targets**. Additionally, it could include features such as **personalised suggestions** on reducing greenhouse gas emissions and displaying potential offsets through purchases of renewable energy certificates or planted trees. 

# Conversion Factors
The following section highlights the conversion factors and choices adopted in the project. A “conversion factor”, in the context of a carbon footprint calculator, is the fundamental tool used to convert habits into kg of CO2e. The computation of those factors has been extracted from various sources and, when possible, double-checked to ensure scientific accuracy. The issues and limitations of those sources will be later discussed.

## Food section
### Diet
Following the decision made by GoClimate Calculator[^1], we have based the categories and values for the users diet from a study by Scarborough et al (2014)[^2]:
	
| **Diet**                    | **Kg CO2e/day** |
|-----------------------------|-----------------|
| Vegan                       | 2,89            |
| Vegetarian                  | 3,81            |
| Pescetarian                 | 3,91            |
| Some meat (< 50 g/day)      | 4,67            |
| Regular meat (50-100 g/day) | 5,63            |
| Heavy meat (> 100 g/day)    | 7,19            |

### Food waste
To account for food waste emissions, we chose to increase dietary emissions by the amount of food that was wasted. A 10% waste raises the user's diet-specific emissions proportionately. We chose to focus on the production side of food waste because the literature on the subject emphasizes the emissions of organic waste as a composition of gardening residuals in landfills rather than compost.

### Local food
Buying local food products, often from the city street markets, essentially means to avoid two aspects of the retail industry: transportation and packaging. In the literature[^3] it is said that:
> [...] the sum of emissions from packaging, transport, and retail contributes just 1 to 9%.

So we decided to reduce the user’s emissions by an average of 5% if they consistently buy local products.

## Transportation
We accounted for transportation emissions referencing the website Ourworldindata[^4] for the public services like trains and buses, and private cars. Flights emissions are instead implemented thanks to the REST API of GoClimate lifestyle calculator[^5].

## Housing

## Consumption

## Methodological limitations 
As mentioned above, in the retrieval of the conversion factors we encountered a number of issues. The free carbon footprint calculators available online, even when methodology reports where indeed available, didn’t expose the conversion factors of the survey they offered. So in many cases we couldn’t use pre-made factors. Furthermore, the precise methodology behind the creation of any given conversion factor is nowhere to be found. The reason being that each material/fuel/machine used in any daily activity requires specific knowledge about its production, efficiency, life-cycle, and so on. So the factors developed in the context of this project are extremely generic and couldn’t follow a precise methodology.
As a result of the mentioned issues, the computations offered by the calculator are the best approximation we could reach, but an approximation nonetheless.








[^1]: Go Climate Methodology report https://drive.google.com/file/d/1x0GbM7LDahU07RghHfj6JysBmdDHUZBc/view

[^2]: Scarborough, P., Appleby, P.N., Mizdrak, A. et al. Dietary greenhouse gas emissions of meat-eaters, fish-eaters, vegetarians and vegans in the UK. Climatic Change 125, 179–192 (2014). https://link.springer.com/article/10.1007/s10584-014-1169-1

[^3]: J. Poore T. Nemecek ,Reducing food’s environmental impacts through producers and consumers.Science360,987-992(2018). doi:10.1126/science.aaq0216

[^4]: Our World in Data website, "Carbon footprint of travel per kilometer, 2018" https://ourworldindata.org/travel-carbon-footprint 

[^5]: GoClimate API Reference https://api.goclimate.com/docs





