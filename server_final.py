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
from sklearn.preprocessing import MinMaxScaler
import pygame

now_date = datetime.datetime.now()
today_date = now_date.strftime('%Y-%m-%d')

#interpreter = tf.Interpreter(model_path="cnn_1_final.tflite")
interpreter = tf.Interpreter(model_path="tuner_layer3.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#conn = ps.connect(host='', user='', passwd='', db='')
curs = conn.cursor()

behavior = ['stand', 'sleep', 'seat', 'walk', 'slowWalk', 'run', 'eat', 'bite']

sql = f"insert into mostBehavior(dogIdx, mDate) select 1, '{today_date}' from dual where not exists(select 1 from mostBehavior where mDate='{today_date}')"
curs.execute(sql)
conn.commit()

scaler = MinMaxScaler()

pygame.mixer.init()
pygame.mixer.music.load("./warning_sound.wav")

certi_time = datetime.datetime.strptime("12:00:00", "%H:%M:%S")

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
            
            x_test = x_test.reshape(120,1)            
            scaler.fit(x_test)
            x_test = scaler.transform(x_test)
            
            #########CNN#########
            """
            x_test = x_test.reshape(120,)
            test_shape = x_test.shape
            
            x_test = np.array_split(x_test, 6)
            test_ax, test_ay, test_az, test_gx, test_gy, test_gz = x_test[0], x_test[1], x_test[2], x_test[3], x_test[4], x_test[5]
            
            x_test = np.zeros((test_shape[0], 20, 6), dtype=np.float32)
            x_test[..., 0] = test_ax
            x_test[..., 1] = test_ay
            x_test[..., 2] = test_az
            x_test[..., 3] = test_gx
            x_test[..., 4] = test_gy
            x_test[..., 5] = test_gz
            """
                

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
            
            
            now_time = datetime.datetime.now()
            now_datetime = now_time.strftime('%Y-%m-%d %H:%M:%S')
            now_time = now_time.strftime('%H:%M:%S')
            now_time = datetime.datetime.strptime(now_time,'%H:%M:%S')
            
            diff = abs(certi_time - now_time)
            diff_minute = diff.seconds/60
            
            
            if(output_data[0] == 6 and diff_minute > 5):
                #GPIO.output(PIN, GPIO.HIGH)
                pygame.mixer.music.play()
                print("sound~~")
                
                sql = f"insert into abnormal(dog_idx, abnormalName, abnormalTime) values(1, '먹기','{now_datetime}')"
                curs.execute(sql)
                conn.commit()
                
            elif(output_data[0] == 7 and diff_minute > 5):
                #GPIO.output(PIN, GPIO.HIGH)
                pygame.mixer.music.play()
                print("sound~~")
                                
                sql = f"insert into abnormal(dog_idx, abnormalName, abnormalTime) values (1, '뜯기','{now_datetime}')"
                curs.execute(sql)
                conn.commit()               
                        
                
            else:
                #GPIO.output(PIN, GPIO.LOW)
                pygame.mixer.music.stop()
            
            
            
            sql = 'delete from behavior'
            curs.execute(sql)
            conn.commit()

            sql = f'insert into behavior(dog_idx, behaviorName) values (1, {output_data[0]})'
            curs.execute(sql)
            conn.commit()
            
            """
            sql = f"insert into abnormal(dog_idx, abnormalName, abnormalTime) values (1, '뜯기','{now_datetime}')"
            curs.execute(sql)
            conn.commit()
            """
            
            now_time = time.time()
            gap_time = round(now_time-pre_time)
                                    
            
            sql = f"update mostBehavior set {behavior[output_data[0]]}={behavior[output_data[0]]}+{gap_time} where mDate='{today_date}'"
            curs.execute(sql)
            conn.commit()
            
            pre_time = now_time
            
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
    GPIO.output(PIN, GPIO.LOW)
    GPIO.cleanup()
    server_socket.close()

