import time

class Singleton:
    _instance = None
    _initialized = False
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.init1()
        self._initialized = True
    
    def init1(self):
        self.last_dump = time.time()
        self.counter = 0