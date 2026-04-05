import time

from limits import storage, limits, strategies, parse
from .config import Config
from .exceptions import LimitExceeded

NS='postfixlimit'

class Limiter:
    def __init__(self, config):
        self.config = config
        self.field = self.config.field
        self.default_limit = self.config.default_limit
        self.limits = self.config.limits
        self.counters = {}
        

        self.storage = storage.storage_from_string(self.config.storage)

        if self.config.strategy == 'fixed-window':
            self.strategy = strategies.FixedWindowRateLimiter(self.storage)
        else:            
            raise ValueError(f"Unsupported strategy type: {self.config.strategy}")

        # init limiters for all configured keys
        for key, limit_info in self.limits.items():
            print(f"Configuring limiter for {key}: {limit_info}")
            self.counters[key] = parse(limit_info)

        # syntax check: create default limiter for keys not explicitly configured
        _ = parse(self.default_limit)

    def check(self, key: str):
        if key not in self.counters:
            print("make new limiter for key", key)
            self.counters[key] = parse(self.default_limit)

        cnt = self.counters[key]

        if self.strategy.test(cnt, NS, key):
            self.strategy.hit(cnt, NS, key)
            return True
        else:
            msg = self.config.action_text.format(limit=str(cnt), field=self.field, key=key)
            raise LimitExceeded(action=self.config.action, 
                                message=msg)

    def dump(self):
        print("Limits:")
        for key, limiter in self.counters.items():
            window = self.strategy.get_window_stats(limiter, NS, key)
            print(f"  {key}: {limiter} remaining: {window.remaining}")
    
    def reset(self, sender: str):
        print("Resetting counter for", sender)
        
        if sender=='ALL':
            self.storage.reset()
            self.counters = {}
            print("All counters reset")
            return
        
        cnt = self.counters.get(sender)
        if cnt is None:
            self.counters[sender] = parse(self.default_limit)
            cnt = self.counters.get(sender)
        
        self.strategy.clear(cnt, NS, sender)
