from pymongo import MongoClient


class MongoDBManager:
    def __init__(self, database_name, collection_name):
        self.client = MongoClient('mongodb://mongo:27017/')
        self.db = self.client[database_name]
        self.users_collection = self.db[collection_name]
    
    def insert_user(self, user_data):
        result = self.users_collection.insert_one(user_data)
        print(f"User inserted with id: {result.inserted_id}")
    
    def list_users(self):
        users = self.users_collection.find()
        for user in users:
            print(user)
    
    def delete_all_users(self):
        result = self.users_collection.delete_many({})
        print(f"Deleted {result.deleted_count} users")
    
    def delete_user_by_username(self, username):
        result = self.users_collection.delete_one({'username': username})
        if result.deleted_count > 0:
            print(f"User with username '{username}' deleted")
        else:
            print(f"No user found with username '{username}'")

    def check_login(self, username, password):
        user = self.users_collection.find_one({'username': username})
        if user and user['password'] == password:
            return True
        else:
            return False
    
    def close_connection(self):
        self.client.close()

# Usage example
mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')

user_data1 = {
    'username': 'john_doe',
    'password': '123456',
    'email': 'johndoe@example.com'
}

