#!/usr/bin/env python3
import argparse
import logging
from open_lisa.api.api import OpenLISA
from open_lisa.config.config import load_config
from open_lisa.protocol.rs232configuration import RS232Configuration
from open_lisa.tests.utils import reset_databases


def parse_config_params():
    """ Parse env variables to find program config params
    Function that search and parse program configuration parameters in the
    program environment variables. If at least one of the config parameters
    is not found a KeyError exception is thrown. If a parameter could not
    be parsed, a ValueError is thrown. If parsing succeeded, the function
    returns a map with the env variables
    """
    parser = argparse.ArgumentParser("Optional app description")
    parser.add_argument('--env', required=True,
                        help='Environment value determines Open LISA configuration file', choices=['dev', 'test', 'production'], default='dev')
    parser.add_argument('--mode', required=True,
                        help='SERIAL or TCP', choices=['SERIAL', 'TCP'])
    parser.add_argument(
        '--rs_232_port', help='RS232 connection port, i.e. COM3')
    parser.add_argument('--tcp_port', type=int,
                        help='TCP Listening port, i.e. 8080')
    parser.add_argument('--rs_232_baudrate', type=int,
                        help='Baudrate of RS232 connection, i.e. 19200')
    parser.add_argument('--rs_232_timeout', type=int,
                        help='Timeout in seconds for RS232 connection reads')
    parser.add_argument('--log-level', required=True,
                        help='Environment value determines Open LISA configuration file',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO')

    args = parser.parse_args()
    if args.mode == "SERIAL" and args.rs_232_port is None:
        logging.error("Serial port must be specified in Serial mode")
        exit(1)
    if args.mode == "TCP" and args.tcp_port is None:
        logging.error("Port must be specified in TCP mode")
        exit(1)

    return parser.parse_args()


def initialize_log(level):
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s [OPEN_LISA_SERVER] %(levelname)-8s %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    args = parse_config_params()
    initialize_log(args.log_level)

    logging.info(
        "Configuring Open LISA Server for {} environment".format(args.env))
    if args.env == "test":
        logging.info(
            "Server running in test mode... resetting databases to seed value")
        reset_databases()
    load_config(env=args.env)

    rs232_config = RS232Configuration(
        args.rs_232_port, args.rs_232_baudrate, args.rs_232_timeout)

    open_lisa = OpenLISA(
        mode=args.mode,
        rs232_config=rs232_config,
        listening_port=args.tcp_port
    )
    open_lisa.start()


if __name__ == "__main__":
    main()
