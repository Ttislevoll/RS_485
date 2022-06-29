import tkinter as tk
from tkinter import BOTTOM, END, LEFT, NW, SOLID, SUNKEN, TOP, ttk
import ctypes
import serial
import serial.tools.list_ports
from PIL import ImageTk, Image
import logging
import datetime
import struct

output : str = ""              
ports : list = []
adr : hex = 0x00
fcs : hex = 0x00
ser = None

broadcast = [0x10,0x7f,0x01,0x09,0x89,0x16]
distance_temp_v03a = [0x10,adr,0x01,0x4c,fcs,0x16]
#block 0x10
soft_version_v03a = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x02,0x02,fcs,0x16]
article_number = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x04,0x04,fcs,0x16]
serial_number = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x10,0x04,fcs,0x16]
description = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x28,0x20,fcs,0x16]
#block 0x20
measuring_unit = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x03,0x01,fcs,0x16]
measuring_range = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x1c,0x04,fcs,0x16]
measuring_offset = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x20,0x04,fcs,0x16]


def get_fcs(telegram, x):
    sum=0
    for i in range(x, len(telegram)-2):
        sum += int(telegram[i])
    return sum % 256

def get_adr():
    ser.write(bytearray(broadcast))
    received = ser.read(6)
    return received[2]

def initialize_port():
    index = int(combobox_ports.current())
    if index < 0:
        raise Exception()
    #Creates Serial object
    COM = ports[index].device
    ser = serial.Serial(
        port=COM,
        baudrate=230400,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_EVEN,
        timeout=1
    )
    return ser


def get_temperature():
    try:
        distance_temp_v03a[1] = get_adr()
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        temperature = struct.unpack('f', received[11:15])[0]
        lbl_temperature['text'] = str(temperature)
        log_text=f'Temperature: {temperature}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_distance():
    try:
        distance_temp_v03a[1] = get_adr()
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        distance = struct.unpack('f', received[7:11])[0]
        lbl_distance['text'] = str(distance)
        log_text=f'Distance: {distance}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_serial_number():
    try:
        serial_number[4] = get_adr()
        serial_number[-2] = get_fcs(serial_number, 4)
        ser.write(bytearray(serial_number))
        received = ser.read(19)
        serial_n = int.from_bytes(received[13:17], "little")
        lbl_serial_number['text'] = str(serial_n)
        log_text=f'Serial Number: {serial_n}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_article_number():
    try:
        article_number[4] = get_adr()
        article_number[-2] = get_fcs(article_number, 4)
        ser.write(bytearray(article_number))
        received = ser.read(19)
        article_n = int.from_bytes(received[13:17], "little")
        lbl_article_number['text'] = str(article_n)
        log_text=f'Article Number: {article_n}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_soft_version():
    try:
        soft_version_v03a[4] = get_adr()
        soft_version_v03a[-2] = get_fcs(soft_version_v03a, 4)
        ser.write(bytearray(soft_version_v03a))
        received = ser.read(17)
        soft = received[13:15]
        text = f'0.{int(soft[1])}{chr(soft[0])}'
        lbl_soft_version['text'] = text
        log_text=f'Software Version: {text}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_description():
    try:
        description[4] = get_adr()
        description[-2] = get_fcs(description, 4)
        ser.write(bytearray(description))
        received = ser.read(47)
        temp = received[13:45]
        text = temp.decode("ascii")
        lbl_description['text'] = text
        log_text=f'Description: {text}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_measuring_unit():
    try:
        measuring_unit[4] = get_adr()
        measuring_unit[-2] = get_fcs(measuring_unit, 4)
        ser.write(bytearray(measuring_unit))
        received = ser.read(16)
        unit = int(received[13])
        units = ["m","mm","μm"]
        lbl_measuring_unit['text'] = units[unit]
        log_text=f'Measuring Unit: {units[unit]}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_measuring_range():
    try:
        measuring_range[4] = get_adr()
        measuring_range[-2] = get_fcs(measuring_range, 4)
        ser.write(bytearray(measuring_range))
        received = ser.read(19)
        range = struct.unpack('f', received[13:17])[0]
        lbl_measuring_range['text'] = str(range)
        log_text=f'Measuring Range: {range}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_measuring_offset():
    try:
        measuring_offset[4] = get_adr()
        measuring_offset[-2] = get_fcs(measuring_offset, 4)
        ser.write(bytearray(measuring_offset))
        received = ser.read(19)
        offset = struct.unpack('f', received[13:17])[0]
        lbl_measuring_offset['text'] = str(offset)
        log_text=f'Measuring Offset: {offset}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)


def refresh_ports(): #Function is called when refresh button is pressed
    global ports
    global ser
    ports = serial.tools.list_ports.comports()
    combobox_ports['values'] = ports
    current_port.set("")
    ser = None

def log_write(text : str): #Writes to log text-widget
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    txt_log.insert(END, f'{str(current_time)} {text}\n')
    txt_log.yview_moveto(1.0)

def logging_write(text : str):#Writes to log file
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    logging.info(f'{str(current_time)} {text}')

def port_selected(): #Function is called when a port is selected
    global ser
    ser = initialize_port()
    window.focus()
    log_text=f'Selected port: {current_port.get()}'
    log_write(log_text)
    logging_write(log_text)


#Creates Window---------------------------------------------------------------------------------------------
ctypes.windll.shcore.SetProcessDpiAwareness(1)
window = tk.Tk()
window.title("DT3005 - Serial Communication")
window.geometry('1000x800')
window.resizable(False,False)

#Configures log file--------------------------------------------------------------------------------------------
logging.basicConfig(filename="Log.log", encoding='utf-8', level=logging.INFO, format='%(levelname)s:%(message)s')

#adds onesubsea icon and logo to window------------------------------------------------------------------
canvas = tk.Canvas(window, width = 700, height = 150)
canvas.pack()
img = ImageTk.PhotoImage(Image.open("onesubsea_logo.png"))
canvas.create_image(20, 20, anchor=NW, image=img)
icon = ImageTk.PhotoImage(Image.open("onesubsea_icon.png"))
window.iconphoto(False, icon)

#Creates button for retreiving temperature value from sensor and a label to display result---------------------
frame_temperature = tk.Frame(window, width=50, height=50)
btn_temperature = ttk.Button(frame_temperature, text="Temperature", command=lambda: get_temperature())
btn_temperature.pack(side=tk.LEFT, padx=8, pady=8)
lbl_temperature = ttk.Label(frame_temperature, text="", width=11, background="white", relief=SOLID)
lbl_temperature.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving distance value from sensor and a label to display result---------------------
frame_distance = tk.Frame(window, width=50, height=50)
btn_distance = ttk.Button(frame_distance, text="Distance", command=lambda: get_distance())
btn_distance.pack(side=tk.LEFT, padx=8, pady=8)
lbl_distance = ttk.Label(frame_distance, text="", width=11, background="white", relief=SOLID)
lbl_distance.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving serial number from sensor and a label to display result--------------------
frame_serial_number = tk.Frame(window, width=50, height=50)
btn_serial_number = ttk.Button(frame_serial_number, text="Serial Number", command=lambda: get_serial_number())
btn_serial_number.pack(side=tk.LEFT, padx=8, pady=8)
lbl_serial_number = ttk.Label(frame_serial_number, text="", width=11, background="white", relief=SOLID)
lbl_serial_number.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving sofr version from sensor and a label to display result--------------------
frame_soft_version = tk.Frame(window, width=50, height=50)
btn_soft_version = ttk.Button(frame_soft_version, text="Version", command=lambda: get_soft_version())
btn_soft_version.pack(side=tk.LEFT, padx=8, pady=8)
lbl_soft_version = ttk.Label(frame_soft_version, text="", width=11, background="white", relief=SOLID)
lbl_soft_version.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving article number from sensor and a label to display result--------------------
frame_article_number = tk.Frame(window, width=50, height=50)
btn_article_number = ttk.Button(frame_article_number, text="Article Number", command=lambda: get_article_number())
btn_article_number.pack(side=tk.LEFT, padx=8, pady=8)
lbl_article_number = ttk.Label(frame_article_number, text="", width=11, background="white", relief=SOLID)
lbl_article_number.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving article number from sensor and a label to display result--------------------
frame_description = tk.Frame(window, width=50, height=50)
btn_description = ttk.Button(frame_description, text="Description", command=lambda: get_description())
btn_description.pack(side=tk.LEFT, padx=8, pady=8)
lbl_description = ttk.Label(frame_description, text="", width=11, background="white", relief=SOLID)
lbl_description.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving article number from sensor and a label to display result--------------------
frame_measuring_unit = tk.Frame(window, width=50, height=50)
btn_measuring_unit = ttk.Button(frame_measuring_unit, text="Measuring Unit", command=lambda: get_measuring_unit())
btn_measuring_unit.pack(side=tk.LEFT, padx=8, pady=8)
lbl_measuring_unit = ttk.Label(frame_measuring_unit, text="", width=11, background="white", relief=SOLID)
lbl_measuring_unit.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving article number from sensor and a label to display result--------------------
frame_measuring_range = tk.Frame(window, width=50, height=50)
btn_measuring_range = ttk.Button(frame_measuring_range, text="Measuring range", command=lambda: get_measuring_range())
btn_measuring_range.pack(side=tk.LEFT, padx=8, pady=8)
lbl_measuring_range = ttk.Label(frame_measuring_range, text="", width=11, background="white", relief=SOLID)
lbl_measuring_range.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving article number from sensor and a label to display result--------------------
frame_measuring_offset = tk.Frame(window, width=50, height=50)
btn_measuring_offset = ttk.Button(frame_measuring_offset, text="Measuring offset", command=lambda: get_measuring_offset())
btn_measuring_offset.pack(side=tk.LEFT, padx=8, pady=8)
lbl_measuring_offset = ttk.Label(frame_measuring_offset, text="", width=11, background="white", relief=SOLID)
lbl_measuring_offset.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates a label, dropdown list and refresh button for port selection---------------------------------
frame_ports = tk.Frame(window, width=50, height=50)
lbl_ports = tk.Label(frame_ports, text="Available Ports")
lbl_ports.pack()
current_port = tk.StringVar()
combobox_ports = ttk.Combobox(frame_ports, textvariable=current_port)
combobox_ports['state'] = 'readonly'
combobox_ports.bind("<<ComboboxSelected>>", lambda e: port_selected())
combobox_ports.pack(side=tk.LEFT, padx=5, pady=5)
ports = serial.tools.list_ports.comports() #Creates a list of connected serial ports
combobox_ports['values'] = ports #adds the "ports" list to a dropdown menu
refresh_btn = ttk.Button(frame_ports, text="Refresh", command=refresh_ports)
refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)

#Creates a text box for displaying log-----------------------------------------------------------
frame_log = ttk.Frame(window)
txt_log = tk.Text(frame_log, height=10)
lbl_log = ttk.Label(frame_log, text="Log")
lbl_log.pack(anchor=NW)
txt_log.pack()

#Places widgets in window----------------------------------------------------------------------------
frame_ports.pack()
frame_temperature.pack()
frame_distance.pack()
frame_soft_version.pack()
frame_serial_number.pack()
frame_article_number.pack()
frame_description.pack()
frame_measuring_unit.pack()
frame_measuring_range.pack()
frame_measuring_offset.pack()
frame_log.pack(side=BOTTOM)

#-------------------------------------------------------------------------------------------------------
window.mainloop()