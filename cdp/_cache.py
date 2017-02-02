class Cache():
    def __init__(self):
        self._cache = {}

    def __call__(self, func, *args, **kwargs):
        cache_key = (func.__name__, args)
        if cache_key not in self._cache:
            print 'not in cache'
            self._cache[cache_key] = func(*args, **kwargs)
        else:
            print 'in cache'
        return self._cache[cache_key]

    def clear(self):
        """ Clears the cache. """
        for key, value in self._cache:
            del self._cache[key]

cache = Cache()
