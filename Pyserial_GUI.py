import tkinter as tk
from tkinter import BOTTOM, END, LEFT, N, NW, RIGHT, SOLID, SUNKEN, TOP, ttk, messagebox
import ctypes
import serial
import serial.tools.list_ports
from PIL import ImageTk, Image
import logging
import datetime
import struct
from Machine import Machine
from Sensor import Sensor
import pickle
from typing import List
import os.path
import time
from dialog_box import Dialog_box

output : str = ""              
ports : list = []
adr : hex = 0x00
fcs : hex = 0x00
new_adr : hex = 0x00
ser = None
machines : List[Machine] = []

broadcast = [0x10,0x7f,0x01,0x09,0x89,0x16]
distance_temp_v03a = [0x10,adr,0x01,0x4c,fcs,0x16]
#read block 0x10
soft_version_v03a = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x02,0x02,fcs,0x16]
article_number = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x04,0x04,fcs,0x16]
serial_number = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x10,0x04,fcs,0x16]
description = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x28,0x20,fcs,0x16]
#read block 0x20
measuring_unit = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x03,0x01,fcs,0x16]
measuring_range = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x1c,0x04,fcs,0x16]
measuring_offset = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x20,0x20,0x04,fcs,0x16]
#assign address
assign_address = [0x68,0x09,0x09,0x68,adr,0x01,0x43,0x37,0x3e,new_adr,0x00,0x00,0x00,fcs,0x16]


#serial read functions
def get_temperature():
    try:
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        distance_temp_v03a[1] = adr
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
        temperature = struct.unpack('f', received[11:15])[0]
        lbl_temperature['text'] = str(temperature)
        log_text=f'Temperature: {temperature}'
        log_write(log_text)
        logging.info(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)
        logging_write(log_text)

def get_distance():
    try:
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        distance_temp_v03a[1] = adr
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        serial_number[4] = adr
        serial_number[-2] = get_fcs(serial_number, 4)
        ser.write(bytearray(serial_number))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        article_number[4] = adr
        article_number[-2] = get_fcs(article_number, 4)
        ser.write(bytearray(article_number))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        soft_version_v03a[4] = adr
        soft_version_v03a[-2] = get_fcs(soft_version_v03a, 4)
        ser.write(bytearray(soft_version_v03a))
        received = ser.read(17)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        description[4] = adr
        description[-2] = get_fcs(description, 4)
        ser.write(bytearray(description))
        received = ser.read(47)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        measuring_unit[4] = adr
        measuring_unit[-2] = get_fcs(measuring_unit, 4)
        ser.write(bytearray(measuring_unit))
        received = ser.read(16)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        measuring_range[4] = adr
        measuring_range[-2] = get_fcs(measuring_range, 4)
        ser.write(bytearray(measuring_range))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
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
        adr = get_adr()
        if adr is None: raise Exception("Checksum is not equal")
        measuring_offset[4] = adr
        measuring_offset[-2] = get_fcs(measuring_offset, 4)
        ser.write(bytearray(measuring_offset))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        offset = struct.unpack('f', received[13:17])[0]
        lbl_measuring_offset['text'] = str(offset)
        log_text=f'Measuring Offset: {offset}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)

def get_all():
    get_temperature()
    get_distance()
    get_serial_number()
    get_article_number()
    get_soft_version()
    get_description()
    get_measuring_unit()
    get_measuring_range()
    get_measuring_offset()


#serial write functions
def set_address(new_adr):
    try:
        assign_address[4] = get_adr()
        assign_address[9] = new_adr
        assign_address[-2] = get_fcs(assign_address, 4)
        ser.write(bytearray(assign_address))
        received = ser.read(1)
        log_text=f'Received: {received}'
        log_write(log_text)
        messagebox.showinfo("Assign Address", "Restart the sensor then click 'ok'")
        t_5s = time.time() + 5
        current_adr = None
        while current_adr is None:
            current_adr = get_adr()
            if(time.time() > t_5s):
                current_adr = "Sensor polling timed out"
                break
        lbl_assign_address['text'] = str(current_adr)
        log_text=f'current address: {current_adr}'
        log_write(log_text)
        logging.info(log_text)
    except:
        log_text="Invalid port"
        log_write(log_text)
        logging_write(log_text)


#Utility functions
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
    ser = None
    ser = initialize_port()
    window.focus()
    log_text=f'Selected port: {current_port.get()}'
    log_write(log_text)
    logging_write(log_text)

def machine_selected():
    window.focus()
    log_text=f'Selected machine: {current_machine.get()}'
    log_write(log_text)
    logging_write(log_text)
    combobox_sensors['values'] = machines[combobox_machines.current()].sensors
    current_sensor.set("")    

def create_button(text, func, padx_btn=(20,8), padx_lbl=(8,20), pady=(8,8)):
    frame = ttk.Frame(frame_right, width=50, height=50)
    btn = ttk.Button(frame, text=text, width=14, command=lambda: func())
    btn.pack(side=tk.LEFT, padx=padx_btn, pady=pady)
    lbl = ttk.Label(frame, text="", width=14, background="white", relief=SOLID)
    lbl.pack(side=tk.RIGHT, padx=padx_lbl, pady=pady)
    frame.pack()
    return lbl

def get_fcs(telegram, x):
    sum=0
    for i in range(x, len(telegram)-2):
        sum += telegram[i]
    return sum % 256

def get_adr():
    try:
        ser.write(bytearray(broadcast))
        received = ser.read(6)
        if get_fcs(received, 1) != received[-2]: raise Exception("Checksum is not equal")
        return received[2]
    except:
        return None

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

def create_machine():
    dialog = Dialog_box(parent=window, msg_list=["Itm Number:","Description:","Serial Number:"])
    window.wait_window(dialog.window)
    machines.append(Machine(dialog.inputs[0],dialog.inputs[1],dialog.inputs[2]))
    combobox_machines['values'] = machines
    log_write(f'Added machine with Itm Number: {machines[0].itm_number}')

def create_sensor():
    dialog = Dialog_box(parent=window, msg_list=["Sensor Location:"])
    window.wait_window(dialog.window)
    machines[combobox_machines.current()].sensors.append(Sensor(dialog.inputs[0]))
    combobox_sensors['values'] = machines[combobox_machines.current()].sensors
    log_write(f'Added sensor with location: {dialog.inputs[0]}')


#Creates Window
ctypes.windll.shcore.SetProcessDpiAwareness(1)
window = tk.Tk()
window.title("DT3005 - Serial Communication")
window.geometry('1300x900+300+50')
window.resizable(False,False)

#Configures log file
logging.basicConfig(filename="Log.log", encoding='utf-8', level=logging.INFO, format='%(levelname)s:%(message)s')

#adds onesubsea icon and logo to window
canvas = tk.Canvas(window, width = 700, height = 150)
canvas.pack()
img = ImageTk.PhotoImage(Image.open("onesubsea_logo.png"))
canvas.create_image(20, 20, anchor=NW, image=img)
icon = ImageTk.PhotoImage(Image.open("onesubsea_icon.png"))
window.iconphoto(False, icon)

frame_right=ttk.Frame(master=window)
frame_left= ttk.Frame(master=window)

#Creates button for retreiving temperature value from sensor and a label to display result
lbl_temperature = create_button("Temperature", get_temperature, pady=(28,8))
#Creates button for retreiving distance value from sensor and a label to display result
lbl_distance = create_button("Distance", get_distance)
#Creates button for retreiving serial number from sensor and a label to display result
lbl_serial_number = create_button("Serial Number", get_serial_number)
#Creates button for retreiving sofr version from sensor and a label to display result
lbl_soft_version = create_button("Soft Version", get_soft_version)
#Creates button for retreiving article number from sensor and a label to display result
lbl_article_number = create_button("Article Number", get_article_number)
#Creates button for retreiving measuring unit from sensor and a label to display result
lbl_description = create_button("Description", get_description)
#Creates button for retreiving measuring unit from sensor and a label to display result
lbl_measuring_unit = create_button("Measuring Unit", get_measuring_unit)
#Creates button for retreiving article number from sensor and a label to display result
lbl_measuring_range = create_button("Measuring Range", get_measuring_range)
#Creates button for retreiving article number from sensor and a label to display result
lbl_measuring_offset = create_button("Measuring Offset", get_measuring_offset)


#Creates button for changing address of the sensor
frame_assign_address = ttk.Frame(frame_right, width=50, height=50)
btn_assign_address = ttk.Button(frame_assign_address, text="Assign Address", width=14, command=lambda: set_address(0x7e))
btn_assign_address.pack(side=tk.LEFT, padx=(20,8), pady=8)
lbl_assign_address = ttk.Label(frame_assign_address, text="", width=14, background="white", relief=SOLID)
lbl_assign_address.pack(side=tk.RIGHT, padx=(8,20), pady=8)

#Creates a text box for displaying log
frame_log = ttk.Frame(window)
txt_log = tk.Text(frame_log, height=31, width=60)
lbl_log = ttk.Label(frame_log, text="Log")
lbl_log.pack(anchor=NW)
txt_log.pack()

#Creates a label, dropdown list and refresh button for port selection
frame_ports = ttk.Frame(frame_left, width=50, height=50)
lbl_ports = ttk.Label(frame_ports, text="Available Ports")
lbl_ports.pack(anchor=NW, padx=(20,5), pady=(0,0))
current_port = tk.StringVar()
combobox_ports = ttk.Combobox(frame_ports, textvariable=current_port)
combobox_ports['state'] = 'readonly'
combobox_ports.bind("<<ComboboxSelected>>", lambda e: port_selected())
combobox_ports.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
ports = serial.tools.list_ports.comports() #Creates a list of connected serial ports
combobox_ports['values'] = ports #adds the "ports" list to a dropdown menu
if(len(ports) > 0): 
    combobox_ports.current(newindex=0)
    port_selected()
refresh_btn = ttk.Button(frame_ports, text="Refresh", command=refresh_ports)
refresh_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))

#Creates a label, dropdown list and refresh button for port selection
frame_machines = ttk.Frame(frame_left, width=50, height=50)
lbl_machines = ttk.Label(frame_machines, text="Machines")
lbl_machines.pack(anchor=NW, padx=(20,5), pady=(50,0))
current_machine = tk.StringVar()
combobox_machines = ttk.Combobox(frame_machines, textvariable=current_machine)
combobox_machines['state'] = 'readonly'
combobox_machines.bind("<<ComboboxSelected>>", lambda e: machine_selected())
combobox_machines.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
add_machine_btn = ttk.Button(frame_machines, text="New Machine", command=create_machine)
add_machine_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))




#Creates a label, dropdown list and refresh button for port selection
frame_sensors = ttk.Frame(frame_left, width=50, height=50)
lbl_sensors = ttk.Label(frame_sensors, text="Sensors")
lbl_sensors.pack(anchor=NW, padx=(20,5), pady=(50,0))
current_sensor = tk.StringVar()
combobox_sensors = ttk.Combobox(frame_sensors, textvariable=current_sensor)
combobox_sensors['state'] = 'readonly'
#combobox_machines.bind("<<ComboboxSelected>>", lambda e: port_selected())
combobox_sensors.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
add_sensor_btn = ttk.Button(frame_sensors, text="New Sensor", command=create_sensor)
add_sensor_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))


#Places widgets in window
frame_right.pack(side=RIGHT, anchor=N)
frame_left.pack(side=LEFT, anchor=N)
frame_ports.pack()
frame_machines.pack()
frame_sensors.pack()
frame_assign_address.pack()
frame_log.pack()

window.mainloop()