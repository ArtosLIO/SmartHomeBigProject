from flask import Flask, request, render_template, Response, stream_with_context, url_for, redirect
from flask import jsonify
from threading import Thread
import mysql.connector
from mysql.connector import Error
import datetime


temperature = 0.0
max_v = 0
min_v = 0
lamp_v = 0
# data_graph = []
# date_graph = []
# dat_max = []
# dat_min = []

connuser = 'root'
connpass = '23l07i04o06tigr'

app = Flask(__name__)

try:
    connector = mysql.connector.connect( #Подключение к БД
        user='root',
        password='23l07i04o06tigr',
        host='localhost',
        database='smarthome'
    )
except Error as e:
    print('Error connected: ', e)
    
    
def lamp_manipulate(lamp_valu):
#     global connector
    
    try:
        connector = mysql.connector.connect( #Подключение к БД
            user='root',
            password='23l07i04o06tigr',
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)
    
    try:
        cursor = connector.cursor()
        cursor.execute('''UPDATE setting SET light = \'{}\''''.format(lamp_valu))
        connector.commit()
    except Error as e:
        print(e)
    
    if connector.is_connected():
        connector.close()
#     finally:
#         cursor.close()


def select_temperature():
    global temperature, max_v, min_v
#     , data_graph, date_graph, dat_max, dat_min
#     , connector
    
    try:
        connector = mysql.connector.connect( #Подключение к БД
            user='root',
            password='23l07i04o06tigr',
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)
    
#     data_graph = []
#     date_graph = []
#     dat_max = []
#     dat_min = []
    
    try:
        cursor = connector.cursor()
        cursor.execute('''SELECT temperature FROM data_temperature ORDER BY date DESC LIMIT 1''')
        result = cursor.fetchone()
        temperature = result[0]
    except Error as e:
        print(e)
    
    if connector.is_connected():
        connector.close()
        
    try:
        connector = mysql.connector.connect( #Подключение к БД
            user='root',
            password='23l07i04o06tigr',
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)
    
    try:
        dt = datetime.datetime.now().replace(microsecond=0)
        date_now = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
#         if box_index == 0:
#             hour = dt.hour - 1
#             date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, dt.day, hour, dt.minute, dt.second)
#         elif box_index == 1:
#             day = dt.day - 1
#             date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, day, dt.hour, dt.minute, dt.second)
#         elif box_index == 2:
        month = dt.month - 1
        date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, month, dt.day, dt.hour, dt.minute, dt.second)
            
        cursor = connector.cursor()
        cursor.execute('''SELECT * FROM data_temperature WHERE `date` BETWEEN \'{}\' AND \'{}\''''.format(date_future, date_now))
        result = cursor.fetchone()
        data_graph = []
        date_graph = []
        dat_max = []
        dat_min = []
        while result is not None:
            data_graph.append(result[1])
            date_graph.append(result[2])
            dat_min.append(min_v)
            dat_max.append(max_v)
            result = cursor.fetchone()
    except Error as e:
        print(e)
        
    if connector.is_connected():
        connector.close()
        
    time_now = datetime.datetime.now()
    return jsonify({'result': temperature, 'second_r': time_now,
                      'data_graph': data_graph, 'date_graph': date_graph,
                      'dat_max': dat_max, 'dat_min': dat_min})
#     finally:
#         cursor.close()

        
def select():
    global max_v, min_v, lamp_v, temperature
#     , connector
    
    try:
        connector = mysql.connector.connect( #Подключение к БД
            user='root',
            password='23l07i04o06tigr',
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)
    
    try: #Считывание данных с БД и управление
        cursor = connector.cursor()
        cursor.execute('''SELECT min_temperature, max_temperature, light FROM setting''')
        result = cursor.fetchone()
        
        min_v = result[0]
        max_v = result[1]
        lamp_v = result[2]
        
    except Error as e:
        print(e)
    finally:
        if connector.is_connected():
            connector.close()
        templateData = {'ledRed': lamp_v, 'maxvalue': max_v, 'minvalue': min_v}
        return templateData
    
    


@app.route('/', methods=['POST', 'GET'])
def index():
    templateData = select()
    return render_template('index.html', **templateData)


@app.route('/refresh')
def refresh():
    global temperature, data_graph, date_graph, dat_max, dat_min
    myjson = select_temperature()
#     time_now = datetime.datetime.now()
#     myjson = jsonify({'result': temperature, 'second_r': time_now,
#                       'data_graph': data_graph, 'date_graph': date_graph,
#                       'dat_max': dat_max, 'dat_min': dat_min})
    return myjson


@app.route('/<action>', methods=['post', 'get'])
def do(action):
    
    if action == "on":
        lamp_manipulate(1)
    if action == "off":
        lamp_manipulate(0)
        
    templateData = select()
    return render_template('index.html', **templateData)

@app.route('/t', methods=['post'])
def heating():
    global min_v, max_v
    if request.method == 'POST':
        if max_v != request.form.get('maxt') and request.form.get('maxt') != None:
            maxt = request.form.get('maxt')
        else:
            maxt = max_v
        if min_v != request.form.get('mint') and request.form.get('mint') != None:
            mint = request.form.get('mint')
        else:
            mint = min_v
        
    try:
        connector = mysql.connector.connect( #Подключение к БД
            user='root',
            password='23l07i04o06tigr',
            host='localhost',
            database='smarthome'
        )
    except Error as e:
        print('Error connected: ', e)
    
    try:
        cursor = connector.cursor()
        cursor.execute('''UPDATE setting SET max_temperature = \'{}\', min_temperature = \'{}\''''.format(maxt, mint))
        connector.commit()
    except Error as e:
        print(e)
    
    if connector.is_connected():
        connector.close()
        
    templateData = select()
    return render_template('index.html', **templateData)


if connector.is_connected():
    connector.close()




