import serial
import time
from crc import Calculator, Crc32
from cobs import cobs
from typing import Optional
import signal
import sys

CRC_SIZE = 4
COBS_BYTE = b'\x00'

class SerialCommunicator:
    def __init__(self, port_name: str, baudrate: int = 115200, timeout: int = 1, chunk_size: int = 256):
        """
        Initializes the SerialCommunicator object.

        Args:
            port_name (str): The name of the serial port.
            baudrate (int): The baud rate for the serial port communication.
            timeout (int): The timeout for serial communication.
            chunk_size (int): The size of each chunk to be sent.
        """
        self.port = serial.Serial(port_name, baudrate=baudrate, timeout=timeout)
        self.chunk_size = chunk_size - (CRC_SIZE + len(COBS_BYTE) + 1)
        self.data = self.read_data_from_file('commands.txt')
        self.offset = 0

    @staticmethod
    def read_data_from_file(file_path: str) -> bytes:
        """
        Reads data from a file and returns it as a bytes object.

        Args:
            file_path (str): The path to the file to read.

        Returns:
            bytes: The data read from the file.
        """
        with open(file_path, 'rb') as file:
            return file.read()

    def send_total_size(self) -> None:
        """
        Sends the total size of the data to the serial port.
        """
        size = len(self.data)
        print(f'Datasize: {size}')
        size_buffer = size.to_bytes(4, byteorder='little')
        print("Size buffer: " + ' '.join('{:02x}'.format(x) for x in size_buffer))
        encoded_size = cobs.encode(size_buffer) + COBS_BYTE
        print("Encoded size buffer: " + ' '.join('{:02x}'.format(x) for x in encoded_size))
        self.port.write(encoded_size)

    def send_next_chunk(self) -> None:
        """
        Sends the next chunk of data if available.
        """
        if self.offset < len(self.data):
            self.send_chunk(self.offset)
            self.offset += self.chunk_size
        else:
            print('All data sent')

    def send_chunk(self, offset: int) -> None:
        """
        Sends a chunk of data starting from the given offset.

        Args:
            offset (int): The starting point of the chunk to be sent.
        """
        end = min(offset + self.chunk_size, len(self.data))
        chunk = self.data[offset:end]
        calculator = Calculator(Crc32.CRC32)
        crc = calculator.checksum(chunk)
        crc_buffer = crc.to_bytes(4, byteorder='little')
        print("CRC: " + ' '.join('{:02x}'.format(x) for x in crc_buffer))
        packet = chunk + crc_buffer
        print("Packet: " + ' '.join('{:02x}'.format(x) for x in packet))
        encoded_packet = cobs.encode(packet) + COBS_BYTE
        self.wait_for_port()
        self.port.write(encoded_packet)
        print(f'Chunk sent, offset: {offset}, size {len(packet)}')

    def wait_for_port(self) -> None:
        """
        Waits until the serial port is available for writing.
        """
        while not self.port.writable():
            time.sleep(0.1)

    def read_decode(self, serial_data: serial.Serial) -> bytes:
        """
        Reads and decodes data from the serial port.

        Args:
            serial_data (serial.Serial): The serial port to read from.

        Returns:
            bytes: The decoded data.
        """
        zero_byte = COBS_BYTE
        raw_data = serial_data.read_until(zero_byte)
        print(raw_data)
        if len(raw_data) > 0:
            decode_str = raw_data[0:-1]
            return cobs.decode(decode_str)
        else:
            return zero_byte

    def read_response(self) -> None:
        """
        Reads responses from the serial port and acts accordingly.
        """
        while True:
            if self.port.in_waiting > 0:
                response = self.read_decode(self.port)
                print("Response: " + response.decode())
                if response == b'SIZE_ACK':
                    self.send_next_chunk()
                elif response == b'ACK':
                    self.send_next_chunk()
                else:
                    print(f'Unknown response: {response}')
            time.sleep(0.1)

def signal_handler(sig, frame):
    """
    Handles the signal for graceful termination.

    Args:
        sig: The signal number.
        frame: The current stack frame.
    """
    print('Exiting program...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    communicator = SerialCommunicator(port_name="/dev/rfcomm0")
    communicator.port.flushInput()
    communicator.send_total_size()
    communicator.read_response()
