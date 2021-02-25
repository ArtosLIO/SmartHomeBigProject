from tkinter import *
import tkinter.ttk as ttk
import mysql.connector
from mysql.connector import Error
from threading import Thread
import time
import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


root = Tk()
root.geometry('700x550')
connector = mysql.connector.connect()
connuser = 'root'
connpass = '23l07i04o06tigr'
fig = plt.figure() #создание екзампляра контейнера графика
ax = fig.add_subplot(111) #Создание графика

min_t = 0
max_t = 0
lamp = 0
index_graph = 0
box_index = 0

try:
    connector = mysql.connector.connect( #Подключение к БД
        user=connuser,
        password=connpass,
        host='localhost',
        database='smarthome'
    )
except Error as e:
    print('Error connected: ', e)

class SecondThread(Thread):
    '''Второй поток для связи с БД, для отправки и получение информации об состоянии системы'''
    def __init__(self):
        Thread.__init__(self)
        self.deamon = True
    def run(self):
        global min_t, max_t, lamp
        while True:
            try:
                cursor = connector.cursor()
                cursor.execute('''SELECT max_temperature, min_temperature, lamp, heating FROM setting''')
                result = cursor.fetchone()
                
                if result[0] != min_t:
                    max_t = result[0]
                if result[1] != max_t:
                    min_t = result[1]
                if result[2] != lamp:
                    if lamp == 0:
                        lamp = 1
                        bt_lamp_manipulate.configure(text='Выключить свет')
                    else:
                        lamp = 0
                        bt_lamp_manipulate.configure(text='Включить свет')
            except Error as e:
                print(e)
            
            time.sleep(1)


def lamp_manipulate():
    global lamp, connector
    
    if lamp == 0:
        lamp = 1
        bt_lamp_manipulate.configure(text='Выключить свет')
    else:
        lamp = 0
        bt_lamp_manipulate.configure(text='Включить свет')
        
    try:
        cursor = connector.cursor()
        cursor.execute('''UPDATE setting SET `lamp` = {}'''.format(lamp))
        connector.commit()
    except Error as e:
        pass


def heating_manipulate():
    global min_t, max_t, connector

    try:
        if en_heating_manipulate_min.get() != '' and en_heating_manipulate_min.get() < en_heating_manipulate_max.get():
            min_t = int(en_heating_manipulate_min.get())
        if en_heating_manipulate_max.get() != '' and en_heating_manipulate_max.get() > en_heating_manipulate_min.get():
            max_t = int(en_heating_manipulate_max.get())
        
        lb_heating_min_size.configure(text=min_t)
        lb_heating_max_size.configure(text=max_t)
        lb_heating_manipulate_error.configure(text='')
    except Error as e:
        lb_heating_manipulate_error.configure(text='Введен неверный тип данных')
        
    try:
        cursor = connector.cursor()
        cursor.execute('''UPDATE setting
SET min_temperature = \'{}\', max_temperature = \'{}\''''.format(min_t, max_t))
        connector.commit()
    except Error as e:
        pass       


def animation(i):
    global min_t, max_t, connector, box_index

    arrmini = []
    arrmax = []
    arrx = []
    arry = []
    try:
        dt = datetime.datetime.now().replace(microsecond=0)
        date_now = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        
        if box_index == 0:
            hour = dt.hour - 1
            date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, dt.day, hour, dt.minute, dt.second)
        elif box_index == 1:
            day = dt.day - 1
            date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, dt.month, day, dt.hour, dt.minute, dt.second)
        elif box_index == 2:
            month = dt.month - 1
            date_future = '{}-{}-{} {}:{}:{}'.format(dt.year, month, dt.day, dt.hour, dt.minute, dt.second)
        
        cursor = connector.cursor()
        cursor.execute('''SELECT * FROM data_temperature
WHERE `date` BETWEEN \'{}\' AND \'{}\''''.format(date_future, date_now))
        result = cursor.fetchone()
        while result is not None:
            arry.append(result[1])
            arrx.append(result[2])
            arrmini.append(min_t)
            arrmax.append(max_t)
            result = cursor.fetchone()
    except:
        pass
    
    ax.clear()
    ax.plot(arrx, arry, 'r', arrx, arrmax, 'g', arrx, arrmini, 'b') #для вывода данных
    
    plt.title('Зависимость')
    plt.xlabel('Время')
    plt.ylabel('Температура')
    
    xfmt = mdates.DateFormatter('%H:%M:%S') #формат отображения данных
    ax.xaxis.set_major_formatter(xfmt)

canvas = FigureCanvasTkAgg(fig, master=root) #отображение в окне
anim = FuncAnimation(fig, animation, interval=1000)


def graph():
    global index_graph, arry, arrx
    if index_graph == 0:
        canvas.get_tk_widget().grid(row=11, column=1, columnspan=3)
        index_graph = 1
        bt_graph.configure(text='Убрать график')
    else:
        canvas.get_tk_widget().grid_forget()
        index_graph = 0
        bt_graph.configure(text='Вывести график')


def box_graph(box_i):
    global box_index
    if str(cb_graph.get()) == 'час':
        box_index = 0
    elif str(cb_graph.get()) == 'день':
        box_index = 1
    elif str(cb_graph.get()) == 'месяц':
        box_index = 2


lb_lamp = Label(text='Состояние освещения:').grid(row=1, column=1)
lb_lamp_vv = Label()

lb_heating = Label(text='Состояния отопления: ').grid(row=2, column=1)
lb_heating_vv = Label()

lb_heating_min = Label(text='Порог минимальной температуры: ').grid(row=3, column=1)
lb_heating_min_size = Label()

lb_heating_max = Label(text='Порог максимальной температуры: ').grid(row=4, column=1)
lb_heating_max_size = Label()

lb_heating_manipulate = Label(text='Изменить пороги температуры', font=20).grid(row=5, column=1, columnspan=2)
lb_heating_manipulate_min = Label(text='Минимальная температура').grid(row=6, column=1)
lb_heating_manipulate_max = Label(text='Максимальная температура').grid(row=7, column=1)
lb_heating_manipulate_error = Label()

en_heating_manipulate_min = Entry(width=4)
en_heating_manipulate_max = Entry(width=4)

bt_heating_manipulate = Button(text='Подтвердить изменение', command=heating_manipulate)
bt_lamp_manipulate = Button(text='Включить свет', command=lamp_manipulate)
bt_graph = Button(text='Вывести график', command=graph)

lb_grahp = Label(text='Вывести график за последний')
cb_graph = ttk.Combobox(values=[u'час', u'день', u'месяц'])
cb_graph.set(u'час')
cb_graph.bind('<<ComboboxSelected>>', box_graph)

lb_lamp_vv.grid(row=1, column=2)
lb_heating_vv.grid(row=2, column=2)
lb_heating_min_size.grid(row=3, column=2)
lb_heating_max_size.grid(row=4, column=2)

en_heating_manipulate_min.grid(row=6, column=2)
en_heating_manipulate_max.grid(row=7, column=2)
lb_heating_manipulate_error.grid(row=8, column=1, columnspan=2)

bt_lamp_manipulate.grid(row=9, column=3, columnspan=2)
bt_heating_manipulate.grid(row=9, column=1, columnspan=2)
bt_graph.grid(row=10, column=1)

lb_grahp.grid(row=10, column=2)
cb_graph.grid(row=10, column=3)



thr = SecondThread()
thr.deamon = True
thr.start()
root.mainloop()
thr.stop()
cursor.close()


