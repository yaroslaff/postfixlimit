import toml
import sys

class TomlConfig:
    def __init__(self, path):
        self.path = path
        self.config = toml.load(path)
        self._parse_config()

    def validate_config(self):
        try:
            assert self.action in ['DEFER', 'REJECT'], "Action must be either DEFER or REJECT"
            assert self.strategy in ['fixed-window'], "Currently only fixed-window strategy is supported"
            assert self.field in ['sender', 'client_address', 'sasl_username'], "Field must be one of sender, client_address, sasl_username"
        except AssertionError as e:
            print(f"Configuration error: {e}")    
            sys.exit(1)

    def _parse_config(self):
        """Parse and validate the configuration."""
        # Get global settings
        self.address = self.config.get('address', 'localhost')
        self.port = int(self.config.get('port', 4455))
        self.field = self.config.get('field', 'sender')
        self.default_limit = self.config.get('default_limit', '10/hour')
        self.storage = self.config.get('storage', 'memory://')
        self.strategy = self.config.get('strategy', 'fixed-window')
        self.action = self.config.get('action', 'DEFER')
        self.action_text = self.config.get('action_text', '4.5.3 Limit ({limit}) exceeded for {field}={key}')
        self.dump_period = int(self.config.get('dump_period', 3600))
        self.dump_file = self.config.get('dumpfile', None)
        self.log_file = self.config.get('logfile', None)

        self.validate_config()

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
                f"storage={self.storage}, strategy={self.strategy}, limits={len(self.limits)}), "
                f"log={self.log_file}, dump_file={self.dump_file}, dump_period={self.dump_period}")