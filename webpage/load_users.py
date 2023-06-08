
import ast
import pandas as pd
from classes.footprintcalculator import footprintCalculator
import csv

from classes.mongodbmanager import MongoDBManager
from classes.postgresqlmanager import PostgreSQLManager

user_files = ["vegan", "mixed_diet", "low_meat_eater", "pescetarian", "heavy_consumer", "average_consumer", "average_consumer_plus_plane", "random"]

mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')
postgresql_manager = PostgreSQLManager('localhost',5858,'postgres', 'password', 'mydatabase')

for user in user_files:
    print("User: ", user)
    df = pd.read_csv("./Users/" + user + ".csv")
    df.fillna(0, inplace=True)

    user_data = {
        'username': user,
        'password': user
    }
            
    mongo_manager.insert_user(user_data)

    table_name_carbon = f'user_{user}_carbon_footprint'

    columns_cf = [
        'start_date DATE',
        'end_date DATE',
        'diet FLOAT',  
        'transportation FLOAT',
        'car FLOAT',
        'bustrain FLOAT',
        'plane FLOAT',
        'housing FLOAT',
        'consumption FLOAT',
        'waste FLOAT',
        'number_of_days FLOAT',
        'average_per_day FLOAT',
        'total FLOAT'
    ]

    postgresql_manager.create_table(table_name_carbon, columns_cf)

    for index, row in df.iterrows():
        print("Row Index:", index)
        print("Row Data:", row)

        row_dict = row.to_dict()
        row_dict['origin_airports'] = ast.literal_eval(row_dict['origin_airports'])
        row_dict['destination_airports'] = ast.literal_eval(row_dict['destination_airports'])
        row_dict['cabin_classes'] = ast.literal_eval(row_dict['cabin_classes'])
        row_dict['round_trips'] = ast.literal_eval(row_dict['round_trips'])
        row_dict['answerHowManyPeople'] = str(row_dict['answerHowManyPeople'])
        row_dict['anwerWasteMaterials'] = row_dict['anwerWasteMaterials'].split(", ")
        
        carbon_footprint_manager = footprintCalculator(row_dict)
        carbon_footprint = carbon_footprint_manager.computeCarbonFootprint()

        

        postgresql_manager.insert_data(table_name_carbon,carbon_footprint)


        