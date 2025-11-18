# Zebra Label Printer

This project provides a Python interface for connecting to Zebra printers and sending ZPL (Zebra Programming Language) labels for printing. It includes functionality for fetching article data from an API, generating ZPL labels, and managing the connection to the printer.

## Project Structure

```
zebra-label-printer
├── src
│   ├── printer
│   │   ├── __init__.py
│   │   ├── connector.py
│   │   └── usb_socket.py
│   ├── request.py
│   └── send_labels.py
├── tests
│   └── test_send_labels.py
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/axelclaudiom/zebra-label-printer.git
cd zebra-label-printer
pip install -r requirements.txt
```

## Usage

1. **Fetch Data and Generate Labels**: Use the `send_labels.py` script to fetch article data and generate ZPL labels. You can specify the article code and the number of labels to print.

   Example command:
   ```bash
   python src/send_labels.py -c BOR0003 -n 5
   ```

2. **Connect to the Printer**: The `ZebraPrinterConnector` class in `connector.py` manages the connection to the printer. Ensure your printer is connected via USB and recognized by your system.

3. **Testing**: Unit tests are provided in the `tests` directory. Run the tests to ensure everything is functioning correctly.

   Example command:
   ```bash
   pytest tests/test_send_labels.py
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.