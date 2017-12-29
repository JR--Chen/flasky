import redis


def create_pool(**redis_kwargs):
    global __pool
    __pool = redis.ConnectionPool(
        host=redis_kwargs.get('host', 'localhost'),
        port=redis_kwargs.get('port', 6379),
        db=redis_kwargs.get('db', 0),
    )


def get_pool():
    global __pool
    return __pool


class Client:
    """Simple Queue with Redis Backend"""

    def __init__(self, name, namespace, **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.db = redis.Redis(connection_pool=get_pool(), **redis_kwargs)
        self.key = '%s:%s' % (namespace, name)
        self.pipe = self.db.pipeline(transaction=True)

    def execute(self):
        self.pipe.execute()

    def save(self):
        self.pipe.save()


class RedisQueue(Client):
    """Simple Queue with Redis Backend"""

    def __init__(self, name, namespace='queue', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        super().__init__(name, namespace, **redis_kwargs)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.db.llen(self.key)

    def __len__(self):
        return self.db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.db.blpop(self.key, timeout=timeout)

        else:
            item = self.db.lpop(self.key)

        if not isinstance(item, bytes) and item is not None:
            item = item[1]

        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)

    def lrange(self):
        return self.db.lrange(self.key, 0, self.__len__()-1)


class RedisSet(Client):
    def __init__(self, name, namespace='set', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""

        super().__init__(name, namespace, **redis_kwargs)

    def add(self, value):
        self.db.sadd(self.key, value)

    def ismembers(self, value):
        return self.db.sismember(name=self.key, value=value)

    def members(self):
        return self.db.smembers(self.key)

    def __contains__(self, item):
        return self.ismembers(item)


class RedisHash(Client):
    def __init__(self, name, namespace='hash', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""

        super().__init__(name, namespace, **redis_kwargs)

    def keys(self):
        return self.db.hkeys(name=self.key)

    def delete(self, key):
        self.db.hdel(self.key, key)

    def __len__(self):
        return self.db.hlen(name=self.key)

    def __setitem__(self, key, value):
        self.db.hset(self.key, key, value)

    def __getitem__(self, key):
        self.db.hget(self.key, key)

    def __contains__(self, item):
        return self.db.hexists(self.key, item)


