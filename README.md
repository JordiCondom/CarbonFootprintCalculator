# CarbonFootprintCalculator
Carbon Footprint Calculator for Big Data Technologies course of University of Trento

# **How to run**

The project comes with a dockerfile 
```
docker-compose -p citus up --scale worker=2
```
At this point you should have interactive access to the docker container. To run the other stacks you need, open a new shell and:

```
python3 ./app.py
```

At this point you can upload some test user using 

```
pyhton3 ./load_user.py 
```
You can installing dependencies on your machine through

```
pip install -r requirements.txt 
```

# Project description
Carbon Footprint Calculator: In this project, your task will involve developing a platform that **calculates individual carbon footprints** based on **user input** regarding lifestyle habits, transportation choices, dietary preferences, waste production and consumption patterns. The system should allow users to **track** and **compare** their annual emissions against **national averages** and **global targets**. Additionally, it could include features such as **personalized suggestions** on reducing greenhouse gas emissions and displaying potential offsets through purchases of renewable energy certificates or planted trees. 

# Conversion Factors
The following section highlights the conversion factors and choices adopted in the project. A “conversion factor”, in the context of a carbon footprint calculator, is the fundamental tool used to convert habits into kg of CO2e. The computation of those factors has been extracted from various sources and, when possible, double-checked to ensure scientific accuracy. The issues and limitations of those sources will be later discussed.

## Food section
### Diet
Following the decision made by GoClimate Calculator[^1], we have based the categories and values for the users diet from a study by Scarborough et al (2014)[^2]:
	
| **Diet**                    | **kg CO2e/day** |
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
We accounted for transportation emissions referencing the website Ourworldindata[^4] for the public services like trains and buses, and private cars. To make the questionnaire user-friendly we decided to ask for the time spent in the mean of transportation instead of the actual kilometers traveled (_seriously… who could answer that?_). Unfortunately, as someone once said “To obtain, something of equal value must be lost”[^5] and to obtain an answerable question, here we made the assumption about the average driving speed, generalized for both city and countryside streets. 
For the cars, we accounted for the engine type following GoClimate report[^1] and determined an average speed of 60 km/h:

| **Engine**      | **kgCO2e/km**    | **kg/hours (60 km/h)** |
|-----------|----------|------------------|
| Gasoline  | 0.148    | 8.88             |
| Diesel    | 0.146    | 8.76             |
| Hybrid    | 0.049    | 2.94             |
| Electric  | 0.005    | 0.3              |
| No Car    | 0        | 0                |

While for public transportation we extracted an online emission calculator [^7] accounting for both city/countryside buses and normal/high speed trains velocities:
|             | CO2e kg/km | avg speed km/h | CO2e kg/h |
|-------------|------------|----------------|-----------|
| city bus    | 0.03       | 22             | 0.66      |
| intercity bus | 0.03       | 80             | 2.4       |
| high speed train | 0.04       | 200            | 8         |
| normal speed train | 0.04       | 100            | 4         |

Flights emissions are instead implemented thanks to the REST API of GoClimate lifestyle calculator[^6].

## Housing
To track the users' heating emissions in relation to their households, we used an online emission calculator [^7] for the exact conversion factors (kg CO2e/kWh) and an energy blog for the average kWh need of households. The specific conversions used are:

| Energy Type            | kg CO2e / kWh |
|------------------------|---------------|
| Electric               | 0.34          |
| Methane                | 0.18          |
| Fuel Oil               | 0.25          |
| Pellet                 | 0.0029        |
| LPG (Liquefied Petroleum Gas) | 0.21  |

While the average kWh consumption per Household size is:

| Household size | Mean kWh/day |
|-------------|--------------|
| 1           | 4            |
| 2           | 6            |
| 3           | 7.5          |
| 4           | 9            |
| 5+           | 10           |


## Waste
Computing waste emissions was quite challenging as we had to take a long path to assess municipal waste weight[^8] and composition[^9] in Europe. Then we referred to the specific material-industry sector reports to assess the impact of production/recycling/landfilling of the materials. When the data conversion was too complex (_preatty often_) we resorted to the production emissions, mainly because some materials produced more greenhouse gasses if they were recycled with respect to thrown in a landfill. Production emissions were instead a reliable indicator for all materials. The conversion factors used are as follows:
| Material        | avg % in Municipal Waste (Europe) | kgCO2e/kg[^10] |
|-----------------|----------------------------------|-----------|
| Plastic         | 10.00%                           | 2.7       |
| Paper           | 30.00%                           | 0.13      |
| Glass           | 7.50%                            | 0.6       |
| Non Ferrous     | 5.00%                            | 0.392     |
| Ferrous Metals  | 2.00%                            | 2.7       |


## Consumption
Last but not least, for the generic consumption emission assessment, we decided to focus on clothing[^11] and technological[^12] expenditure:
|          | kgCO2e | kg fibers per capita| kgCO2/kg fibers |
|----------|-------|------------|----------------|
| UE       | 1210  | 31.21      | 38.77          |

|            | kg CO2e | refurbished (=10%) |
|------------|---------|------------------|
| Smartphone | 70      | 7                |
| Laptop     | 300     | 30               |



## Methodological limitations 
As mentioned above, in the retrieval of the conversion factors we encountered a number of issues. The free carbon footprint calculators available online, even when methodology reports where indeed available, didn’t expose the conversion factors of the survey they offered. So in many cases we couldn’t use pre-made factors. Furthermore, the precise methodology behind the creation of any given conversion factor is nowhere to be found. The reason being that each material/fuel/machine used in any daily activity requires specific knowledge about its production, efficiency, life-cycle, and so on. So the factors developed in the context of this project are extremely generic and couldn’t follow a precise methodology.
As a result of the mentioned issues, the computations offered by the calculator are the best approximation we could reach, but an approximation nonetheless.


## Users description

After loading the users, you can login using the username also as a password to see some test data. These are the following:

vegan: 
Data is each 2 months starting January first 
They follow a vegan diet.
They waste an average of 10-14% of their food.
They prioritize consuming local food.
They do not use a car 
They only use city buses for 60-40 hours.
They live in a household of three people.
The type of heating in their home is unknown.
They recycle glass, plastic, paper, and aluminum.
They have an average shopping profile.
They opt for buying a refurbished phone in the last period

pescatarian: 
Data is each 2 months starting January first 
They follow a pescetarian diet.
They waste an average of 5-10% of their food.
They prioritize consuming local food.
They do not use a car 
They only use city buses for 20-35 hours.
No data regarding flights
They live in a household of four people.
They use LPG as the heating type in their home.
They recycle glass, plastic, paper, and aluminum.
They have a low shopping profile.
They opt for buying a refurbished phone in the last period.


low_meat_eater: 
Data is each 2 months starting January first 
They follow a diet that includes some meat.
They waste an average of 7-20% of their food.
They prioritize consuming local food.
They use a plug-in hybrid electric car and spend 15-20 hours on car travel.
They use trains 6 to 3 hours.
No data regarding flights
They live in a household of one person.
The type of heating in their home is unknown.
They do not recycle.
They have a low shopping profile.
They opt for buying a phone or laptop in different periods.


heavy_consumer: 
Data is each 2 months starting January first 
They follow a diet that includes heavy meat consumption.
They waste an average of 10-15% of their food.
They do not prioritize consuming local food.
They use a gasoline car and spend 40-60 hours on car travel.
They use trains for 2 to 5 hours.
No data regarding flights
They live in a household of one person.
They use gas methane as the heating type in their home.
They do not recycle.
They have a high shopping profile.
They opt for buying a laptop in one of the periods.

average_consumer:
Data is each 2 months starting January first 
They follow a regular meat diet.
They waste an average of 5-10% of their food.
They prioritize consuming local food.
They use a diesel car and spend 5 hours on car travel.
They also use city buses, intercity buses, and trains, spending 10-15 hours on each mode of transportation.
No data regarding flights
They live in a household of three people.
They use gas methane as the heating type in their home.
They recycle glass, plastic, paper, and aluminum.
They have an average shopping profile.
They opt for buying a phone in one of the periods.


mixed_diet:
Data is each 2 months starting January first 
They follow a regular meat or vegetarian diet.
They waste an average of 6-18% of their food.
They sometimes consume local food but not always.
They use a diesel car and spend 3-10 hours on car travel.
They also use city buses, intercity buses, and trains, spending 7-13 hours on each mode of transportation.
No data regarding flights
They live in a household of three people.
They use gas methane as the heating type in their home.
They recycle glass, plastic, paper, and aluminum.
They have an average shopping profile.
They opt for buying a phone in one of the periods.

random:
Data is each 2 months starting January first 
They follow a heavy meat diet.
They waste an average of 18-20% of their food.
They prioritize consuming local food.
They use an electric car and spend 25-30 hours on car travel.
They use city buses, and trains sometimes.
No data regarding flights
They live in a household of three people.
The type of heating in their home is unknown.
They grecycle glass, plastic, paper, and aluminum.
They have an average shopping profile.
They opt for buying a phone in one of the periods.


average_consumer_plus_plane
Data is each 2 months starting January first 
They follow a regular meat diet.
They waste an average of 5-10% of their food.
They prioritize consuming local food.
They use a diesel car and spend 5 hours on car travel.
They also use city buses, intercity buses, and trains, spending 10-15 hours on each mode of transportation.
They took a flight from LA to NY and back in business class
They live in a household of three people.
They use gas methane as the heating type in their home.
They recycle glass, plastic, paper, and aluminum.
They have an average shopping profile.
They opt for buying a phone in one of the periods.



## IMAGES

![alt text](https://imgur.com/a/qCtxGmT)






[^1]: Go Climate Methodology report https://drive.google.com/file/d/1x0GbM7LDahU07RghHfj6JysBmdDHUZBc/view

[^2]: Scarborough, P., Appleby, P.N., Mizdrak, A. et al. Dietary greenhouse gas emissions of meat-eaters, fish-eaters, vegetarians and vegans in the UK. Climatic Change 125, 179–192 (2014). https://link.springer.com/article/10.1007/s10584-014-1169-1

[^3]: J. Poore T. Nemecek ,Reducing food’s environmental impacts through producers and consumers.Science360,987-992(2018). doi:10.1126/science.aaq0216

[^4]: Our World in Data website, "Carbon footprint of travel per kilometer, 2018" https://ourworldindata.org/travel-carbon-footprint 

[^5]: [A. Elric “等価交換”] (https://www.youtube.com/watch?v=8nm4chD_-Mg)

[^6]: GoClimate API Reference https://api.goclimate.com/docs

[^7]: https://www.carbonfootprint.com/calculator.aspx

[^8]: Average Municipal waste in EU 2021 https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Municipal_waste_statistics

[^9]: Waste composition % in EUhttps://www.researchgate.net/publication/225979972_Separate_collection_and_biological_waste_treatment_in_the_European_Community

[^10]: [Plastic emissions (Paper - page 13)](https://www.eionet.europa.eu/etcs/etc-wmge/products/etc-wmge-reports/greenhouse-gas-emissions-and-natural-capital-implications-of-plastics-including-biobased-plastics/@@download/file/ETC_2.1.2.1._GHGEmissionsOfPlastics_FinalReport_v7.0_ED.pdf) – 
[Paper emissions (Website)](https://www.holmen.com/en/paper/sustainability/sustainability-stories/how-to-undrestand-carbon-footprints/) – 
[Glass emissions (Glass industry sector report - page 2)](https://climate.ec.europa.eu/system/files/2016-11/bm_study-glass_en.pdf) – 
[Aluminum emissions (Aluminum industry sector report - page 13)](https://climate.ec.europa.eu/system/files/2016-11/bm_study-aluminium_en.pdf) – 
[Steel emissions (Website)](https://www.sustainable-ships.org/stories/2022/carbon-footprint-steel)

[^11]: [Clothes emissions (Global apparel/footwear industries report - page 19)](https://quantis.com/wp-content/uploads/2018/03/measuringfashion_globalimpactstudy_full-report_quantis_cwf_2018a.pdf)

[^12]: [Tech (Website)](https://www.goclimate.com/blog/the-carbon-footprint-of-shopping/) – 
[Tech refurbished (Website)](https://impakter.com/by-buying-your-smartphone-refurbished-rather-than-new-you-can-save-over-77kg-of-co2) 



