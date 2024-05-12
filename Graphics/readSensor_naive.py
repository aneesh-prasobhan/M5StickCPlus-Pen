#readSensor_naive.py

from threading import Thread
import serial, time, io
import struct
import numpy as np
import pandas as pd
import os
import threading
import queue

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
        self.process_ble_count = 0 
        self.process_serial_count = 0
        self.dataQueue = queue.Queue()
        self.lock = threading.Lock()
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
        self.ble_thread = threading.Thread(target=run_ble, daemon=True)
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
        with self.lock:
            if len(data) == self.dataNumBytes * self.numParams:
                self.dataQueue.put(data)

    def parse_data(self, data):
        self.data = np.zeros(self.numParams)
        for i in range(self.numParams - 1):
            start = i * self.dataNumBytes
            end = start + self.dataNumBytes
            value, = struct.unpack('<h', data[start:end])
            if i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:  # Scaling for sensor values
                value = value / 100.0
            self.data[i] = value
        button_status = data[-2]  # Assume button status is at the second to last byte
        self.data[-1] = button_status  # No scaling for button status
        self.process_ble_count += 1
        # print(f"BLE processed {self.process_ble_count} times")
        # print(f"Print inside Parsed data: {self.data}")



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
        if enableBLE:
            if enableBLE:
                try:
                    # Wait for data to be available in the queue
                    raw_data = self.dataQueue.get(timeout=1)
                    self.parse_data(raw_data)
                except queue.Empty:
                    pass
            return self.data
        else:
            privateData = self.rawData[:]
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
                   # A custom counter to count the notifications received
            self.process_serial_count += 1
            print(f"Serial processed {self.process_serial_count} times")
            return self.data


    def backgroundThread(self):
        if not enableBLE:
            time.sleep(1.0)  # give some buffer time for retrieving data
            self.serialConnection.reset_input_buffer()
            while self.isRun:
                self.serialConnection.readinto(self.rawData)
                self.isReceiving = True
                # self.parse_data(self.rawData)


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