from __future__ import print_function

from datetime import datetime
import sys
import time
from bluepy.btle import BTLEException
from bluepy.sensortag import SensorTag
import socket
from _thread import *

HOST = '127.0.0.1'
PORT = 9999

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def recv_data(client_socket) :
    while True :
        data = client_socket.recv(2048)

        print("recive : ",repr(data.decode()))


start_new_thread(recv_data, (client_socket,))
print ('>> Connect Server')


# configurations to be set accordingly
SENSORTAG_ADDRESS = "54:6C:0E:52:DC:BE"
#SENSORTAG_ADDRESS = "54:6C:0E:B4:44:83"

def enable_sensors(tag):
    """Enable sensors so that readings can be made."""
    tag.accelerometer.enable()
    tag.magnetometer.enable()
    tag.gyroscope.enable()
    
def disable_sensors(tag):
    """Disable sensors to improve battery life."""
    tag.accelerometer.disable()
    tag.magnetometer.disable()
    tag.gyroscope.disable()


def reconnect(tag):
    try:
        tag.connect(tag.deviceAddr, tag.addrType)

    except Exception as e:
        print("Unable to reconnect to SensorTag.")
        raise e



def main():
    print('Connecting to {}'.format(SENSORTAG_ADDRESS))
    tag = SensorTag(SENSORTAG_ADDRESS)

    print('Press Ctrl-C to quit.')
    enable_sensors(tag)
    
    value_list = []
    
    while True:
        # get sensor readings
        acc = tag.accelerometer.read()
        gyro = tag.gyroscope.read()
        
        value_list.append([acc[0], acc[1], acc[2], gyro[0], gyro[1], gyro[2]])
        
        if len(value_list)==20:
            message = ''
            
            acc_x = list(zip(*value_list))[0]
            acc_y = list(zip(*value_list))[1]
            acc_z = list(zip(*value_list))[2]
            gyro_x = list(zip(*value_list))[3]
            gyro_y = list(zip(*value_list))[4]
            gyro_z = list(zip(*value_list))[5]

            message = message + (str(acc_x).replace("(", "").replace(")", ", "))
            message = message + (str(acc_y).replace("(", "").replace(")", ", "))
            message = message + (str(acc_z).replace("(", "").replace(")", ", "))
            message = message + (str(gyro_x).replace("(", "").replace(")", ", "))
            message = message + (str(gyro_y).replace("(", "").replace(")", ", "))
            message = message + (str(gyro_z).replace("(", "").replace(")", ""))
        
            client_socket.send(message.encode())

            value_list = []        
        
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n+++++++++done program++++++++++")        
        client_socket.close()
            
