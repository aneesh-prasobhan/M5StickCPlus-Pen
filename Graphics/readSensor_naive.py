#readSensor_naive.py

from threading import Thread
import serial, time, io
import struct
import numpy as np
import pandas as pd
import os

# BLE module import
from ble_communication import BLECommunication, notification_handler
import asyncio

enableBLE = 1  # Set to 1 for BLE, 0 for serial

class SerialRead:
    def __init__(self, serialPort='COM4', serialBaud=115200, dataNumBytes=2, numParams=6, ble_address="E8:9F:6D:09:2E:8A"):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numParams = numParams
        self.ble_address = ble_address
        self.rawData = bytearray(numParams * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float
        self.data = np.zeros(numParams)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.data_buffer = bytearray()
        self.button_status_received = False
        self.sensor_data_received = False
        self.process_count = 0 
        # self.csvData = []

        if enableBLE:
            self.init_ble()
        else:
            self.init_serial()
    
    
    def init_ble(self):
        def run_ble():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.ble_comm = BLECommunication(self.ble_address, '4fafc201-1fb5-459e-8fcc-c5c9c331914b', 'beb5483e-36e1-4688-b7f5-ea07361b26a8')
            loop.run_until_complete(self.ble_comm.connect())
            loop.run_until_complete(self.ble_comm.start_notify(self.handle_data))
            loop.run_forever()
        self.ble_thread = Thread(target=run_ble, daemon=True)
        self.ble_thread.start()

    def init_serial(self):
        try:
            self.serialConnection = serial.Serial(self.port, self.baud, timeout=4, dsrdtr=True, rtscts=False)
            self.serialConnection.reset_input_buffer()
            print('Connected to ' + str(self.port) + ' at ' + str(self.baud) + ' BAUD.')
        except Exception as e:
            print("Failed to connect with " + str(self.port) + ' at ' + str(self.baud) + ' BAUD. Error: ' + str(e))
            exit()

    def handle_data(self, sender, data):
        # print(f"Received BLE data: {data}")
        # Append new data to the buffer
        self.data_buffer += data  

        # Check if buffer has enough data for the sensor readings (data[0] to data[9])
        if not self.sensor_data_received and len(self.data_buffer) >= self.dataNumBytes * 10:
            self.sensor_data_received = True

        # Check if the button status has been received
        if not self.button_status_received and len(self.data_buffer) >= self.dataNumBytes * 11:
            self.button_status_received = True

        # If both sensor data and button status have been received, parse the complete data
        if self.sensor_data_received and self.button_status_received:
            self.parse_data(self.data_buffer[:self.dataNumBytes * 11])
            # Clear the buffer and reset flags
            self.data_buffer = bytearray()
            self.sensor_data_received = False
            self.button_status_received = False

    def parse_data(self, data):
        num_values = (len(data) - 2) // self.dataNumBytes  # Adjust for 10 sensor readings, last 2 bytes for button
        formatted_data = []
        for i in range(num_values):
            value, = struct.unpack('<h', data[i*self.dataNumBytes:(i+1)*self.dataNumBytes])
            formatted_data.append(value)
        
        # Correctly handle the button status
        # Assuming button status is sent as first byte of the last two bytes, ignoring the second byte
        button_status, = struct.unpack('<h', data[-2:])  # interprets the full 2 bytes
        button_status = data[-2]  # directly take the first byte only, assuming little endian

        formatted_data.append(button_status)  # Append the button status correctly
        formatted_data = np.array(formatted_data) / 100.0  # Scale the data if necessary
        formatted_data[-1] *= 100  # Undo scaling for button status (last item)

        self.data = formatted_data
        # print(f"Parsed data: {self.data}")
        # A custom counter to count the notifications received
        self.process_count += 1
        print(f"Data processed {self.process_count} times")

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            if not enableBLE:
                while self.isReceiving != True:
                    time.sleep(0.1)
            else:
                return True
                    
    def getSerialData(self):
        privateData = self.rawData[:]
        if enableBLE:
            return self.data
        else:
            for i in range(self.numParams):
                data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
                value,  = struct.unpack(self.dataType, data)
                
                # Convert gyro values from int16_t to float (divide by 100, as it was multiplied by 100 in the M5StickC Plus code)
                if i in [0, 1, 2]:
                    value = value / 100.0
                
                # Convert accelerometer values from int16_t to float (divide by 100, as it was multiplied by 100 in the M5StickC Plus code)
                if i in [3, 4, 5]:
                    value = value / 100.0
                
                if i in [6, 7, 8]:
                    value = value / 100.0 
                            
                self.data[i] = value
            return self.data


    def backgroundThread(self):
        if not enableBLE:
            time.sleep(1.0)  # give some buffer time for retrieving data
            self.serialConnection.reset_input_buffer()
            while self.isRun:
                self.serialConnection.readinto(self.rawData)
                self.isReceiving = True
                self.parse_data(self.rawData)


    def close(self):        
        if enableBLE:
            asyncio.get_event_loop().run_until_complete(self.ble_comm.disconnect())
        
        else:
            self.serialConnection.dtr = True
            self.serialConnection.rts = False
            time.sleep(0.5)  # Give some time for states to settle
            self.isRun = False
            self.thread.join()
            self.serialConnection.close()
            print('Disconnected...')
            # df = pd.DataFrame(self.csvData)
            # df.to_csv('/home/Aneesh/Desktop/data.csv')