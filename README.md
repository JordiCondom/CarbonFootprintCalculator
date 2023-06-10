# Carbon Footprint Calculator
This project develops a carbon footprint questionnaire, calculator, and tracking system using big data technologies taught
in the Big Data Technologies course at the University of
Trento. The questionnaire assesses carbon emissions across
various activities, while the calculator generates accurate
estimations. Real-time data tracking enables personalized
recommendations to reduce carbon footprints, and carbon
offsetting recommendations support environmental mitigation. The project offers a comprehensive solution for assessing, managing, and mitigating carbon footprints, applying big
data technologies to promote sustainability and eco-friendly
practices.

# **Execution**

As a first step, we have to set up the technologies with docker. In this case, worker refers to the ammount of worker nodes Citus uses for PostgreSQL, 2 by default. Important to notice ports 5432 and 6379 must be free of use before running Docker. Also, internet access is required as the javascript of the frontend imports some code from the internet. All of the required files for the following executions are in the webpage folder.
```
docker-compose -p citus up --scale worker=2
```
Install the required python dependencies:
```
pip install -r requirements.txt 
```
To run the website server locally, open a new shell and execute:
```
python3 ./app.py
```
The local server is now running at: http://127.0.0.1:5000 and you are ready to input and track your data. At this point you can (not required but recommended) upload some test users using (Required Docker running) and check their profiles (User descriptions available below):
```
pyhton3 ./load_user.py 
```

# Data Pipeline
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/datapipeline.png)

# Test Users descriptions

After loading the users, you can login using the username and the password (same username) to see some test data. These are the following:

## vegan:

- Data is each 2 months starting January first
- Follows a vegan diet.
- Wastes an average of 10-14% of their food.
- Prioritizes consuming local food.
- Does not use a car.
- Only uses city buses for 60-40 hours.
- Lives in a household of three people.
- The type of heating in their home is unknown.
- Recycles glass, plastic, paper, and aluminum.
- Has an average shopping profile.
- Opts for buying a refurbished phone in the last period.

## pescetarian:

- Data is each 2 months starting January first
- Follows a pescetarian diet.
- Wastes an average of 5-10% of their food.
- Prioritizes consuming local food.
- Does not use a car.
- Only uses city buses for 20-35 hours.
- No data regarding flights.
- Lives in a household of four people.
- Uses LPG as the heating type in their home.
- Recycles glass, plastic, paper, and aluminum.
- Has a low shopping profile.
- Opts for buying a refurbished phone in the last period.

## low_meat_eater:

- Data is each 2 months starting January first
- Follows a diet that includes some meat.
- Wastes an average of 7-20% of their food.
- Prioritizes consuming local food.
- Uses a plug-in hybrid electric car and spends 15-20 hours on car travel.
- Uses trains for 6 to 3 hours.
- No data regarding flights.
- Lives in a household of one person.
- The type of heating in their home is unknown.
- Does not recycle.
- Has a low shopping profile.
- Opts for buying a phone or laptop in different periods.

## heavy_consumer:

- Data is each 2 months starting January first
- Follows a diet that includes heavy meat consumption.
- Wastes an average of 10-15% of their food.
- Does not prioritize consuming local food.
- Uses a gasoline car and spends 40-60 hours on car travel.
- Uses trains for 2 to 5 hours.
- No data regarding flights.
- Lives in a household of one person.
- Uses gas methane as the heating type in their home.
- Does not recycle.
- Has a high shopping profile.
- Opts for buying a laptop in one of the periods.

## average_consumer:

- Data is each 2 months starting January first
- Follows a regular meat diet.
- Wastes an average of 5-10% of their food.
- Prioritizes consuming local food.
- Uses a diesel car and spends 5 hours on car travel.
- Also uses city buses, intercity buses, and trains, spending 10-15 hours on each mode of transportation.
- No data regarding flights.
- Lives in a household of three people.
- Uses gas methane as the heating type in their home.
- Recycles glass, plastic, paper, and aluminum.
- Has an average shopping profile.
- Opts for buying a phone in one of the periods.

## mixed_diet:

- Data is each 2 months starting January first
- Follows a regular meat or vegetarian diet.
- Wastes an average of 6-18% of their food.
- They sometimes consume local food but not always.
- Uses a diesel car and spends 3-10 hours on car travel.
- Also uses city buses, intercity buses, and trains, spending 7-13 hours on each mode of transportation.
- No data regarding flights.
- Lives in a household of three people.
- Uses gas methane as the heating type in their home.
- Recycles glass, plastic, paper, and aluminum.
- Has an average shopping profile.
- Opts for buying a phone in one of the periods.

## random:

- Data is each 2 months starting January first
- Follows a heavy meat diet.
- Wastes an average of 18-20% of their food.
- Prioritizes consuming local food.
- Uses an electric car and spends 25-30 hours on car travel.
- Uses city buses and trains sometimes.
- No data regarding flights.
- Lives in a household of three people.
- The type of heating in their home is unknown.
- Recycles glass, plastic, paper, and aluminum.
- Has an average shopping profile.
- Opts for buying a phone in one of the periods.

## average_consumer_plus_plane:

- Data is each 2 months starting January first
- Follows a regular meat diet.
- Wastes an average of 5-10% of their food.
- Prioritizes consuming local food.
- Uses a diesel car and spends 5 hours on car travel.
- Also uses city buses, intercity buses, and trains, spending 10-15 hours on each mode of transportation.
- Took a flight from LA to NY and back in business class.
- Lives in a household of three people.
- Uses gas methane as the heating type in their home.
- Recycles glass, plastic, paper, and aluminum.
- Has an average shopping profile.
- Opts for buying a phone in one of the periods.


# Conversion Factors for the Calculator
The following section highlights the conversion factors and choices adopted in the project. A “conversion factor”, in the context of a carbon footprint calculator, is the fundamental tool used to convert habits into kg of CO2e. The computation of those factors has been extracted from various sources and, when possible, double-checked to ensure scientific accuracy. The issues and limitations of those sources will be later discussed.

## Food section
### Diet
Following the factors by GoClimate Calculator[^1], we have based the categories and values for the users diet from a study by Scarborough et al (2014)[^2]:
	
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
Computing waste emissions was quite challenging as we had to take a long path to assess municipal waste weight[^8] and composition[^9] in Europe. In addition, we referred to how much kg CO2 a recycled and not recycled material imply[^13]. The conversion factors used are as follows:
| Material        | avg % in Municipal Waste (Europe) |
|-----------------|----------------------------------|
| Plastic         | 10.00%                           |
| Paper           | 30.00%                           |
| Glass           | 7.50%                            |
| Non Ferrous     | 5.00%                            |
| Ferrous Metals  | 2.00%                            | 


| Material  | GHG From New Production (kg CO2e/kg) | GHG From Producing Recycled Materials (kg CO2e/kg) |
|-----------|----------------------------------|------------------------------------------------|
| Aluminum  | 11.0                             | 0.4                                            |
| Glass     | 0.9                              | 0.5                                            |
| Plastic   | 2.1                              | 1.3                                            |
| Paper     | 1.1                              | 0.7                                            |



## Consumption
Last but not least, for the generic consumption emission assessment, we decided to focus on shopping profile[^11] and technological[^12] expenditure:
|          | High Shopping Profile | Average Shopping Profile | Low Shopping Profile |
|----------|-------|------------|----------------|
| kg CO2 per day       | 12.14  | 8.09      | 4.04         |

|            | kg CO2e | refurbished (=10%) |
|------------|---------|------------------|
| Smartphone | 70      | 7                |
| Laptop     | 300     | 30               |


## Tracking Data Plots and Questionnaire screenshot examples:
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Questionnaire.png)
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Screenshot%202023-06-10%20alle%2017.13.37.png)
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Screenshot%202023-06-10%20alle%2017.13.46.png)
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Screenshot%202023-06-10%20alle%2017.13.53.png)
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Screenshot%202023-06-10%20alle%2017.14.04.png)
![alt text](https://raw.githubusercontent.com/JordiCondom/CarbonFootprintCalculator/main/Images/Screenshot%202023-06-10%20alle%2017.14.16.png)






[^1]: Go Climate Methodology report https://drive.google.com/file/d/1x0GbM7LDahU07RghHfj6JysBmdDHUZBc/view

[^2]: Scarborough, P., Appleby, P.N., Mizdrak, A. et al. Dietary greenhouse gas emissions of meat-eaters, fish-eaters, vegetarians and vegans in the UK. Climatic Change 125, 179–192 (2014). https://link.springer.com/article/10.1007/s10584-014-1169-1

[^3]: J. Poore T. Nemecek ,Reducing food’s environmental impacts through producers and consumers.Science360,987-992(2018). doi:[10.1126/science.aaq0216](https://www.science.org/doi/10.1126/science.aaq0216)

[^4]: Our World in Data website, "Carbon footprint of travel per kilometer, 2018" https://ourworldindata.org/travel-carbon-footprint 

[^5]: [A. Elric “等価交換”](https://www.youtube.com/watch?v=8nm4chD_-Mg) 

[^6]: GoClimate API Reference https://api.goclimate.com/docs

[^7]: [Carbon Footprint calculator](https://www.carbonfootprint.com/calculator.aspx)

[^8]: Average Municipal waste in EU 2021 https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Municipal_waste_statistics

[^9]: Waste composition % in EU https://www.researchgate.net/publication/225979972_Separate_collection_and_biological_waste_treatment_in_the_European_Community

[^10]: [Plastic emissions (Paper - page 13)](https://www.eionet.europa.eu/etcs/etc-wmge/products/etc-wmge-reports/greenhouse-gas-emissions-and-natural-capital-implications-of-plastics-including-biobased-plastics/@@download/file/ETC_2.1.2.1._GHGEmissionsOfPlastics_FinalReport_v7.0_ED.pdf) – 
[Paper emissions (Website)](https://www.holmen.com/en/paper/sustainability/sustainability-stories/how-to-undrestand-carbon-footprints/) – 
[Glass emissions (Glass industry sector report - page 2)](https://climate.ec.europa.eu/system/files/2016-11/bm_study-glass_en.pdf) – 
[Aluminum emissions (Aluminum industry sector report - page 13)](https://climate.ec.europa.eu/system/files/2016-11/bm_study-aluminium_en.pdf) – 
[Steel emissions (Website)](https://www.sustainable-ships.org/stories/2022/carbon-footprint-steel)

[^11]: [GoClimate: Methodology behind the carbon footprint calculator](https://www.goclimate.com/blog/methodology-behind-the-carbon-footprint-calculator/)

[^12]: [Tech (Website)](https://www.goclimate.com/blog/the-carbon-footprint-of-shopping/) – 
[Tech refurbished (Website)](https://impakter.com/by-buying-your-smartphone-refurbished-rather-than-new-you-can-save-over-77kg-of-co2) 

[^13]: [Carbon Footprint: Recycling Compared to Not Recycling](https://8billiontrees.com/carbon-offsets-credits/carbon-footprint-recycling/)



