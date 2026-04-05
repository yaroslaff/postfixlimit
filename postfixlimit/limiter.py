import logging
import sys
import time
import datetime

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
        
        self.logger: logging.Logger = logging.getLogger("postfixlimit")

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
        self.logger.info(f".. check {key}")
        if key not in self.counters:
            self.logger.info(f"make new limiter for key {key}")
            self.counters[key] = parse(self.default_limit)

        cnt = self.counters[key]

        if self.strategy.test(cnt, NS, key):
            self.strategy.hit(cnt, NS, key)
            return True
        else:
            msg = self.config.action_text.format(limit=str(cnt), field=self.field, key=key)
            self.logger.warning(f"Limit exceeded for {key}: {msg}")
            raise LimitExceeded(action=self.config.action, 
                                message=msg)

    def dump(self):
        # dump to self.config.dump_file if configured, otherwise print to stdout

        out = open(self.config.dump_file, 'w') if self.config.dump_file else sys.stdout
        try:
            print(f"Limits ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):", file=out)    
            for key, limiter in self.counters.items():
                window = self.strategy.get_window_stats(limiter, NS, key)            
                print(f"  {key}: {limiter} remaining: {window.remaining}", file=out)
        finally:            
            if self.config.dump_file:
                out.close()
    
    def reset(self, sender: str):
        print("Resetting counters for", sender)
        
        if sender=='ALL':
            self.storage.reset()
            self.counters = {}
            return
        
        cnt = self.counters.get(sender)
        if cnt is None:
            self.counters[sender] = parse(self.default_limit)
            cnt = self.counters.get(sender)
        
        self.strategy.clear(cnt, NS, sender)
