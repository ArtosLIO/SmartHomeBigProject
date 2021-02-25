from w1thermsensor import W1ThermSensor
import time
import datetime
import mysql.connector
from mysql.connector import Error
import RPi.GPIO as GPIO


connector = mysql.connector.connect()
sensor = W1ThermSensor()

pin_Lamp =  #пин лампы
pin_Heating =  #пин обогревателя
pin_Sensor = 4 #пин датчка температуры
GPIO.setmode(GPIO.BCM)
GPIO.setup([pin_Led, pin_Heating], GPIO.OUT)
GPIO.setup(pin_Sensor, GPIO.IN)
GPIO.setwarnings(False)


i = 0
temperature = 0
date_time = 0 #дата и время получение данных с сенсора
connuser = 'root'
connpass = '23l07i04o06tigr'


try:
        connector = mysql.connector.connect( #Подключение к БД
            user=connuser,
            password=connpass,
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)


while True: #Считывание и запись температуры и времени
    temperature = sensor.get_temperature()
    date_time = datetime.datetime.now().replace(microsecond=0)
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    
    if i == 5: #Передает данные времени и температуры в БД каждые 5 секунд
        try:
            cursor = connector.cursor()
            cursor.execute('''INSERT INTO data_temperature (temperature, date) () VALUE (\'{}\', \'{}\')'''.format(temperature, date_time)) #Введение данных в БД
            connector.commit()
        except Error as e:
            print(e)
        finally:
            i = 0
#             cursor.close()
             
    try: #Считывание данных с БД и управление
        cursor = connector.cursor()
        cursor.execute('''SELECT min_temperature, max_temperature, led_lamp FROM setting''')
        result = cursor.fetchone()
        
        if temperature < result[0]:
            GPIO.output(pin_Heating, GPIO.HIGH)
        if temperature > result[1]:
            GPIO.output(pin_Heating, GPIO.LOW)
        if result[2] == 1:
            GPIO.output(pin_Lamp, GPIO.HIGH)
        if result[2] == 0:
            GPIO.output(pin_Lamp, GPIO.LOW)
    except Error as e:
        print(e)
#     finally:
#         cursor.close()
            
    time.sleep(1)
    i += 1

if connector.is_connected():
    connector.close()

GPOI.cleanup()
    













