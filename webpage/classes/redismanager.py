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
    
    def insert_range_dates(self, range_start, range_end, range_id):
        self.r.zadd("date_ranges", {str(range_start): 0, str(range_end): 0})
        self.r.hset("range_ids", str(range_start), range_id)
        self.r.hset("range_ids", str(range_end), range_id)

    def get_all_date_ranges(self):
        date_ranges = self.r.zrange("date_ranges", 0, -1, withscores=True)
        return date_ranges

    def get_all_range_ids(self):
        range_ids = self.r.hgetall("range_ids")
        return range_ids
    
    def dates_overlap(self, range_start, range_end):
        print("DATE RANGES: ", self.get_all_date_ranges())
        print("DATE IDS: ", self.get_all_range_ids())
        print("RANGE START: ", range_start)
        print("RANGE END:", range_end)
        overlapping_ranges = self.r.zrangebyscore("date_ranges", min=str(range_start), max=str(range_end))
        print("OVERLAPPING RANGES: ", overlapping_ranges)
        return overlapping_ranges