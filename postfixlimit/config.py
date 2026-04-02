"""
exanple config file (postfixlimit.toml):
address=127.0.0.1
port=4455
field=sender # or client_address or sasl_username
default_limit=1000
default_period=3600


# per field configuration. LIMIT / PERIOD (seconds), period is optional, default to global default_period.
# period can be given as word (sec, seconds, min, minute, hr, hour, d, day) or just number (default to seconds)
[limits]
aaa@bbb.com = 100/86400
bbb@bbb.com = 1000/day
ccc@bbb.com = 100 
"""

import toml


class TomlConfig:
    def __init__(self, path):
        self.path = path
        self.config = toml.load(path)
        self._parse_config()

    def _parse_config(self):
        """Parse and validate the configuration."""
        # Get global settings
        self.address = self.config.get('address', 'localhost')
        self.port = int(self.config.get('port', 4455))
        self.field = self.config.get('field', 'sender')
        self.default_limit = self.config.get('default_limit', '10/hour')
        self.storage = self.config.get('storage', 'memory://')
        self.strategy = self.config.get('strategy', 'fixed-window')

        # Parse per-field limits
        self.limits = {}
        if 'limits' in self.config:
            for key, value in self.config['limits'].items():
                self.limits[key] = value

    def get_limit(self, value):
        """
        Get limit and period for a specific value (e.g., email address).
        Returns {'limit': int, 'period': int} or None if not found.
        """
        return self.limits.get(value)

    def __repr__(self):
        return (f"TomlConfig(address={self.address}, port={self.port}, "
                f"field={self.field}, default_limit={self.default_limit}, "
                f"storage={self.storage}, strategy={self.strategy}, limits={len(self.limits)})")