import json

import redis

from flexpkit.basic_utils import current_strftime
from flexpkit.exp_settings import redis_config


def generate_lock_key(key):
    return 'lock_{}'.format(key)


def generate_cache_key(key):
    return 'cache_{}'.format(key)


class RedisCli:

    redis_conn = None

    def __init__(self):
        self.redis_conn = redis.Redis(host=redis_config['host'], port=redis_config['port'])

    def broadcast(self, message_queue, sender, event):
        event['sender'] = sender
        event['timestamp'] = current_strftime()

        self.redis_conn.publish(message_queue, json.dumps(event))


    def set_lock(self, key, value, lock_timeout=10):
        lock_key = generate_lock_key(key)
        result = self.redis_conn.setnx(lock_key, value)
        if not result:
            return False

        if lock_timeout > 0:
            self.redis_conn.expire(lock_key, lock_timeout)

        return True

    def get_lock_value(self, key):
        lock_key = generate_lock_key(key)

        return self.redis_conn.get(lock_key).decode()

    def remove_lock(self, key):
        lock_key = generate_lock_key(key)
        self.redis_conn.delete(lock_key)


    def check_cache_exists(self, key):
        key = generate_cache_key(key)

        return self.redis_conn.exists(key)

    def set_cached_value(self, key, val):
        key = generate_cache_key(key)

        self.redis_conn.set(key, val)
    
    def get_cached_value(self, key):
        key = generate_cache_key(key)

        return self.redis_conn.get(key)

    def get_connection(self):
        return self.redis_conn


redis_cli = RedisCli()