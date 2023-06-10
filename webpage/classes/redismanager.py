import redis
from datetime import datetime

class RedisManager:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)
    
    def set_key_value(self, key, value):
        # Set a key-value pair in Redis
        self.r.set(key, value)

    def get_value_by_key(self, key):
        # Get the value associated with a given key in Redis
        value = self.r.get(key)
        return value.decode()

    def key_exists_boolean(self,key):
        # Check if a key exists in Redis and return a boolean value
        return self.r.exists(key)
    
    def store_date_range(self, username, start_date, end_date):
        # Store a date range in Redis as a field in a hash

        # Convert dates to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        final_str = str(start_date_str + ":" + end_date_str)
        # Store the date range in Redis as a field in the Hash
        self.r.hset(username, final_str, end_date_str)

    def delete_date_range(self, username, start_date, end_date):
        # Delete a date range from the hash associated with a given username

        # Convert dates to strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Delete the date range for the given username
        self.r.hdel(username, f'{start_date_str}:{end_date_str}')

    def check_date_overlap(self, username, new_start_date, new_end_date):
        # Check if a new date range overlaps with existing date ranges for a given username

        # Convert dates to strings and get all fields (date ranges) for the specified username
        date_ranges = self.r.hgetall(username)

        for range_str, score in date_ranges.items():
            range_start_str, range_end_str = map(str, range_str.decode().split(':'))
            # Convert range dates to datetime objects
            range_start = datetime.strptime(range_start_str, '%Y-%m-%d').date()
            range_end = datetime.strptime(range_end_str, '%Y-%m-%d').date()
            # Check for overlap
            if range_start <= new_end_date and new_start_date <= range_end:
                return [True, range_start, range_end]

        return [False, new_start_date, new_end_date]
    

    def delete_user_data(self, username):
        # Delete all data associated with a specific username

        # Get all the fields (date ranges) for the specified username
        date_ranges = self.r.hkeys(username)

        # Delete each date range for the username
        for date_range in date_ranges:
            self.r.hdel(username, date_range)
        
        # Delete the username itself
        self.r.delete(username)


    def insert_user(self, user_data):
        # Insert a user into Redis with the provided user data

        user_id = user_data.get('id')
        self.r.hmset(f"user:{user_id}", user_data)
        print(f"User inserted with id: {user_id}")

    def list_users(self):
        # List all the users stored in Redis

        user_keys = self.r.keys("user:*")
        for key in user_keys:
            user_data = self.r.hgetall(key)
            print(user_data)

    def delete_all_users(self):
        # Delete all users stored in Redis

        user_keys = self.r.keys("user:*")
        for key in user_keys:
            self.r.delete(key)
        print(f"Deleted {len(user_keys)} users")

    def delete_user_by_username(self, username):
        # Delete a user from Redis based on their username

        user_keys = self.r.keys("user:*")
        deleted_count = 0
        for key in user_keys:
            user_data = self.r.hgetall(key)
            current_username = user_data[b'username'].decode()
            if current_username == username:
                self.r.delete(key)
                deleted_count += 1
        if deleted_count > 0:
            print(f"Deleted {deleted_count} user(s) with username '{username}'")
        else:
            print(f"No user found with username '{username}'")

    def check_login(self, username, password):
        # Check if a user login is valid based on the provided username and password

        user_keys = self.r.keys("user:*")
        for key in user_keys:
            user_data = self.r.hgetall(key)

            current_username = user_data[b'username'].decode()
            current_password = user_data[b'password'].decode()
            if current_username == username and current_password == password:
                return True
        return False
    
    def check_username_exists(self, username):
        # Check if a username already exists in Redis

        user_keys = self.r.keys("user:*")
        print("hola")
        for key in user_keys:
            user_data = self.r.hgetall(key)
            current_username = user_data[b'username'].decode()
            if current_username == username:
                return True
        return False