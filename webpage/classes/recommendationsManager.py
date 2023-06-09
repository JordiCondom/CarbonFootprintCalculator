import random

class RecommendationsManager:
    def __init__(self, data):
        self.data = data
        self.recommendations_list = []

    def generate_recommendations(self, number_of_rows):
        if self.data['diet']/self.data['number_of_days'] > 4.6:
            self.recommendations_list.append("Diet: With a little change in your diet you can drastically lower your carbon footprint, if you decide to reduce your consumption of meat to just one steak (350g) instead of two each week you can save 35% with respect to eating 2!")
        else:
            self.recommendations_list.append("Diet: Your diet doesn't  produce as much CO2 as the one of a frequent meat eater. You're definitely doing your part, and if you want to go Vegan you should know that your emission with respect to the Vegetarian would drop by 24%. If you are already vegan, but you are reading this suggestion, this means that you waste more than 10% of your food, so please keep on reading for some suggestions on that!")


        if self.data['car'] > self.data['bustrain']:
            self.recommendations_list.append("Carpooling or sharing rides with others presents numerous benefits in reducing the number of vehicles on the road. We can effectively reduce traffic congestion and lessen the strain on our transportation infrastructure by grouping trips together and sharing transportation. We can maximize our resource use, reduce congestion, reduce negative environmental effects, and develop a more sustainable and effective transportation system for the benefit of all by adopting this collaborative approach. Let's band together and use shared rides to change the world.")
            self.recommendations_list.append("Transportation: Taking the train or the bus can save you up to four times the money you would spend driving your own car, and for medium-length distances you would cut your emissions by ~80% (LINK). Regular use of your personal car will necessitate maintenance costs as well as various extra charges such as parking fees, pollution violations, and speeding fines. By taking public transportation, you will be able to save all of the money that would otherwise be spent on expenses associated with driving a personal vehicle. So it seems counterintuitive, but you should consider taking public transportation even if you possess a car! We often think that we have to use the car at all costs, given the huge investment we did buying it… but to really save money we can simply decide to not use it for some of our trips.")
        else:
            self.recommendations_list.append("Transportation: You're already making a significant impact in reducing your carbon footprint. By continuing to prioritize public transport, you'll not only save money on maintenance and extra charges but also contribute to cleaner air and a more sustainable future. Keep up the great work!")
        
        if self.data['plane'] > 0:
            self.recommendations_list.append("Transportation: \"Please don’t use planes\" is what we should say, but if you want to meet your family and friends from across the world there is no other good way to do it. Even if sometimes you need a sky-ride to travel long distances, what you should really know is that flying contributes 8 times as much as traveling by train. Consider, as an example, that France has implemented a ban on short-haul flights where train travel is viable, aiming to reduce carbon emissions and promote sustainable transportation. Next time you want to take a break and go on vacation, instead of a flight to a distant country (often not as beautiful as they told you), consider some place in your own country or the nearest ones that you can reach by train. PS with the money you’ll save taking the train, you can buy a tree on treedom to offset more CO2 or buy some ice cream, cheers!")

        option1 = "Housing: Around 7% of the energy you use for heating your house may be saved by lowering the thermostat by only one degree. Your annual energy cost could decrease by as much as € 70 for every degree you turn the heating down."
        option2 = "There are also various advantages to installing energy-efficient appliances and LED lighting. This not only lowers your electricity bills and saves you money in the long run, but it also reduces energy consumption, minimizes your carbon footprint, and supports sustainability. Making this switch helps to create a greener future and a healthier earth."
        option3 = "Housing: Installing solar thermal panels in your house offers both financial and environmental benefits. This technology uses renewable energy to heat water or air by utilizing the power of the sun. You can thereby considerably cut your heating costs while lowering your carbon footprint. Additionally, tax breaks and government incentives make it even more affordable. This long-term investment benefits the environment and increases the value of your home at the same time. By selecting solar thermal panels for your home, you can embrace solar energy, save money, and help the environment. Assuming you install 6 panels for a total of 1,5 MWh produced per year, you (and your family) would save a total of 900 kg of CO2 per year with respect to using just a typical heat pump water heater."

        # Generate a random number between 0 and 2
        random_number = random.randint(0, 2)

        # Append the selected option to the recommendations list
        if random_number == 0:
            self.recommendations_list.append(option1)
        elif random_number == 1:
            self.recommendations_list.append(option2)
        else:
            self.recommendations_list.append(option3)
            
        if self.data['shopping_profile']/number_of_rows > 0:
            self.recommendations_list.append("Consumption: We have realized you have a high shopping profile. You probably already know that there exist some fashion brands which offset all their emissions and use sustainable materials, but quality and sustainability, paired with the fast-fashion desire for endless consumption, turns out to be quite expensive. The solution is simple: second hand clothing. Nowadays there are many solutions, you can search for many websites that center their business around second hand clothing, delivering your ‘new’ pair of shoes at your doorstep. But come on… you did so much to reduce your carbon footprint already, as a last selfless act of mercy for our planet consider going to a second hand clothing physical shop.")

        if self.data['refurbished']/number_of_rows > 0:
            self.recommendations_list.append("Consumption: Consider buying refurbished laptops, computers, and smartphones instead of new ones. Refurbished devices have a longer lifespan and help minimize electronic waste. Manufacturing new devices requires a significant amount of energy and resources, which contributes to greenhouse gas emissions. Refurbished options are thoroughly inspected and repaired, providing dependable functionality at a lower cost. Purchasing refurbished electronics reduces raw material demand and promotes resource conservation. It also promotes the development of a circular economy. We can reduce electronic waste and carbon emissions by embracing refurbished technology. Let's make a choice that makes us spend less for a greener future.")

        if self.data['plastic']/number_of_rows < 1:
            self.recommendations_list.append("Waste: We have noted you do not always recycle plastic. Plastic recycling can achieve a 37% reduction in carbon footprint. Recycling plastic helps to reduce environmental impact and waste accumulation. Let's recycle to make a positive difference for the environment.")
        if self.data['glass']/number_of_rows < 1: 
            self.recommendations_list.append("Waste: We have noted you do not always recycle glass. Glass recycling can result in a 41% reduction in carbon footprint. Glass recycling saves energy and lowers greenhouse gas emissions. Let's recycle to make a positive difference for the environment.")
        if self.data['paper']/number_of_rows < 1:
            self.recommendations_list.append("Waste: We have noted you do not always recycle paper. Paper recycling can achieve a 37% reduction in carbon footprint. Recycling paper saves trees, water, and energy. Let's recycle to make a positive difference for the environment.")
        if self.data['aluminium']/number_of_rows < 1:
            self.recommendations_list.append("Waste: We have noted you do not always recycle aluminum. Aluminum recycling can achieve a 96% reduction in carbon footprint. Aluminum recycling conserves energy and reduces the need for raw material extraction and processing. Let's recycle to make a positive difference for the environment.")


        self.recommendations_list.append("Consumption and Waste: Significant environmental benefits can be obtained by reducing the use of single-use items like plastic bottles, bags, and eating utensils. We can conserve valuable resources and reduce pollution by reducing our reliance on these things. This also lowers the demand for their production. Besides, adopting reusable alternatives like cloth bags and stainless steel water bottles, also results in long-term financial savings.")

        return self.recommendations_list