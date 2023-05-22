import redis

class RedisManager:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)
    
    def set_key_value(self, key, value):
        self.r.set(key, value)

    def get_value_by_key(self, key):
        value = self.r.get(key)
        return value.decode()

    def key_exists_boolean(self,key):
        return self.r.exists(key)