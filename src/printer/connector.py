class ZebraPrinterConnector:
    def __init__(self, usb_socket):
        self.usb_socket = usb_socket

    def connect(self):
        """Establish a connection to the Zebra printer."""
        try:
            self.usb_socket.open()
            print("Connected to Zebra printer.")
        except Exception as e:
            print(f"Error connecting to printer: {e}")

    def send_label(self, zpl_data):
        """Send ZPL data to the printer."""
        try:
            self.usb_socket.send(zpl_data)
            print("Label sent to printer.")
        except Exception as e:
            print(f"Error sending label: {e}")

    def disconnect(self):
        """Close the connection to the printer."""
        try:
            self.usb_socket.close()
            print("Disconnected from Zebra printer.")
        except Exception as e:
            print(f"Error disconnecting from printer: {e}")