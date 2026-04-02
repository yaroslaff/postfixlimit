import socketserver
import argparse

from ..policyhandler import PolicyHandler
from ..config import TomlConfig 
from ..limiter import Limiter

def get_args():
    def_port = 4455
    def_addr = "localhost"
    def_config = "/etc/postfixlimit.conf"
    parser = argparse.ArgumentParser("Simple Postfix Limiter (policy service)")
    parser.add_argument("--port", "-p", type=int, default=def_port,
                        help=f"Listen this port (def: {def_port})")
    parser.add_argument("--address", "-a", type=str, default=def_addr,
                        help=f"Listen this address (def: {def_addr})")
    parser.add_argument("--config", "-c", type=str, default=def_config,
                        help=f"Read this config (def: {def_config})")
    parser.add_argument("--daemon", "-d", action='store_true', default=False,
                        help=f"Run as daemon")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
                        help="Verbosity level: 0=warning, 1=info, 2=debug+all attrs (default 1)")
    parser.add_argument("-l", "--log", dest="log_file", default=None,
                        help="Log output file path (default=stderr)")

    return parser.parse_args()


def main():
    args = get_args()

    print(f"Loading config from {args.config}")
    config = TomlConfig(args.config)
    print(config)

    limiter = Limiter(config)
    limiter.dump()

    PolicyHandler.configure_logger(log_file=args.log_file, verbosity=args.verbosity)
    PolicyHandler.configure_limiter(limiter)
    try:
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        server = socketserver.ThreadingTCPServer((args.address, args.port), PolicyHandler)
    except OSError as e:
        print(f"Error starting server on {args.address}:{args.port}: {e}")
        return
    
    # server.allow_reuse_address = True
    print(f"Postfix policy server listening on {args.address}:{args.port} (verbosity={args.verbosity}, log_file={args.log_file})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        # server.shutdown()
        server.server_close()

if __name__ == '__main__':
    main()