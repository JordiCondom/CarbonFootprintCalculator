from classes.postgresqlmanager import PostgreSQLManager
from classes.redismanager import RedisManager


user_files = ["vegan", "mixed_diet", "low_meat_eater", "pescetarian", "heavy_consumer", "average_consumer", "average_consumer_plus_plane", "random"]

for username in user_files:
    table_name_answers = f'user_{username}_answers'
    table_name_carbon = f'user_{username}_carbon_footprint'
    postgresql_manager = PostgreSQLManager('0.0.0.0',5858,'docker', 'docker', 'mydatabase')
    redis_manager = RedisManager('localhost', 6379, 1)

    redis_manager.delete_user_data(username)
    
    postgresql_manager.delete_all_table_data(table_name_carbon)

    postgresql_manager.close_connection()