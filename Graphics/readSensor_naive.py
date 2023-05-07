#readSensor_naive.py

from threading import Thread
import serial, time, io
import struct
import numpy as np
import pandas as pd
import os


class SerialRead:
    def __init__(self, serialPort='COM4', serialBaud=115200, dataNumBytes=2, numParams=6):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numParams = numParams
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
        # self.csvData = []

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4, dsrdtr=True)

            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
            exit()


    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)


    # def getSerialData(self):
    #     privateData = self.rawData[:]
    #     for i in range(self.numParams):
    #         data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
    #         value,  = struct.unpack(self.dataType, data)
    #         if i == 0:
    #             value = ((value * 0.00875) - 0.464874541896) / 180.0 * np.pi
    #         elif i == 1:
    #             value = ((value * 0.00875) - 9.04805461852) / 180.0 * np.pi
    #         elif i == 2:
    #             value = ((value * 0.00875) + 0.23642053973) / 180.0 * np.pi
    #         elif i == 3:
    #             value = (value * 0.061) - 48.9882695319
    #         elif i == 4:
    #             value = (value * 0.061) - 58.9882695319
    #         elif i == 5:
    #             value = (value * 0.061) - 75.9732905214
    #         elif i == 6:
    #             value = value * 0.080
    #         elif i == 7:
    #             value = value * 0.080
    #         elif i == 8:
    #             value = value * 0.080
    #         self.data[i] = value
    #     return self.data
    
    def getSerialData(self):
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
        return self.data


    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True
            #print(self.rawData)


    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/Aneesh/Desktop/data.csv')