import socket
import struct

# TODO: Duplicado en server y SDK, ver de usar uno en comun
# Source: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
class MessageProtocol:
  def __init__(self, socket):
    self._socket = socket

  def __del__(self):
    self._socket.shutdown(socket.SHUT_RDWR)
    self._socket.close()

  def send_msg(self, msg):
    msg = msg.encode()
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    self._socket.sendall(msg)

  def receive_msg(self):
    # Read message length and unpack it into an integer
    raw_msglen = self.__recvall(4)
    if not raw_msglen:
      raise ConnectionResetError
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return self.__recvall(msglen).decode()

  def __recvall(self, n):
    # Helper function to recv n bytes or raise ConnectionResetError if EOF is hit
    data = bytearray()
    while len(data) < n:
      packet = self._socket.recv(n - len(data))
      if not packet:
        raise ConnectionResetError
      data.extend(packet)
    return data