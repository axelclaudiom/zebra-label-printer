import unittest
from unittest.mock import patch, MagicMock
from src.send_labels import send_labels

class TestSendLabels(unittest.TestCase):

    @patch('src.request.fetch_data')
    @patch('src.printer.connector.ZebraPrinterConnector')
    def test_send_labels_success(self, MockZebraPrinterConnector, MockFetchData):
        # Arrange
        mock_printer = MockZebraPrinterConnector.return_value
        mock_printer.send_data = MagicMock()
        MockFetchData.return_value = {'COD_STA11': 'BOR0003', 'DESCRIPCIO': 'Test Item'}

        # Act
        result = send_labels('BOR0003', 1)

        # Assert
        self.assertTrue(mock_printer.send_data.called)
        self.assertEqual(result, "Labels sent successfully.")

    @patch('src.request.fetch_data')
    @patch('src.printer.connector.ZebraPrinterConnector')
    def test_send_labels_no_item(self, MockZebraPrinterConnector, MockFetchData):
        # Arrange
        MockFetchData.return_value = {}

        # Act
        result = send_labels('BOR0003', 1)

        # Assert
        self.assertEqual(result, "No item found for codigo: BOR0003.")

    @patch('src.request.fetch_data')
    @patch('src.printer.connector.ZebraPrinterConnector')
    def test_send_labels_printer_error(self, MockZebraPrinterConnector, MockFetchData):
        # Arrange
        mock_printer = MockZebraPrinterConnector.return_value
        mock_printer.send_data.side_effect = Exception("Printer error")
        MockFetchData.return_value = {'COD_STA11': 'BOR0003', 'DESCRIPCIO': 'Test Item'}

        # Act
        result = send_labels('BOR0003', 1)

        # Assert
        self.assertEqual(result, "Error sending labels to printer: Printer error.")

if __name__ == '__main__':
    unittest.main()