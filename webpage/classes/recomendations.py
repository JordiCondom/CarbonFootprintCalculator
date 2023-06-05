def recomendations(dataframe):
    res = []
# DIET
    if (dataframe['diet'] > 4.6)/dataframe['number_of_days']:
        temp = "With a little change in your diet you can drastically lower your carbon footprint, if you decide to reduce your consumption of meat to just one steak (350g) instead of two each week you can save 35% with respect to eating 2!"
        reduction = 0.35
    else:
        temp = "Your diet doesn't  produce as much CO2 as the one of a frequent meat eater. You're definitely doing your part, and if you want to go Vegan you should know that your emission with respect to the Vegetarian would drop by 24%. If you are already vegan, but you are reading this suggestion, this means that you waste more than 30% of your food, so please keep on reading for some suggestions on that!"
        reduction = 0.24
    res.append(tuple(temp, reduction))

# TRANSPORTATION
    if dataframe['car'] > 2 * dataframe['bustrain']:    # Private to Public transport
        temp = "Taking a train can save you up to four times the money you would spend driving your own car, and for medium-length distances you would cut your emissions by ~80% (LINK). Regular use of your personal car will necessitate maintenance costs as well as various extra charges such as parking fees, pollution violations, and speeding fines. By taking public transportation, you will be able to save all of the money that would otherwise be spent on expenses associated with driving a personal vehicle. So it seems counterintuitive, but you should consider taking public transportation even if you possess a car! We often think that we have to use the car at all costs, given the huge investment we did buying it… but to really save money we can simply decide to not use it for some of our trips. If you want to know more about this topic, discover more benefits of public transport here (LINK)"
        reduction = 0.8
    elif dataframe['car'] > dataframe['bustrain']:      # Switch Car
        temp = "Switching to an electric vehicle can have a huge environmental benefit. Electric vehicles have no exhaust emissions, lowering greenhouse gas emissions and increasing air quality. Even with energy generation, according to research by the European Energy Agency, driving an electric car emits 96 % fewer carbon emissions than doing so in a gasoline or diesel vehicle. They are also more energy-efficient, converting a higher percentage of grid energy to wheel power, resulting in lower energy use and reliance on fossil fuels. While pricing can be an issue, the availability and affordability of electric vehicles are improving as technology advances and government incentives are implemented. You may help to create a cleaner, more sustainable future by evaluating the environmental benefits and examining viable options. While it is true that electric cars can be expensive, it is also true that their availability and affordability are increasing as technology progresses and economies of scale improve. Incentives, grants, and subsidies are also provided by various governments and organizations to make electric cars more accessible and cheap to a larger range of individuals."
        reduction = 0.96
    else:
        temp = "You're already making a significant impact in reducing your carbon footprint. By continuing to prioritize public transport, you'll not only save money on maintenance and extra charges but also contribute to cleaner air and a more sustainable future. Keep up the great work!"
        reduction = 0
    res.append(tuple(temp, reduction))

    if dataframe['plane'] > 0:
        temp = " \"Please don’t use planes\" is what we should say, but if you want to meet your family and friends from across the world there is no other good way to do it. Even if sometimes you need a sky-ride to travel long distances, what you should really know is that flying contributes 8 times as much as traveling by train. Next time you want to take a break and go on vacation, instead of a flight to a distant country (often not as beautiful as they told you), consider some place in your own country or the nearest ones that you can reach by train. PS with the money you’ll save taking the train, you can buy a tree on treedom to offset more CO2 or buy some ice cream, cheers!"
        reduction = 0.88
        res.append(tuple(temp, reduction))

# HOME
    # 1 DEGREE
    temp = "Around 7% of the energy you use for heating your house may be saved by lowering the thermostat by only one degree. Your annual energy cost could decrease by as much as € 70 for every degree you turn the heating down."
    reduction = 0.07
    res.append(tuple(temp, reduction))
##### SOLAR THERMAL PANEL !!!
    temp = "Installing solar thermal panels in your house offers both financial and environmental benefits. This technology uses renewable energy to heat water or air by utilizing the power of the sun. You can thereby considerably cut your heating costs while lowering your carbon footprint. Additionally, tax breaks and government incentives make it even more affordable. This long-term investment benefits the environment and increases the value of your home at the same time. By selecting solar thermal panels for your home, you can embrace solar energy, save money, and help the environment. Assuming you install 6 panels for a total of 1,5 MWh produced per year, you (and your family) would save a total of 900 kg of CO2 per year with respect to using just a typical heat pump water heater."
    kg_reduction = dataframe['number_of_days'] * 2.5
    res.append(tuple(temp, kg_reduction))

######################### WASTE IN PROGRESS #########################
    # if dataframe['waste'] > ?
    # temp = "Recycling glass, plastic, paper, and aluminum is highly recommended for reducing CO2 emissions. Glass recycling can result in a 41% reduction, plastic and paper recycling can achieve a 37% reduction, while aluminum recycling offers an impressive 96% reduction. These percentages represent the amount of CO2 emissions prevented when these materials are produced from raw materials. We can contribute to a greener future and reduce environmental impact by actively participating in recycling efforts. Glass recycling saves energy and lowers greenhouse gas emissions. Recycling plastic helps to reduce environmental impact and waste accumulation. Recycling paper saves trees, water, and energy. Aluminum recycling conserves energy and reduces the need for raw material extraction and processing. Let's recycle to make a positive difference for the environment."
    # dict_reduction = {
    #     'Plastic': 0.37,
    #     'Glass': 0.41,
    #     'Paper': 0.37,
    #     'Aluminium': 0.96}
    # res.append(tuple(temp, dict_reduction))


    # 0 = NOT RECYCLED
    if dataframe['wastePlastic'] == 1:

    if dataframe['wasteGlass'] == 1:

    if dataframe['wastePaper'] == 1:

    if dataframe['wasteAluminium'] == 1:
 