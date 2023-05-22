import numpy as np
import tflite_runtime.interpreter as tf
import pandas as pd
import time
import socket
from _thread import *
import pymysql as ps
import time
import datetime
import RPi.GPIO as GPIO
import threading

PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

now_date = datetime.datetime.now()
today_date = now_date.strftime('%Y-%m-%d')

interpreter = tf.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#conn = ps.connect(host='', user='', passwd='', db='')
curs = conn.cursor()

behavior = ['none', 'stand', 'sleep', 'seat', 'walk', 'slowWalk', 'run', 'eat', 'bite']

sql = f"insert into mostBehavior(dogIdx, mDate) select 1, '{today_date}' from dual where not exists(select 1 from mostBehavior where mDate='{today_date}')"
curs.execute(sql)
conn.commit()


def threaded(client_socket, addr):
    print('>> Connected by :', addr[0], ':', addr[1])
    pre_time = time.time()    

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
            print(output_data[0])
            
            if(output_data[0] == 8):
                GPIO.output(PIN, GPIO.HIGH)                
            else:
                GPIO.output(PIN, GPIO.LOW)                
            
            
            
            sql = 'delete from behavior'
            curs.execute(sql)
            conn.commit()

            sql = f'insert into behavior(dog_idx, behaviorName) values (1, {output_data[0]})'
            curs.execute(sql)
            conn.commit()
            
            now_time = time.time()
            gap_time = round(now_time-pre_time)
                                    
            
            sql = f"update mostBehavior set {behavior[output_data[0]]}={behavior[output_data[0]]}+{gap_time} where mDate='{today_date}'"
            curs.execute(sql)
            conn.commit()
            
            pre_time = now_time
            
        except ConnectionResetError as e:
            print('>> Disconnected by ' + addr[0], ':', addr[1])
            GPIO.cleanup()
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

