import socket

class ZebraUSBSocket:
    """Class to handle USB communication with the Zebra printer."""

    def __init__(self, device_path):
        self.device_path = device_path
        self.sock = None

    def open(self):
        """Open a USB socket connection to the printer."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.device_path, 9100))  # Assuming the printer listens on port 9100
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the printer at {self.device_path}: {e}")

    def send(self, data):
        """Send data to the printer."""
        if self.sock is None:
            raise ConnectionError("Socket is not open. Please open the socket before sending data.")
        try:
            self.sock.sendall(data.encode('utf-8'))
        except Exception as e:
            raise IOError(f"Failed to send data to the printer: {e}")

    def receive(self, buffer_size=1024):
        """Receive data from the printer."""
        if self.sock is None:
            raise ConnectionError("Socket is not open. Please open the socket before receiving data.")
        try:
            return self.sock.recv(buffer_size).decode('utf-8')
        except Exception as e:
            raise IOError(f"Failed to receive data from the printer: {e}")

    def close(self):
        """Close the USB socket connection."""
        if self.sock:
            self.sock.close()
            self.sock = None