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

broadcast = [0x10,0x7f,0x01,0x09,0x89,0x16]
distance_temp_v03a = [0x10,adr,0x01,0x4c,fcs,0x16]
soft_version_v03a = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x02,0x02,fcs,0x16]
serial_number_v03a = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x10,0x04,fcs,0x16]

def get_fcs(telegram, x):
    global fcs
    sum=0
    for i in range(x, len(telegram)-2):
        sum += int(telegram[i])
    fcs = hex(sum % 256)

def get_adr():
    global adr
    ser = initialize_port()
    ser.write(bytearray(broadcast))
    received = ser.read(6)
    adr = hex(received[2])


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
        get_adr()
        get_fcs(distance_temp_v03a, 1)
        ser = initialize_port()
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        temperature = struct.unpack('f', received[11:15])
        lbl_distance['text'] = str(temperature)
        log_text=f'Temperature: {temperature}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_serial_number():
    try:
        get_adr()
        get_fcs(serial_number_v03a, 4)
        ser = initialize_port()
        ser.write(bytearray(serial_number_v03a))
        received = ser.read(19)
        serial_number = int.from_bytes(received[13:17], "little")
        lbl_serial_number['text'] = str(serial_number)
        log_text=f'Serial Number: {serial_number}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def receive_data(address, data): #Function is called when button for retrieving data from sensor is pressed
    try:
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
        #Sends request to sensor        
        ser.write(address)        
        #Reads returned value
        if data == "distance":
            received = ser.read(17)
            distance = struct.unpack('f', received[7:11])
            temperature = struct.unpack('f', received[11:15])
            lbl_distance['text'] = str(distance)
            log_text=f'Distance: {distance}'
            log_text2=f'Temperature: {temperature}'
            log_write(log_text)
            log_write(log_text2)
            logging.info(log_text)
        elif data == "serial_number":
            received = ser.read(17)
            soft_number = received[14]
            soft_letter = chr(received[13])
            soft_version = f'{soft_number}{soft_letter}'
            lbl_serial_number['text'] = soft_version
            log_text=f'Read serial number: {soft_version}'
            log_write(log_text)
            logging_write(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)
        
def refresh_ports(): #Function is called when refresh button is pressed
    global ports
    ports = serial.tools.list_ports.comports()
    combobox_ports['values'] = ports
    current_port.set("")

def log_write(text : str): #Writes to log text-widget
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    txt_log.insert(END, f'{str(current_time)} {text}\n')
    txt_log.yview_moveto(1.0)

def logging_write(text : str):#Writes to log file
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    logging.info(f'{str(current_time)} {text}')

def port_selected(): #Function is called when a port is selected
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

#Creates button for retreiving distance value from sensor and a label to display result---------------------
frame_distance = tk.Frame(window, width=50, height=50)
btn_temperature = ttk.Button(frame_distance, text="Temperature", command=lambda: get_temperature())
btn_temperature.pack(side=tk.LEFT, padx=8, pady=8)
lbl_distance = ttk.Label(frame_distance, text="", width=11, background="white", relief=SOLID)
lbl_distance.pack(side=tk.RIGHT, padx=8, pady=8)

#Creates button for retreiving serial number from sensor and a label to display result--------------------
frame_serial_number = tk.Frame(window, width=50, height=50)
btn_serial_number = ttk.Button(frame_serial_number, text="Serial Number", command=lambda: get_serial_number())
btn_serial_number.pack(side=tk.LEFT, padx=8, pady=8)
lbl_serial_number = ttk.Label(frame_serial_number, text="", width=11, background="white", relief=SOLID)
lbl_serial_number.pack(side=tk.RIGHT, padx=8, pady=8)

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
frame_distance.pack()
frame_serial_number.pack()
frame_log.pack(side=BOTTOM)

#-------------------------------------------------------------------------------------------------------
window.mainloop()