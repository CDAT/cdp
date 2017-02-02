
class cache():
    def __init__(self, func):
        self._cache = {}
        self._func = func

    def __call__(self, *args, **kwargs):
        cache_key = (self._func.__name__, args)
        if cache_key not in self._cache:
            print 'not in cache'
            self._cache[cache_key] = self._func(*args, **kwargs)
        else:
            print 'in cache'
        return self._cache[cache_key]
