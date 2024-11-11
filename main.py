import csv
import os
import threading
import time
from datetime import datetime
import logging
import psutil
import ftplib
from pypsexec.client import Client
import socket
import pandas as pd
from typing import Dict, List, Optional
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

class SystemMonitor:
    def __init__(self, ip: str, username: str, password: str, monitoring_duration: int = 10800):
        """
        Initialize the system monitor

        Args:
            ip: Target machine IP
            username: Windows username
            password: Windows password
            monitoring_duration: Duration in seconds (default 3 hours)
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.hostname = None
        self.monitoring_duration = monitoring_duration
        self.sampling_interval = 600  # 10 minutes in seconds
        self.data_queue = queue.Queue()
        self.stop_flag = threading.Event()

    def __str__(self):
        """Return a string representation of the SystemMonitor object"""
        return f"SystemMonitor(ip='{self.ip}', username='{self.username}', password='{self.password}', monitoring_duration={self.monitoring_duration}, sampling_interval={self.sampling_interval})"

    def connect_to_machine(self) -> bool:
        """Establish connection to remote machine using psexec"""
        try:
            self.client = Client(
                self.ip,
                username=self.username,
                password=self.password,
                encrypt=True
            )
            # Get hostname
            self.hostname = socket.gethostbyaddr(self.ip)[0]
            logging.info(f"Successfully connected to {self.ip} ({self.hostname})")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to {self.ip}: {str(e)}")
            return False

    def get_system_metrics(self) -> Dict:
        """Collect system metrics from remote machine"""
        try:
            metrics = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv
            }
            return metrics
        except Exception as e:
            logging.error(f"Error collecting metrics: {str(e)}")
            return None

    def monitoring_worker(self):
        """Worker thread for continuous monitoring"""
        samples = []
        start_time = time.time()

        while not self.stop_flag.is_set() and \
                (time.time() - start_time) < self.monitoring_duration:

            metrics = self.get_system_metrics()
            if metrics:
                samples.append(metrics)
                self.data_queue.put(metrics)

            time.sleep(self.sampling_interval)

        # Calculate averages
        if samples:
            avg_metrics = {
                'timestamp': 'AVERAGE',
                'cpu_percent': sum(s['cpu_percent'] for s in samples) / len(samples),
                'memory_percent': sum(s['memory_percent'] for s in samples) / len(samples),
                'disk_percent': sum(s['disk_percent'] for s in samples) / len(samples),
                'network_bytes_sent': sum(s['network_bytes_sent'] for s in samples) / len(samples),
                'network_bytes_recv': sum(s['network_bytes_recv'] for s in samples) / len(samples)
            }
            self.data_queue.put(avg_metrics)

    def save_to_csv(self, data: List[Dict], filename: str):
        """Save metrics to CSV file"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logging.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving CSV: {str(e)}")
            return False

    def upload_to_ftp(self, local_file: str, ftp_host: str) -> bool:
        """Upload file to FTP server"""
        try:
            with ftplib.FTP(ftp_host) as ftp:
                ftp.login(user="username", passwd="password")
                with open(local_file, 'rb') as file:
                    ftp.storbinary(f'STOR {os.path.basename(local_file)}', file)
            logging.info(f"Successfully uploaded {local_file} to FTP server")
            return True
        except Exception as e:
            logging.error(f"FTP upload failed: {str(e)}")
            return False

def process_machines(input_csv: str, ftp_host: str):
    """Main function to process all machines from CSV"""
    try:
        df = pd.read_csv(input_csv)

        for index, row in df.iterrows():
            # print(row['IP'], row['username'], row['password'])
            monitor = SystemMonitor(
                row['IP'],
                row['username'],
                row['password']
            )
            print(monitor)
            # Try to connect
            connection_success = monitor.connect_to_machine()
            df.at[index, 'is_connected_succeed'] = connection_success

            if connection_success:
                # Start monitoring in separate thread if connection succeed
                monitoring_thread = threading.Thread(
                    target=monitor.monitoring_worker
                )
                monitoring_thread.start()

                # Collect data for 3 hours
                data = []
                while monitoring_thread.is_alive():
                    try:
                        metrics = monitor.data_queue.get(timeout=1)
                        data.append(metrics)
                    except queue.Empty:
                        continue

                # Save to local CSV
                local_file = f"{os.path.expanduser('~/Desktop')}/{monitor.hostname}_metrics.csv"
                if monitor.save_to_csv(data, local_file):

                    # Upload to FTP
                    if monitor.upload_to_ftp(local_file, ftp_host):
                        # Delete local file
                        try:
                            os.remove(local_file)
                            df.at[index, 'is_file_deleted'] = True
                            logging.info(f"Deleted local file: {local_file}")
                        except Exception as e:
                            logging.error(f"Error deleting file: {str(e)}")
                            df.at[index, 'is_file_deleted'] = False

            # Update original CSV
            df.to_csv(input_csv, index=False)

    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")

if __name__ == '__main__':
    try:
        # Configuration
        INPUT_CSV = "machines.csv"
        FTP_HOST = "ftp.example.com"

        # Process all machines
        process_machines(INPUT_CSV, FTP_HOST)

    except KeyboardInterrupt:
        logging.info("Script terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

