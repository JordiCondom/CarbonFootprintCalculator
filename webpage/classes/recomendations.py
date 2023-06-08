import pandas as pd
def recomendations(dataframe):
    res = []
    # DIET
    if dataframe['diet'][0] / dataframe['number_of_days'][0] > 4.6:
        temp = "With a little change in your diet you can drastically lower your carbon footprint, if you decide to reduce your consumption of meat to just one steak (350g) instead of two each week you can save 35% with respect to eating 2!"
        reduction = 0.35
    else:
        temp = "Your diet doesn't  produce as much CO2 as the one of a frequent meat eater. You're definitely doing your part, and if you want to go Vegan you should know that your emission with respect to the Vegetarian would drop by 24%. If you are already vegan, but you are reading this suggestion, this means that you waste more than 30% of your food, so please keep on reading for some suggestions on that!"
        reduction = 0.24
    res.append(('diet', (temp, reduction)))

    # TRANSPORTATION
    if dataframe['car'][0] > 2 * dataframe['bustrain'][0]:  # Private to Public transport
        temp = "Taking a train can save you up to four times the money you would spend driving your own car, and for medium-length distances you would cut your emissions by ~80% (LINK). Regular use of your personal car will necessitate maintenance costs as well as various extra charges such as parking fees, pollution violations, and speeding fines. By taking public transportation, you will be able to save all of the money that would otherwise be spent on expenses associated with driving a personal vehicle. So it seems counterintuitive, but you should consider taking public transportation even if you possess a car! We often think that we have to use the car at all costs, given the huge investment we did buying it… but to really save money we can simply decide to not use it for some of our trips. If you want to know more about this topic, discover more benefits of public transport here (LINK)"
        reduction = 0.8
    elif dataframe['car'][0] > dataframe['bustrain'][0]:  # Switch Car
        temp = "Switching to an electric vehicle can have a huge environmental benefit. Electric vehicles have no exhaust emissions, lowering greenhouse gas emissions and increasing air quality. Even with energy generation, according to research by the European Energy Agency, driving an electric car emits 96 % fewer carbon emissions than doing so in a gasoline or diesel vehicle. They are also more energy-efficient, converting a higher percentage of grid energy to wheel power, resulting in lower energy use and reliance on fossil fuels. While pricing can be an issue, the availability and affordability of electric vehicles are improving as technology advances and government incentives are implemented. You may help to create a cleaner, more sustainable future by evaluating the environmental benefits and examining viable options. While it is true that electric cars can be expensive, it is also true that their availability and affordability are increasing as technology progresses and economies of scale improve. Incentives, grants, and subsidies are also provided by various governments and organizations to make electric cars more accessible and cheap to a larger range of individuals."
        reduction = 0.96
    else:
        temp = "You're already making a significant impact in reducing your carbon footprint. By continuing to prioritize public transport, you'll not only save money on maintenance and extra charges but also contribute to cleaner air and a more sustainable future. Keep up the great work!"
        reduction = 0
    res.append(('transportation', (temp, reduction)))

    if dataframe['plane'][0] > 0:
        temp = "\"Please don’t use planes\" is what we should say, but if you want to meet your family and friends from across the world there is no other good way to do it. Even if sometimes you need a sky-ride to travel long distances, what you should really know is that flying contributes 8 times as much as traveling by train. Consider, as an example, that France has implemented a ban on short-haul flights where train travel is viable, aiming to reduce carbon emissions and promote sustainable transportation. Next time you want to take a break and go on vacation, instead of a flight to a distant country (often not as beautiful as they told you), consider some place in your own country or the nearest ones that you can reach by train. PS with the money you’ll save taking the train, you can buy a tree on treedom to offset more CO2 or buy some ice cream, cheers!"
        reduction = 0.88
        res.append(('transportation', (temp, reduction)))

    # HOME
    # 1 DEGREE
    temp = "Around 7% of the energy you use for heating your house may be saved by lowering the thermostat by only one degree. Your annual energy cost could decrease by as much as € 70 for every degree you turn the heating down."
    reduction = 0.07
    res.append(('housing', (temp, reduction)))
    ##### SOLAR THERMAL PANEL
    temp = "Installing solar thermal panels in your house offers both financial and environmental benefits. This technology uses renewable energy to heat water or air by utilizing the power of the sun. You can thereby considerably cut your heating costs while lowering your carbon footprint. Additionally, tax breaks and government incentives make it even more affordable. This long-term investment benefits the environment and increases the value of your home at the same time. By selecting solar thermal panels for your home, you can embrace solar energy, save money, and help the environment. Assuming you install 6 panels for a total of 1,5 MWh produced per year, you (and your family) would save a total of 900 kg of CO2 per year with respect to using just a typical heat pump water heater."
    kg_reduction = dataframe['number_of_days'] * 2.5
    res.append(('housing', (temp, kg_reduction)))

    # WASTE

    # 0 = NOT RECYCLED
    dont_recycle = sum(
        [dataframe['wastePlastic'], dataframe['wasteGlass'], dataframe['wastePaper'], dataframe['wasteAluminium']])
    if dont_recycle[0] >= 1:
        temp = "Recycling glass, plastic, paper, and aluminum is highly recommended for reducing CO2 emissions. Glass recycling can result in a 41% reduction, plastic and paper recycling can achieve a 37% reduction, while aluminum recycling offers an impressive 96% reduction. These percentages represent the amount of CO2 emissions prevented when these materials are produced from raw materials. We can contribute to a greener future and reduce environmental impact by actively participating in recycling efforts. Glass recycling saves energy and lowers greenhouse gas emissions. Recycling plastic helps to reduce environmental impact and waste accumulation. Recycling paper saves trees, water, and energy. Aluminum recycling conserves energy and reduces the need for raw material extraction and processing. Let's recycle to make a positive difference for the environment."
        reduction = 0.0
        if dataframe['wastePlastic'][0] == 1:
            reduction = 0.37
        elif dataframe['wasteGlass'][0] == 1:
            reduction = 0.41
        elif dataframe['wastePaper'][0] == 1:
            reduction = 0.37
        elif dataframe['wasteAluminium'][0] == 1:
            reduction = 0.96
        else:
            raise Exception('Problem in the code with Waste')
        res.append(('waste', (temp, reduction)))

    # Tech
    temp = "Consider buying refurbished laptops, computers, and smartphones instead of new ones. Refurbished devices have a longer lifespan and help minimize electronic waste. Manufacturing new devices requires a significant amount of energy and resources, which contributes to greenhouse gas emissions. Refurbished options are thoroughly inspected and repaired, providing dependable functionality at a lower cost. Purchasing refurbished electronics reduces raw material demand and promotes resource conservation. It also promotes the development of a circular economy. We can reduce electronic waste and carbon emissions by embracing refurbished technology. Let's make a choice that makes us spend less for a greener future."
    reduction = 0.95  # 5% for transport
    res.append(('consumption', (temp, reduction)))
    # Clothing
    temp = "You probably already know that there exist some fashion brands which offset all their emissions and use sustainable materials, but quality and sustainability, paired with the fast-fashion desire for endless consumption, turns out to be quite expensive. The solution is simple: second hand clothing. Nowadays there are many solutions, you can search for many websites that center their business around second hand clothing, delivering your ‘new’ pair of shoes at your doorstep. But come on… you did so much to reduce your carbon footprint already, as a last selfless act of mercy for our planet consider going to a second hand clothing physical shop."
    reduction = 0.95  # 5% for transport
    res.append(('consumption', (temp, reduction)))

    # Additional recommendations for each category
    additional_recommendations = {
        'diet': [
            (
                "As consumers, we hold the power to make conscious choices that impact the environment. By selecting brands with paper and aluminum packaging, we can contribute to reducing the carbon footprint and promoting sustainability. Opting for these materials supports the use of renewable resources and lowers energy consumption during production. By making informed purchasing decisions and embracing responsible recycling practices, we actively play a role in creating a greener future for our planet.")
        ],
        'transportation': [
            (
                "Carpooling or sharing rides with others presents numerous benefits in reducing the number of vehicles on the road. We can effectively reduce traffic congestion and lessen the strain on our transportation infrastructure by grouping trips together and sharing transportation. We can maximize our resource use, reduce congestion, reduce negative environmental effects, and develop a more sustainable and effective transportation system for the benefit of all by adopting this collaborative approach. Let's band together and use shared rides to change the world.")
        ],
        'housing': [
            (
                "There are also various advantages to installing energy-efficient appliances and LED lighting. This not only lowers your electricity bills and saves you money in the long run, but it also reduces energy consumption, minimizes your carbon footprint, and supports sustainability. Making this switch helps to create a greener future and a healthier earth.")
        ],
        'waste': [
            ("")
        ],
        'consumption': [
            (
                "Significant environmental benefits can be obtained by reducing the use of single-use items like plastic bottles, bags, and eating utensils. We can conserve valuable resources and reduce pollution by reducing our reliance on these things. This also lowers the demand for their production. Besides, adopting reusable alternatives like cloth bags and stainless steel water bottles, also results in long-term financial savings."),
            (
                "Instead of throwing things away, consider repairing them or donating them. We increase the worth of existing products and reduce the demand for additional production by finding new uses for them. Repurposing fosters innovation, creativity, and a more sustainable way of thinking. Additionally, by donating items that are no longer needed, waste can be reduced. We actively contribute to a circular economy and ease the burden on our planet's resources by adopting a mindset of repurposing and giving. Let's use considerate reuse and donation techniques to give our possessions a second chance at life and have a positive impact.")]
    }

    for category, recommendations in additional_recommendations.items():
        for recommendation in recommendations:
            res.append((category, (recommendation, 0)))
    return res


########## Data Entry

data = {
    'start_date': [1],
    'end_date': [2],
    'diet': [3],
    'transportation': [4],
    'car': [5],
    'bustrain': [6],
    'plane': [7],
    'housing': [8],
    'consumption': [9],
    'waste': [10],
    'wastePlastic': [1],
    'wasteGlass': [0],
    'wastePaper': [0],
    'wasteAluminium': [0],
    'number_of_days': [1],
    'average_per_day': [2],
    'total': [3]
}

dataf = pd.DataFrame(data)

# CHOOSE THE ORDER OF THE RECOMENDATIONS based on the CO2 values:

col_names = ['diet', 'transportation', 'housing', 'waste', 'consumption']
df = dataf[col_names]

sorted_columns = sorted(df.columns, key=lambda col: df[col].values[0], reverse=True)
# print(sorted_columns)

sasso = recomendations(dataf)

for column in sorted_columns:
    print(column.upper())
    column_recommendations = [element[1][0] for element in sasso if element[0] == column]
    for recommendation in column_recommendations:
        print(recommendation)
        print()
    print()
