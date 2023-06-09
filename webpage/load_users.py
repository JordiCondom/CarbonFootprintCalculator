
import ast
import datetime
import pandas as pd
from classes.footprintcalculator import footprintCalculator
import csv

from classes.postgresqlmanager import PostgreSQLManager
from classes.redismanager import RedisManager

user_files = ["vegan", "mixed_diet", "low_meat_eater", "pescetarian", "heavy_consumer", "average_consumer", "average_consumer_plus_plane", "random"]

postgresql_manager = PostgreSQLManager('0.0.0.0',5858, 'docker', 'docker', 'mydatabase')
redis_manager = RedisManager('localhost', 6379, 2)
redis_manager_1 = RedisManager('localhost', 6379, 1)

for user in user_files:
    print("User: ", user)
    df = pd.read_csv("./Users/" + user + ".csv")
    df.fillna(0, inplace=True)

    user_data = {
        'id': user,
        'username': user,
        'password': user
    }
            
    redis_manager.insert_user(user_data)

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
            'shopping_profile FLOAT',
            'refurbished FLOAT',
            'waste FLOAT',
            'plastic FLOAT',
            'glass FLOAT',
            'paper FLOAT',
            'aluminium FLOAT',
            'number_of_days FLOAT',
            'average_per_day FLOAT',
            'total FLOAT'
        ]

    postgresql_manager.create_table(table_name_carbon, columns_cf)

    for index, row in df.iterrows():

        row_dict = row.to_dict()
        start_date = datetime.datetime.strptime(row_dict['start_date'], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(row_dict['end_date'], '%Y-%m-%d').date()
        redis_manager_1.store_date_range(user, start_date, end_date)

        row_dict['origin_airports'] = ast.literal_eval(row_dict['origin_airports'])
        row_dict['destination_airports'] = ast.literal_eval(row_dict['destination_airports'])
        row_dict['cabin_classes'] = ast.literal_eval(row_dict['cabin_classes'])
        row_dict['round_trips'] = ast.literal_eval(row_dict['round_trips'])
        row_dict['answerHowManyPeople'] = str(row_dict['answerHowManyPeople'])
        row_dict['anwerWasteMaterials'] = row_dict['anwerWasteMaterials'].split(", ")
        
        carbon_footprint_manager = footprintCalculator(row_dict)
        carbon_footprint = carbon_footprint_manager.computeCarbonFootprint()

        

        postgresql_manager.insert_data(table_name_carbon,carbon_footprint)


postgresql_manager.close_connection()


        