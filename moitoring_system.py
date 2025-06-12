import sys
import serial
import time
import re
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
import webbrowser 
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, QPushButton, QComboBox, QWidget, QMessageBox, QLineEdit, QProgressBar
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression
import serial.tools.list_ports

class MonitoringSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.comport = None

        self.setWindowTitle("SHIVAY Parameter Control & Monitoring")
        self.setGeometry(200, 200, 850, 550)

        self.main_layout = QVBoxLayout()

# buttons
        self.label = QLabel("Select COM Port")
        self.label.setStyleSheet("font-weight: bold; padding-left: 5px;")

        self.com_port_combo = QComboBox()
        self.refresh_com_ports()

        self.save_button = QPushButton("Select")
        self.save_button.clicked.connect(self.save_selected_port)

        self.test_button = QPushButton("Test Device Connection")
        self.test_button.clicked.connect(self.test_connection)

        self.signal_button = QPushButton("Check Signal Strength")
        self.signal_button.clicked.connect(self.check_signal_strength)

        self.network_button = QPushButton("Check Network") 
        self.network_button.clicked.connect(self.check_network)

        self.start_trip_button = QPushButton("Start Trip")
        self.start_trip_button.setStyleSheet("color: green; font-weight: 510; height: 100%; width: 150%;")
        self.start_trip_button.clicked.connect(self.change_start_button)
        self.start_trip_button.clicked.connect(self.start_trip)

        self.stop_trip_button = QPushButton("Stop Trip")
        self.stop_trip_button.setStyleSheet("color: red; font-weight: 500; height: 100%; width: 150%; ")
        self.stop_trip_button.clicked.connect(self.stop_trip)
        self.stop_trip_button.clicked.connect(self.change_stop_button)

        self.user_number = QLineEdit(self)
        self.user_number.setPlaceholderText("Enter phone number")
        phone_regex = QRegularExpression(r"^\+?\d{10,12}$")  
        phone_validator = QRegularExpressionValidator(phone_regex, self)
        self.user_number.setValidator(phone_validator)

        self.sms_button = QPushButton("Fetch Data") 
        self.sms_button.clicked.connect(self.check_unread_sms)

        self.fetch_info = QLabel("Please note: You can only fetch data if a trip is running")
        self.fetch_info.setStyleSheet("font-style: italic;  font-weight: 600;  opacity: .5; font-size: 12px") 

        self.plot_temp = QPushButton("Plot Temperature") 
        self.plot_temp.clicked.connect(self.plot_current_trip)

        self.plot_hum = QPushButton("Plot Humidity") 
        self.plot_hum.clicked.connect(self.plot_current_trip)

        self.map_button = QPushButton("Show Latest Location")
        self.map_button.clicked.connect(self.show_latest_location)

        self.plot_info = QLabel("Please note: You can only plot data if a trip is running")
        self.plot_info.setStyleSheet("font-style: italic;  font-weight: 600;  opacity: .5; font-size: 12px") 
     
#layout1
        self.halftoplayout = QHBoxLayout()
        self.halftoplayout.addWidget(self.com_port_combo)
        self.halftoplayout.addWidget(self.save_button)
        self.halftop_widget = QWidget()
        self.halftop_widget.setLayout(self.halftoplayout)

#layout 2
        topLayout = QVBoxLayout()
        topLayout.addWidget(self.label)
        topLayout.addWidget(self.halftop_widget)
        topLayout.addStretch(1) 

#main layout
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()

        self.main_layout = QGridLayout()
        self.main_layout.addLayout(topLayout, 0, 0, 1, 2)
        self.main_layout.addWidget(self.topLeftGroupBox, 1, 0)
        self.main_layout.addWidget(self.topRightGroupBox, 1, 1)
        self.main_layout.addWidget(self.bottomLeftGroupBox, 2, 0)
        self.main_layout.addWidget(self.bottomRightGroupBox, 2, 1)

        self.main_layout.setRowStretch(1, 1)
        self.main_layout.setRowStretch(2, 1)
        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 1)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("font-size: 15px;")

#layout3
    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Device Status/System Diagnostics")
        group1Layout = QVBoxLayout()
        group1Layout.addStretch(1)
        group1Layout.addWidget(self.test_button)
        group1Layout.addWidget(self.signal_button)
        group1Layout.addWidget(self.network_button)
        group1Layout.addStretch(1)
        self.topLeftGroupBox.setLayout(group1Layout)     

#layout4
    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("SMS Handler")
        group2Layout = QVBoxLayout()
        group2Layout.addStretch(1)
        group2Layout.addWidget(self.user_number)
        group2Layout.addWidget(self.sms_button)
        group2Layout.addWidget(self.fetch_info)
        group2Layout.addStretch(1)
        self.topRightGroupBox.setLayout(group2Layout)

#layout5
    def createBottomLeftTabWidget(self):
        self.bottomLeftGroupBox = QGroupBox("Journey Manager")
        group3Layout = QHBoxLayout()
        group3Layout.addStretch(1)            
        group3Layout.addWidget(self.start_trip_button)
        group3Layout.addStretch(1)
        group3Layout.addWidget(self.stop_trip_button)
        group3Layout.addStretch(1)
        self.bottomLeftGroupBox.setLayout(group3Layout) 

#layout6
    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Trip Insights/Visualization Tools")
        group4Layout = QVBoxLayout()
        group4Layout.addStretch(1)
        group4Layout.addWidget(self.plot_temp)
        group4Layout.addWidget(self.plot_hum)
        group4Layout.addWidget(self.map_button)
        group4Layout.addWidget(self.plot_info)
        group4Layout.addStretch(1)
        self.bottomRightGroupBox.setLayout(group4Layout)

#************GUI DESIGNING*****************
    def change_start_button(self):
        self.start_trip_button.setText("Trip Started!")
        self.start_trip_button.setStyleSheet("background-color: green; color: white; height: 100%; width: 150%;")
        self.start_trip_button.setEnabled(False)
    def change_stop_button(self):
        self.start_trip_button.setText("Start Trip")
        self.start_trip_button.setStyleSheet("color: green; font-weight: 510;")
        self.start_trip_button.setEnabled(True)

#************LOGIC DESIGNING***************
    def refresh_com_ports(self):
        self.com_port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_port_combo.addItem(port.device)

    def save_selected_port(self):
        selected_port = self.com_port_combo.currentText()
        if selected_port:
            self.comport = selected_port 
            QMessageBox.information(self, "Port Saved", f"Selected COM port: {selected_port} selected successfully.")
        else:
            QMessageBox.warning(self, "No Port Selected", "Please select a COM port.")

    def test_connection(self):
        if not self.comport:
            QMessageBox.warning(self, "No Port Saved", "Please save a COM port first.")
            return
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            if self.send_at_command(ser, 'AT'):
                QMessageBox.information(self, "Test Successful", "GSM Module is connected successfully.")
            else:
                QMessageBox.warning(self, "Test Failed", "No response from the module. Is it powered on?")
                ser.close()
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def send_at_command(self, ser, command, expected_response="OK"):
        ser.write((command + '\r\n').encode())
        time.sleep(2)
        response = ser.read_all().decode()
        print(f"Sent: {command}")
        print(f"Response: {response.strip()}")
        return expected_response in response

    def check_signal_strength(self):
        if not self.comport:
            QMessageBox.warning(self, "No Port Saved", "Please save a COM port first.")
            return
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CSQ\r\n".encode()) 
            time.sleep(2)
            response = ser.read_all().decode()
            print(f"Sent: AT+CSQ")
            print(f"Response: {response.strip()}")
            ser.close()

            if "+CSQ:" in response:
                try:
                    parts = response.split(",")[0].split() 
                    signal_strength = int(parts[-1]) 
                    if signal_strength <= 10:
                        QMessageBox.warning(self, "Weak Signal", f"Signal strength is weak (+CSQ: {signal_strength},0).")
                    else:
                        QMessageBox.information(self, "Signal Strength", f"Signal strength is good (+CSQ: {signal_strength},0).")
                except (ValueError, IndexError):
                    QMessageBox.critical(self, "Error", "Failed to parse signal strength response.")
            else:
                QMessageBox.warning(self, "Invalid Response", "No valid signal strength data received.")
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def check_network(self):
        if not self.comport:
            QMessageBox.warning(self, "No Port Saved", "Please save a COM port first.")
            return
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CREG?\r\n".encode())
            time.sleep(2)
            response = ser.read_all().decode()
            ser.close()

            if "0,1" in response:
                QMessageBox.information(self, "Network Status", "Network is registered.")
            else:
                self.automate_network_connection()
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def automate_network_connection(self):
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CREG=1\r\n".encode())
            time.sleep(2)
            ser.write("AT+COPS=0\r\n".encode())
            time.sleep(2)
            response = ser.read_all().decode()
            ser.close()

            if "OK" not in response:
                QMessageBox.critical(self, "Failed to Connect to Network", "Cannot Find and Connect to a Network.")
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def set_text_mode(self):
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CMGF=1\r\n".encode()) 
            time.sleep(2)
            response = ser.read_all().decode()
            print(f"Sent: AT+CMGF=1")
            print(f"Response: {response.strip()}")
            ser.close()

            if "OK" in response:
                QMessageBox.information(self, "Text Mode", "Module is in text mode.")
            else:
                QMessageBox.warning(self, "Text Mode Failed", "Failed to set text mode.")
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")  

    def set_storage(self):
        try:
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CPMS=\"SM\",\"SM\",\"SM\"\r\n".encode()) 
            time.sleep(2)
            response = ser.read_all().decode()
            print(f"Sent: AT+CPMS=\"SM\",\"SM\",\"SM\"")
            print(f"Response: {response.strip()}")
            ser.close()

            if "OK" in response:
                QMessageBox.information(self, "Storage Setting", "Storage successfully set to SIM memory.")
            else:
                QMessageBox.warning(self, "Storage Setting Failed", "Failed to set storage.")
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def check_unread_sms(self):
        if not self.comport:
            QMessageBox.warning(self, "No Port Saved", "Please save a COM port first.")
            return
        if len(self.user_number.text())<10:
            QMessageBox.warning(self, "Incorrect number", "Please put a proper 10-digit number.")
            return
        try:
            self.set_text_mode()
            self.set_storage()
            ser = serial.Serial(self.comport, 9600, timeout=2)
            time.sleep(2)
            ser.write("AT+CMGL=\"REC UNREAD\"\r\n".encode()) 
            time.sleep(2)
            response = ser.read_all().decode()
            print(f"Sent: AT+CMGL=\"REC UNREAD\"")
            print(f"Response: {response.strip()}")
            ser.close()

            pattern = re.compile(rf'\+CMGL: \d+,.+,"{self.user_number}",,"([\d/,:]+)".*?\n(.*?)\r', re.DOTALL)
            match = pattern.search(response)

            if match:
                timestamp_str = match.group(1).strip()
                sms_content = match.group(2).strip()
                print(f"Received SMS: {sms_content} at {timestamp_str}")

                timestamp = datetime.strptime(timestamp_str, "%y/%m/%d,%H:%M:%S+%f")

                data_pattern = re.compile(r'ST:(\d+),SH:(\d+),RT:(\d+),RH:(\d+),https://www\.google\.com/maps/place/([\d.]+),([\d.]+)')
                data_match = data_pattern.search(sms_content)

                if data_match:
                    ST, SH, RT, RH, lat, lon = data_match.groups()
                    self.store_sms_in_db(timestamp, ST, SH, RT, RH, lat, lon)
                    QMessageBox.information(self, "Data Fetched", f"New data fetched via SMS from {self.user_number.text()} has been stored in the database.")
                else:
                    QMessageBox.warning(self, "Parsing Error", "Failed to parse SMS content.")
            else:
                QMessageBox.information(self, "No New Data", f"No new unread data could be fetched via SMS from {self.user_number.text()}.")

        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Error opening port {self.comport}: {e}")

    def start_trip(self):
        try:
            connection = mysql.connector.connect(
            user="root",
            password="mysql123",
            host="localhost",
            database="monitoring_sys"
            )
            cursor = connection.cursor()
            cursor.execute("INSERT INTO trips (start_time) VALUES (NOW())")
            self.current_trip_id = cursor.lastrowid 
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "Trip Started", f"New trip started with ID: {self.current_trip_id}")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

    def stop_trip(self):
        if not self.current_trip_id:  
            QMessageBox.warning(self, "No Trip", "No active trip to stop.")
            return
        try:
            connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql123",
            database="monitoring_sys"
            )
            cursor = connection.cursor()
            cursor.execute("UPDATE trips SET end_time = NOW() WHERE trip_id = %s", (self.current_trip_id,))
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "Trip Stopped", f"Trip ID {self.current_trip_id} has been stopped.")
            self.current_trip_id = None
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

    def store_sms_in_db(self, timestamp, ST, SH, RT, RH, lat, lon):
        if not self.current_trip_id:
            QMessageBox.warning(self, "No Active Trip", "Cannot store data without an active trip.")
            return
        try:
            connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql123",
            database="monitoring_sys"
            )
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
            smsID INT AUTO_INCREMENT PRIMARY KEY,
            trip_id INT,
            Timestamp DATETIME,
            ST INT,
            SH INT,
            RT INT,
            RH INT,
            Latitude FLOAT,
            Longitude FLOAT,
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
            )"""
            )
            cursor.execute("""
            INSERT INTO parameters (trip_id, Timestamp, ST, SH, RT, RH, Latitude, Longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.current_trip_id, timestamp, ST, SH, RT, RH, lat, lon))
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

    def plot_temperature_current_trip(self):
        if not self.current_trip_id:
            QMessageBox.warning(self, "No Trip", "No active trip to plot.")
            return
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="insiya",
                password="Insiya@123",
                database="monitoring_sys"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT Timestamp, RT FROM parameters WHERE trip_id = %s ORDER BY Timestamp", (self.current_trip_id,))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()

            if not rows:
                QMessageBox.warning(self, "No Data", "No temperature data found for the current trip.")
                return

            timestamps, RT_values = zip(*rows)

            plt.figure(figsize=(10, 5))
            plt.plot(timestamps, RT_values, marker='o', linestyle='-', color='r', label='Temperature (RT)')
            plt.xlabel("Time")
            plt.ylabel("Temperature (°C)")
            plt.title("Temperature Over Current Trip")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

        def plot_humidity_current_trip(self):
            if not self.current_trip_id:
                QMessageBox.warning(self, "No Trip", "No active trip to plot.")
                return
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="insiya",
                    password="Insiya@123",
                    database="monitoring_sys"
                )
                cursor = connection.cursor()
                cursor.execute("SELECT Timestamp, RH FROM parameters WHERE trip_id = %s ORDER BY Timestamp", (self.current_trip_id,))
                rows = cursor.fetchall()
                cursor.close()
                connection.close()

                if not rows:
                    QMessageBox.warning(self, "No Data", "No humidity data found for the current trip.")
                    return

                timestamps, RH_values = zip(*rows)

                plt.figure(figsize=(10, 5))
                plt.plot(timestamps, RH_values, marker='o', linestyle='-', color='b', label='Humidity (RH)')
                plt.xlabel("Time")
                plt.ylabel("Humidity (%)")
                plt.title("Humidity Over Current Trip")
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Database Error", f"Error: {err}")

          
    def show_latest_location(self):
        try:
            connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql123",
            database="monitoring_sys"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT Latitude, Longitude FROM parameters ORDER BY Timestamp DESC LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                lat, lon = result
                url = f"https://www.google.com/maps/place/{lat},{lon}"
                webbrowser.open(url)
            else:
                QMessageBox.warning(self, "No Data", "No location data available.")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MonitoringSystem()
    window.show()
    sys.exit(app.exec_())
