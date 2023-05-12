import numpy as np
import tflite_runtime.interpreter as tf
import pandas as pd
import time
import socket
from _thread import *

interpreter = tf.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def threaded(client_socket, addr):
    print('>> Connected by :', addr[0], ':', addr[1])

    while True:

        try:
            data = client_socket.recv(2048)            
            data = data.decode()
            
            x_test = data.split(',')
            list(x_test)
            x_test = np.array(x_test, dtype=np.float32)

            if not data:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                break

            interpreter.resize_tensor_input(input_details[0]['index'], x_test.shape)
            interpreter.allocate_tensors()
            interpreter.set_tensor(input_details[0]['index'], x_test)

            interpreter.invoke()

            # The function `get_tensor()` returns a copy of the tensor data.
            # Use `tensor()` in order to get a pointer to the tensor.
            output_data = interpreter.get_tensor(output_details[0]['index'])
            output_data = np.argmax(output_data, axis =-1) # 확률 가장 높은 레이블 번호 얻기
            print('>> Predict Label : ',end='')
            print(output_data)

            
        except ConnectionResetError as e:
            print('>> Disconnected by ' + addr[0], ':', addr[1])
            break


    client_socket.close()


HOST = '127.0.0.1'
PORT = 9999

print('>> Server Start')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

try:
    while True:
        print('>> Wait')

        client_socket, addr = server_socket.accept()
        start_new_thread(threaded, (client_socket, addr))
        
except Exception as e :
    print ('error : ',e)

finally:
    server_socket.close()

