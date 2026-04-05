import logging
import socketserver
import time

from .limiter import Limiter
from .config import Config
from .exceptions import LimitExceeded
from .singleton import Singleton

class PolicyHandler(socketserver.StreamRequestHandler):
    logger: logging.Logger = logging.getLogger("postfixlimit")

    @classmethod
    def configure_limiter(cls, limiter: Limiter):
        cls.limiter = limiter

    @classmethod
    def configure_config(cls, config: Config):
        cls.config = config

    def setup(self):
        super().setup()
        self.singleton = Singleton()

    @classmethod
    def configure_logger(cls, log_file=None, verbosity=1):
        level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}.get(verbosity, logging.INFO)
        logger = cls.logger
        logger.setLevel(level)

        # Clear existing handlers added during reconfiguration
        for h in list(logger.handlers):
            logger.removeHandler(h)

        if log_file:
            handler = logging.FileHandler(log_file)
        else:
            handler = logging.StreamHandler()

        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)

        cls.logger = logger
        cls.verbosity = verbosity

    def handle(self):
        attrs = {}


        for line in self.rfile:
            line = line.decode().strip()
            if not line:
                self.singleton.counter += 1

                if self.verbosity >= 2:
                    self.logger.info(f"all attrs: {attrs}")
                action = self.check_policy(attrs)
                self.logger.info(f"MESSAGE {attrs.get('sender')} > {attrs.get('recipient')}" \
                                 f" (SASL:{attrs.get('sasl_username')!r} client:{attrs.get('client_address')!r} sz:{attrs.get('size')}): {action}")
                self.wfile.write(f"action={action}\n\n".encode())
                attrs = {}

                if self.config.dump_period > 0 and time.time() >= self.singleton.last_dump + self.config.dump_period:
                    self.singleton.last_dump = time.time()
                    self.limiter.dump()

            elif "=" in line:
                k, v = line.split("=", 1)
                attrs[k] = v
                
    def check_policy(self, attrs):
        sender = attrs.get("sender", "")
        size = int(attrs.get("size", 0))

        self.logger.debug(f"check_policy: sender={sender!r}, size={size}")

        try:
            self.limiter.check(sender)
            return "DUNNO"
        except LimitExceeded as e:
            # not allowed
            return e.postfix_response()
        

