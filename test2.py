import tkinter as tk
from tkinter import ANCHOR, BOTTOM, CENTER, END, LEFT, N, NW, RIGHT, SOLID, SUNKEN, SW, TOP, W, ttk, messagebox, filedialog
import ctypes
from turtle import width, window_height
import serial
import serial.tools.list_ports
from PIL import ImageTk, Image
import logging
import datetime
import struct
from machine import Machine
from sensor import Sensor
import pickle
from typing import List
import os.path
import time
from new_machine import New_Machine
from new_sensor import New_Sensor
from openpyxl import Workbook, load_workbook

#global variables
ports : list = []
ser = None
machines : List[Machine] = []
labels = {}
treeview_dict = {}

#telegrams for communicating with sensors
broadcast = [0x10,0x7f,0x01,0x09,0x89,0x16]
distance_temp_v03a = [0x10,0x00,0x01,0x4c,0x00,0x16]
temperature_v02a = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0xd1,0x0c,0x04,0x00,0x16]
#read block 0x10
sw_version = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x10,0x02,0x02,0x00,0x16]
article_number = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x10,0x04,0x04,0x00,0x16]
serial_number = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x10,0x10,0x04,0x00,0x16]
description = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x10,0x28,0x20,0x00,0x16]
#read block 0x20
measuring_unit = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x20,0x03,0x01,0x00,0x16]
measuring_range = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x20,0x1c,0x04,0x00,0x16]
measuring_offset = [0x68,0x09,0x09,0x68,0x00,0x01,0x4c,0x30,0x33,0x5e,0x20,0x20,0x04,0x00,0x16]
#assign address
assign_address = [0x68,0x09,0x09,0x68,0x00,0x01,0x43,0x37,0x3e,0x00,0x00,0x00,0x00,0x00,0x16]


#serial read functions

#reads temperature from sensor with version 0.2a or 0.3a
def get_temperature(adr: int) -> float:
    """Reads temperature from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal
        Exception: Checksum is not equal

    Returns:
        float: Temperature
    """
    if get_sw_version(adr) == "0.2a":
        temperature_v02a[4] = adr
        temperature_v02a[-2] = get_fcs(temperature_v02a, 4)
        ser.write(bytearray(temperature_v02a))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
        temp = struct.unpack('i', received[13:17])[0]
        serial_num = str(get_serial_number(adr))
        temp_corr = get_temp_corr()
        a = temp_corr[serial_num][0]
        b = temp_corr[serial_num][1]
        temperature = temp * a + b
    else:
        distance_temp_v03a[1] = adr
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(17)
        if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
        temperature = struct.unpack('f', received[11:15])[0]
    temperature = round(temperature, 1)
    return temperature

#reads distance from sensor with version 0.2a or 0.3a
def get_distance(adr : int) -> float:
    """Reads distance from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        float: Distance
    """
    distance_temp_v03a[1] = adr
    distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
    bytes = 17
    if get_sw_version(adr) == "0.2a": bytes=13
    ser.write(bytearray(distance_temp_v03a))
    received = ser.read(bytes)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    distance = struct.unpack('f', received[7:11])[0]
    distance = round(distance)
    return distance

#returns serial number from sensor
def get_serial_number(adr : int) -> int:
    """Reads serial number from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        int: Serial number
    """
    serial_number[4] = adr
    serial_number[-2] = get_fcs(serial_number, 4)
    ser.write(bytearray(serial_number))
    received = ser.read(19)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    serial_num = int.from_bytes(received[13:17], "little")
    return serial_num

#reads article number of sensor
def get_article_number(adr : int) -> int:
    """Reads article number from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        int: Article number
    """
    article_number[4] = adr
    article_number[-2] = get_fcs(article_number, 4)
    ser.write(bytearray(article_number))
    received = ser.read(19)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    article_n = int.from_bytes(received[13:17], "little")
    return article_n

#returns software version of sensor
def get_sw_version(adr : int) -> str:
    """Reads sw version from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        str: Sw version
    """
    sw_version[4] = adr
    sw_version[-2] = get_fcs(sw_version, 4)
    ser.write(bytearray(sw_version))
    received = ser.read(17)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    sw = received[13:15]
    sw_string = f'0.{sw[1]}{chr(sw[0])}'
    return sw_string

#reads destriction of sensor
def get_description(adr : int) -> str:
    """Reads description from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        str: Description
    """
    description[4] = adr
    description[-2] = get_fcs(description, 4)
    ser.write(bytearray(description))
    received = ser.read(47)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    temp = received[13:45]
    text = str(temp.decode("ascii"))
    text = text.strip()
    return text

#reads measuring unit of sensor
def get_measuring_unit(adr : int) -> str:
    """Reads measuring unit from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        str: Measuring unit
    """
    measuring_unit[4] = adr
    measuring_unit[-2] = get_fcs(measuring_unit, 4)
    ser.write(bytearray(measuring_unit))
    received = ser.read(16)
    if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
    unit = int(received[13])
    units = ["m","mm","μm"]
    return units[unit]

#reads measuring range of sensor
def get_measuring_range(adr : int) -> float:
    """Reads measuring range from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        float: Measuring range
    """
    measuring_range[4] = adr
    measuring_range[-2] = get_fcs(measuring_range, 4)
    ser.write(bytearray(measuring_range))
    received = ser.read(19)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    range = struct.unpack('f', received[13:17])[0]
    return range

#reads measuring offset of sensor
def get_measuring_offset(adr : int) -> float:
    """Reads measuring offset from sensor

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        float: Measuring offset
    """
    measuring_offset[4] = adr
    measuring_offset[-2] = get_fcs(measuring_offset, 4)
    ser.write(bytearray(measuring_offset))
    received = ser.read(19)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    offset = struct.unpack('f', received[13:17])[0]
    return offset

#returns address if it exists, or if adr=0x7f(broadcast), returns address of single connected sensor
def get_adr(adr : int) -> int:
    """Reads address from sensor. Returns address any single sensor if adr is broadcast(0x7f)

    Args:
        adr (int): Sensor address

    Raises:
        Exception: Checksum is not equal

    Returns:
        int: Address
    """
    broadcast[1] = adr
    broadcast[-2] = get_fcs(broadcast, 1)
    ser.write(bytearray(broadcast))
    received = ser.read(6)
    if get_fcs(received, 1) != received[-2]: raise Exception("Checksum is not equal")
    return received[2]

#retrieve all date from sensor
def get_all(adr: int) -> dict:
    """Reads all values from sensor

    Args:
        adr (int): Sensor address

    Returns:
        dict: Sensor readings
    """
    values = {}
    values["Address"] = adr
    values["Serial Number"] = get_serial_number(adr)
    values["SW Version"] = get_sw_version(adr)
    values["Article Number"] = get_article_number(adr) 
    values["Description"] = get_description(adr)
    values["Measuring Unit"] = get_measuring_unit(adr)
    values["Measuring Range"] = get_measuring_range(adr)
    values["Measuring Offset"] = get_measuring_offset(adr)
    values["Distance"] = get_distance(adr)
    values["Temperature"] = get_temperature(adr)  
    return values

def read_sensor(adr_func, sensor):
    try:
        txt_log.insert(END, "\n")
        try: log_text=f'Machine: {get_machine()},  Sensor: {sensor()}'
        except: log_text="No sensor selected"
        log_write(log_text)
        retrieved = get_all(adr_func())
        for key in retrieved:
            labels[key]['text'] = retrieved[key]
            log_write(f"{key}: {retrieved[key]}")
            try:
                sensor().values[key] = retrieved[key]
            except: pass
        try:
            treeview_dict[sensor().location][0] = retrieved["Serial Number"]
            treeview_dict[sensor().location][1] = retrieved["Address"]
            treeview_dict[sensor().location][3] = retrieved["Distance"]
            current_address_lbl_value['text'] = retrieved["Address"]
            update_treeview()
        except: pass
    except Exception as error:
        log_write(error)


#retrieves all data from sensors when there are mulitple sensors connected
def read_all_sensors():
    try:
        sensors_group = get_machine().sensors_group
        sensors_group.clear()
        ser.timeout=0.02
        for i in range(0, 127):
            try: 
                progress_var.set(i)
                window.update_idletasks()
                adr = get_adr(i)                
            except: pass
            else:
                txt_log.insert(END, "\n")
                log_write(f'found adr: {adr}')
                ser.timeout=1
                serial_num = get_serial_number(adr)
                sensor_found = False
                for sensor in get_machine().sensors:
                    if sensor.values["Serial Number"] == serial_num:
                        sensor_data = [sensor.location, sensor.address, sensor.nom_value, sensor.tolerance]                   
                        sensor_found = True
                        break                
                if not sensor_found: 
                    sensor_data = ["Unknown", "Unknown", "Unknown", "Unknown"]                                      
                    log_write(f"Sensor: {serial_num} not found in registry")  
                sensors_group.append(Sensor(sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3]))  
                read_sensor(lambda:adr, lambda:sensors_group[-1])                               
                ser.timeout=0.02  
        combobox_group_sensors['values'] = sensors_group
        current_group_sensor.set("")     
        combobox_group_sensors.current(newindex=len(sensors_group)-1)
        current_sensor.set("")
        ser.timeout=1
    except Exception as error: 
        log_write(error)
    progress_var.set(0)

#serial write functions
#changes the address of single connected sensor
def set_address(new_adr):
    try:
        try: current_adr = get_adr(get_sensor().values["Address"])
        except: raise Exception("Sensor is not present")
        assign_address[4] = current_adr
        assign_address[9] = new_adr
        assign_address[-2] = get_fcs(assign_address, 4)
        ser.write(bytearray(assign_address))
        received = ser.read(1)
        log_write(f'Received: {received}')
        messagebox.showinfo("Assign Address", "Restart the sensor then click 'ok'")
        seconds = 60
        wait = time.time() + seconds
        polling_sensor(new_adr, seconds, wait)
    except Exception as error:
        log_text=error
        log_write(log_text)

#looks for sensor after reset follwing address change
def polling_sensor(adr, seconds, wait):
    ser.timeout = 0.01
    if ser.in_waiting != 0: ser.reset_input_buffer()
    try:
        if(time.time() > wait):
            current_adr = "Sensor not found"                
        else: current_adr = get_adr(adr)              
    except: 
        time_left = wait - time.time()
        if(time_left < seconds):
            log_write(f'Looking for sensor: {seconds}')
            seconds -= 1
        window.after(100, lambda:polling_sensor(adr, seconds, wait))
    else:
        try: 
            get_sensor().values["Address"] = current_adr
            treeview_dict[get_sensor().location][1] = current_adr
        except: pass
        labels["Address"]['text'] = current_adr
        current_address_lbl_value['text'] = current_adr
        log_text=f'current address: {current_adr}'
        log_write(log_text)
        update_treeview()
    ser.timeout = 1

#Utility functions

#refreshes the values in list of ports
def refresh_ports(): 
    global ports
    global ser
    ports = serial.tools.list_ports.comports()
    combobox_ports['values'] = ports
    current_port.set("")
    ser = None

#writes string to log
def log_write(text : str): 
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    logging.info(f'{str(current_time)} {text}')
    txt_log.insert(END, f'{str(current_time)} {text}\n')    
    txt_log.yview_moveto(1.0)

#function is called when a port is selected from the list
def port_selected():
    global ser
    ser = None
    ser = initialize_port()
    window.focus()
    log_text=f'Selected port: {current_port.get()}'
    log_write(log_text)

#function is called when a machine is selected from the list
def machine_selected():
    global treeview_dict
    window.focus()
    log_text=f'Selected machine: {current_machine.get()}'
    log_write(log_text)
    combobox_sensors['values'] = get_machine().sensors
    combobox_group_sensors['values'] = get_machine().sensors_group
    current_sensor.set("")    
    for key in labels:
        labels[key]['text'] = ""
    if get_machine().machine_type == "Compressor":
        treeview_dict = get_machine().compressors
    elif get_machine().machine_type == "Pump":
        treeview_dict = get_machine().pumps
    update_treeview()

#function is called when a sensor is selected from the list
def sensor_selected():
    window.focus()
    current_group_sensor.set("")
    sensor = get_sensor()
    txt_log.insert(END, "\n")
    log_text=f'Selected sensor: {current_sensor.get()}'
    update_sensor_lbl()
    log_write(log_text) 
    #log_write(sensor)
    for key in sensor.values:
        if sensor.values[key]: log_write(f'{key}: {sensor.values[key]}')
        labels[key]['text'] = sensor.values[key]
    selected_address.set(sensor.address)
    current_address_lbl_value["text"] = sensor.values["Address"]

#function is called when a sensor is selected from the group sensor list
def group_sensor_selected():
    window.focus()
    current_sensor.set("")
    group_sensor = get_machine().sensors_group[combobox_group_sensors.current()]
    txt_log.insert(END, "\n")
    log_text=f'Selected sensor: {current_group_sensor.get()}'
    log_write(log_text) 
    #log_write(sensor)
    for key in group_sensor.values:
        if group_sensor.values[key]: log_write(f'{key}: {group_sensor.values[key]}')
        labels[key]['text'] = group_sensor.values[key]
    
#creates a gui button with label to display results

#calculates the fcs checksum of the telegram
def get_fcs(telegram, x):
    sum=0
    for i in range(x, len(telegram)-2):
        sum += telegram[i]
    return sum % 256

#initializes Serial object
def initialize_port():
    index = combobox_ports.current()
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

#opens a dialog window for creating a new Machine object
def create_machine():
    dialog = New_Machine(parent=window, msg_list=["ITM Number:","Description:","Serial Number:"])
    window.wait_window(dialog.window)
    if dialog.cancel == False:
        machines.append(Machine(dialog.inputs[0],dialog.inputs[1],dialog.inputs[2],dialog.machine_type))
        combobox_machines['values'] = machines
        combobox_machines.current(newindex=len(machines)-1)
        log_write(f'Added machine with Itm Number: {machines[0].itm_number}')
        machine_selected()

#opens a dialog widow for creating a new Sensor object
def create_sensor():
    if combobox_machines.current() == -1: 
        messagebox.showinfo("error", "No selected machine")
        return
    dialog = New_Sensor(window, get_machine())
    window.wait_window(dialog.window)
    if dialog.cancel == False:
        sensors = machines[combobox_machines.current()].sensors
        values = dialog.values
        sensors.append(Sensor(values[0],values[1],values[2],values[3]))
        combobox_sensors['values'] = sensors
        combobox_sensors.current(newindex=len(sensors)-1)
        log_write(f'Added sensor with location: {values[0]}')
        sensor_selected()
        selected_address.set(values[1])

#returns the selected Machine object
def get_machine():
    index = combobox_machines.current()
    if index < 0: raise Exception("Machine not selected")
    return machines[index]

#returns the selected Sensor object
def get_sensor():
    sensor_index = combobox_sensors.current()
    if sensor_index < 0: raise Exception("Sensor not selected")
    return get_machine().sensors[sensor_index]

def update_sensor_lbl():
    try:
        lbl_current_sensor['text'] = f"Sensor: {get_sensor().values['Serial Number']} Location: {get_sensor().location}"
    except: pass

def reset_buffer():
    ser.reset_input_buffer()

def get_temp_corr():
    #reads temperature correction values from text file
    temp_corr = {}
    for line in open("TempCorrFactor.txt").readlines():
        if line != '\n':
            var = line.split()
            temp_corr[var[0]] = [float(var[1]), float(var[2])]
    return temp_corr

#saves machines list to pickle file
def save():
    Files = [('Pickle Files', '*.p')]
    file = filedialog.asksaveasfilename(filetypes = Files, defaultextension = Files)
    pickle.dump(machines, open(file, "wb"))
 
#loads machines list from pickle file
def load():
    global machines
    Files = [('Pickle Files', '*.p')]
    file = filedialog.askopenfilename(filetypes=Files, defaultextension = Files) 
    machines = pickle.load(open(file, "rb"))
    n = machines



