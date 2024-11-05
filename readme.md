# Windows Fleet Metrics Collector

A Python-based tool for automated system metrics collection across multiple Windows machines. This tool connects to remote Windows systems using PsExec, collects system performance metrics, and centralizes the data through FTP storage.

## Features

- 🖥️ **Remote Windows Monitoring**: Connects to multiple Windows 10 machines using PsExec
- 📊 **System Metrics Collection**: Captures CPU, memory, disk, and network usage
- ⏱️ **Scheduled Sampling**: Takes measurements every 10 minutes over a 3-hour period
- 📈 **Performance Analysis**: Calculates and stores average metrics
- 🔄 **Concurrent Processing**: Uses threading for efficient multi-system monitoring
- 📁 **Centralized Storage**: Automatically uploads results to FTP server
- 🔒 **Secure Implementation**: Includes error handling and secure credential management

## Requirements

- Python 3.7+
- Windows 10 target systems
- Network access to target systems
- FTP server for data storage

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Windows-Fleet-Metrics-Collector.git
cd Windows-Fleet-Metrics-Collector

# Install required packages
pip install -r requirements.txt
```

## Usage

1. Create a CSV file with target system details:

```csv
IP address,username,password,is connected succeed,is file deleted
192.168.1.100,admin,password,,
192.168.1.101,admin,password,,
```

2. Update FTP server settings in `config.py` (not included in repo):

```python
FTP_HOST = "your.ftp.server"
FTP_USER = "username"
FTP_PASS = "password"
```

3. Run the collector:

```bash
python fleet_metrics.py
```

## Project Structure

```
Windows-Fleet-Metrics-Collector/
├── fleet_metrics.py      # Main script
├── requirements.txt      # Package dependencies
├── config.py.example    # Example configuration file
├── README.md           # This file
└── logs/              # Log files directory
```

## Configuration

The tool can be configured through the following parameters:

- Monitoring duration (default: 3 hours)
- Sampling interval (default: 10 minutes)
- Maximum concurrent connections (default: 5)
- Log level and format

## Output

For each monitored system, the tool generates:

1. A CSV file containing:

   - Timestamp
   - CPU usage
   - Memory usage
   - Disk usage
   - Network usage
   - Average metrics (appended after collection)

2. Status updates in the input CSV:
   - Connection success/failure
   - File transfer status

## Security Considerations

- Credentials should be stored securely
- Network access should be properly configured
- Windows firewall settings may need adjustment
- Use service accounts with minimum required permissions

## Error Handling

The tool includes comprehensive error handling for:

- Connection failures
- Network interruptions
- Insufficient permissions
- Resource constraints
- FTP upload issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

David E

## Acknowledgments

- PsExec for Windows remote execution
- Python community for excellent libraries
