import socketserver
import argparse

from ..policyhandler import PolicyHandler
from ..config import Config 
from ..limiter import Limiter

def get_args():
    def_config = "/etc/postfixlimit.conf"
    parser = argparse.ArgumentParser("Simple Postfix Limiter (policy service)")
    parser.add_argument("--port", "-p", type=int, default=None,
                        help=f"Listen this port")
    parser.add_argument("--address", "-a", type=str, default=None,
                        help=f"Listen this address")
    parser.add_argument("--config", "-c", type=str, default=def_config,
                        help=f"Read this config (def: {def_config})")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
                        help="Verbosity level: 0=warning, 1=info, 2=debug+all attrs (default 1)")
    parser.add_argument("--reset", type=str, metavar="KEY", help="Reset counters for this key (e.g., email address) and exit")

    return parser.parse_args()


def main():
    args = get_args()


    print(f"Loading config from {args.config}")
    config = Config(args.config)

    if args.port is not None:
        config.port = args.port
    if args.address is not None:
        config.address = args.address

    print(config)

    limiter = Limiter(config)
    limiter.dump()

    PolicyHandler.configure_config(config)
    PolicyHandler.configure_logger(log_file=config.log_file, verbosity=args.verbosity)
    PolicyHandler.configure_limiter(limiter)

    if args.reset:
        print(f"Resetting counters for {args.reset}")
        limiter.reset(args.reset)
        limiter.dump()
        return


    try:
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        server = socketserver.ThreadingTCPServer((config.address, config.port), PolicyHandler)
    except OSError as e:
        print(f"Error starting server on {config.address}:{config.port}: {e}")
        return
    
    # server.allow_reuse_address = True
    print(f"Postfix policy server listening on {config.address}:{config.port} (verbosity={args.verbosity}, log_file={config.log_file})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        # server.shutdown()
        server.server_close()

if __name__ == '__main__':
    main()