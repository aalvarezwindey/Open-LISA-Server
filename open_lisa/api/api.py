import serial
import socket
import traceback
import sys

from ..protocol.message_protocol_rs232 import MessageProtocolRS232
from ..protocol.message_protocol_tcp import MessageProtocolTCP
from ..protocol.server_protocol import *


MODE_SERIAL = 'SERIAL'
MODE_TCP = 'TCP'
MAX_CONCURRENT_CLIENTS = 1
RS232_EXPECTED_CLIENT_QUESTION = 'OPEN'
RS232_ANSWER_TO_CLIENT_QUESTION = 'LISA'


class OpenLISA:

    def __init__(self, mode, rs232_config, listening_port):
        self._rs232_connection = None
        self._server_protocol = None
        self._mode = mode
        self._rs232_config = rs232_config
        self._listening_port = listening_port
        self._server_socket = None
        self._instruments_repository = InstrumentRepository()
        self._shutdown_after_next_client_connection = False  # Do something better than this

    def start(self):
        while True:
            logging.info("Waiting for client connection...")
            if self._mode == MODE_SERIAL:
                self._server_protocol = self._rs232_wait_connection()
            elif self._mode == MODE_TCP:
                self._server_protocol = self._tcp_wait_connection()
            else:
                logging.error(
                    "OpenLisa started with invalid mode: {}".format(self._mode))
                exit(1)

            while True:
                try:
                    command = self._server_protocol.get_command()
                    logging.info(
                        "[OpenLISA][api][start] - command received: " + command)
                    if command == COMMAND_GET_INSTRUMENTS:
                        logging.debug(
                            "[OpenLISA][api][start] - getting instruments")
                        self._server_protocol.handle_get_instruments(
                            self._instruments_repository)
                    elif command == COMMAND_GET_INSTRUMENT:
                        logging.debug(
                            "[OpenLISA][api][start] - getting specific instrument")
                        self._server_protocol.handle_get_instrument(
                            self._instruments_repository)
                    elif command == COMMAND_CREATE_INSTRUMENT:
                        logging.debug(
                            "[OpenLISA][api][start] - creating new instrument")
                        self._server_protocol.handle_create_instrument(
                            self._instruments_repository)
                    elif command == COMMAND_UPDATE_INSTRUMENT:
                        logging.debug(
                            "[OpenLISA][api][start] - updating instrument")
                        self._server_protocol.handle_update_instrument(
                            self._instruments_repository)
                    elif command == COMMAND_DELETE_INSTRUMENT:
                        logging.debug(
                            "[OpenLISA][api][start] - deleting instrument")
                        self._server_protocol.handle_delete_instrument(
                            self._instruments_repository)
                    elif command == COMMAND_GET_INSTRUMENT_COMMANDS:
                        logging.debug(
                            "[OpenLISA][api][start] - getting instrument commands")
                        self._server_protocol.handle_get_instrument_commands(
                            self._instruments_repository)
                    elif command == COMMAND_VALIDATE_COMMAND:
                        logging.debug(
                            "[OpenLISA][api][start] - validating instrument command")
                        self._server_protocol.handle_validate_command(
                            self._instruments_repository)
                    elif command == COMMAND_SEND_COMMAND:
                        logging.debug(
                            "[OpenLISA][api][start] - sending command to instrument")
                        self._server_protocol.handle_send_command(
                            self._instruments_repository)
                    elif command == COMMAND_SEND_FILE:
                        logging.debug(
                            "[OpenLISA][api][start] - receiving file from client")
                        self._server_protocol.handle_send_file()
                    elif command == COMMAND_GET_FILE:
                        logging.debug(
                            "[OpenLISA][api][start] - sending file to client")
                        self._server_protocol.handle_get_file()
                    elif command == COMMAND_EXECUTE_BASH:
                        logging.debug(
                            "[OpenLISA][api][start] - executing bash command sending by client")
                        self._server_protocol.handle_execute_bash_command()
                    elif command == COMMAND_DISCONNECT:
                        logging.info(
                            "[OpenLISA][api][start] - client order disconnect")
                        # self._server_protocol.handle_disconnect_command()
                        break
                    elif command == COMMAND_RESET_DATABASES:
                        self._server_protocol.handle_reset_databases()
                    else:
                        logging.error(
                            "[OpenLISA][api][start] - unknown command '{}'".format(command))
                except ConnectionResetError as ex:
                    logging.info(
                        "[OpenLISA][api][start] - client socket disconnect {}".format(ex))
                    break
                except Exception as ex:
                    logging.error(
                        "[OpenLISA][api][start][FATAL_ERROR]: {}".format(ex))
                    traceback.print_exc()
                    break

            if self._shutdown_after_next_client_connection:
                break

    def _list_instruments(self):
        logging.debug(
            "* * * * * * * * * * Instruments List * * * * * * * * * *")
        for instrument in self._instruments_repository.get_all():
            logging.debug(instrument)
        logging.debug(
            "* * * * * * * * * * * * * * * * * * * * * * * * * * * * *")

    def _rs232_wait_connection(self):
        if not self._rs232_connection:
            self._rs232_create_connection()

        while True:
            logging.info("Waiting for RS232 client question...")
            client_question = self._rs232_connection.read(4)
            logging.info("Question received from client: {}".format(
                client_question.decode()))
            if RS232_EXPECTED_CLIENT_QUESTION == client_question.decode():
                logging.info(
                    "Question match with expected. Starting RS232 connection...")
                self._rs232_connection.write(
                    RS232_ANSWER_TO_CLIENT_QUESTION.encode('utf-8'))
                break
            else:
                logging.info(
                    "Question does not match the expected, still waiting for a client...")

        return ServerProtocol(MessageProtocolRS232(self._rs232_connection))

    def _rs232_create_connection(self):
        try:
            self._rs232_connection = serial.Serial(
                port=self._rs232_config.port,
                baudrate=self._rs232_config.baudrate,
                timeout=self._rs232_config.timeout)

            logging.info("Serial RS232 connection created at {} with baudrate of {}".format(
                self._rs232_config.port,
                self._rs232_config.baudrate
            ))

        except serial.SerialException:
            logging.error("Error on open serial connection on {}".format(
                self._rs232_config.port))
            traceback.print_exception(*sys.exc_info())
            exit(1)

        if not self._rs232_connection.is_open:
            self._rs232_connection.open()

    def _tcp_wait_connection(self):
        if not self._server_socket:
            self._server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind(('', self._listening_port))
            # Only handles one client
            self._server_socket.listen(MAX_CONCURRENT_CLIENTS - 1)

        logging.debug(
            "[OpenLISA][api][start] - TPC proceed to accept new connection")
        socket_connection, addr = self._server_socket.accept()
        logging.debug(
            '[OpenLISA][api][start] - TCP got connection from {}'.format(addr))

        return ServerProtocol(MessageProtocolTCP(socket_connection))
