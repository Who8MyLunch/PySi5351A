
import pickle


def flexi_hash(data):
    """Compute a hash value from any data type, not just immutables.
    """
    try:
        key = hash(data)
    except TypeError:
        key = hash(pickle.dumps(data))
        
    return key



class Memoize():
    """Function decorator
    """
    def __init__(self, func):
        self._cache = {}
        self._func = func
 
    def __call__(self, *args, **kwargs):
        key = flexi_hash(args) + flexi_hash(kwargs)

        if key not in self._cache:
            self._cache[key] = self._func(*args, **kwargs)

        return self._cache[key]
        
    def _clear_cache(self):
        self._cache = {}
        
        
        
if __name__ == '__main__':
    # example
    
    import time

    @Memoize
    def hello(a, b, c=[1]):
        time.sleep(2)
        result = a + b
        for v in c:
            result += v

        return result
    
    print(hello(1, 2, [3, 4, 5]))
    print(hello(1, 2, [3, 4, 5]))
    print(hello(1, 2, [3, 4, 7]))
    print(hello(1, 2, [3, 4, 7]))
    
          