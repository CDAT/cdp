class Cache(object):
    def __init__(self):
        self._cache = {}
        self._hits = 0
        self._misses = 0

    def __call__(self, func, *args, **kwargs):
        cache_key = (func, args)
        if cache_key not in self._cache:
            self._misses += 1
            self._cache[cache_key] = func(*args, **kwargs)
        else:
            self._hits += 1
        return self._cache[cache_key]

    def cache_info(self):
        """Returns a string akin to what functools.lru_cache does in Python 3"""
        return 'CacheInfo(hits=%s, misses=%s)' % (self._hits, self._misses)

    def clear(self):
        """Clears the cache."""
        for key, _ in self._cache:
            del self._cache[key]

cache = Cache()
