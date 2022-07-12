import tkinter as tk
from tkinter import ANCHOR, BOTTOM, CENTER, END, LEFT, N, NW, RIGHT, SOLID, SUNKEN, TOP, W, ttk, messagebox, filedialog
import ctypes
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
          
#global variables
ports : list = []
adr : hex = 0x00
fcs : hex = 0x00
new_adr : hex = 0x00
seconds = 0
t_60s = 0
ser = None
machines : List[Machine] = []
labels = {}
temp_corr = {}

#reads temperature correction values from text file
for line in open("TempCorrFactor.txt").readlines():
    if line != '\n':
        var = line.split()
        temp_corr[var[0]] = [float(var[1]), float(var[2])]

#telegrams for communicating with sensors
broadcast = [0x10,0x7f,0x01,0x09,0x89,0x16]
distance_temp_v03a = [0x10,adr,0x01,0x4c,fcs,0x16]
temperature_v02a = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0xd1,0x0c,0x04,fcs,0x16]
#read block 0x10
sw_version = [0x68,0x09,0x09,0x68,adr,0x01,0x4c,0x30,0x33,0x5e,0x10,0x02,0x02,fcs,0x16]
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

#reads temperature from sensor with version 0.2a or 0.3a
def get_temperature(adr, sensor):
    try:
        adr = adr()
        if get_sw_version(lambda:adr) == "0.2a":
            temperature_v02a[4] = adr
            temperature_v02a[-2] = get_fcs(temperature_v02a, 4)
            ser.write(bytearray(temperature_v02a))
            received = ser.read(19)
            if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
            temp = struct.unpack('i', received[13:17])[0]
            serial_num = str(get_serial_number(lambda:adr))
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
        try: sensor().values["Temperature"] = temperature
        except: pass
        labels["Temperature"]['text'] = str(temperature)
        log_text=f'Temperature: {temperature}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads distance from sensor with version 0.2a or 0.3a
def get_distance(adr, sensor):
    try:
        adr=adr()
        distance_temp_v03a[1] = adr
        distance_temp_v03a[-2] = get_fcs(distance_temp_v03a, 1)
        bytes = 17
        if get_sw_version(lambda:adr) == "0.2a": bytes=13
        ser.write(bytearray(distance_temp_v03a))
        received = ser.read(bytes)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        distance = struct.unpack('f', received[7:11])[0]
        try: sensor().values["Distance"] = distance
        except: pass
        labels["Distance"]['text'] = str(distance)
        log_text=f'Distance: {distance}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#returns serial number from sensor
def get_serial_number(adr):
    serial_number[4] = adr()
    serial_number[-2] = get_fcs(serial_number, 4)
    ser.write(bytearray(serial_number))
    received = ser.read(19)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    serial_num = int.from_bytes(received[13:17], "little")
    return serial_num

#saves and prints serial number
def save_serial_number(adr, sensor):
    try:
        serial_number = get_serial_number(adr)
        try: sensor().values["Serial Number"] = serial_number
        except: pass
        labels["Serial Number"]['text'] = str(serial_number)
        log_text=f'Serial Number: {serial_number}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads article number of sensor
def get_article_number(adr, sensor):
    try:
        article_number[4] = adr()
        article_number[-2] = get_fcs(article_number, 4)
        ser.write(bytearray(article_number))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        article_n = int.from_bytes(received[13:17], "little")
        try: sensor().values["Article Number"] = article_n
        except: pass
        labels["Article Number"]['text'] = str(article_n)
        log_text=f'Article Number: {article_n}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#returns software version of sensor
def get_sw_version(adr):
    sw_version[4] = adr()
    sw_version[-2] = get_fcs(sw_version, 4)
    ser.write(bytearray(sw_version))
    received = ser.read(17)
    if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
    sw = received[13:15]
    sw_string = f'0.{sw[1]}{chr(sw[0])}'
    return sw_string

#save and print software version
def save_sw_version(adr, sensor):
    try:
        sw_version = get_sw_version(adr)
        try: sensor().values["SW Version"] = sw_version
        except: pass
        labels["SW Version"]['text'] = sw_version
        log_text=f'Software Version: {sw_version}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads destriction of sensor
def get_description(adr, sensor):
    try:
        description[4] = adr()
        description[-2] = get_fcs(description, 4)
        ser.write(bytearray(description))
        received = ser.read(47)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        temp = received[13:45]
        text = str(temp.decode("ascii"))
        text = text.strip()
        try: sensor().values["Description"] = text
        except: pass
        labels["Description"]['text'] = text
        log_text=f'Description: {text}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads measuring unit of sensor
def get_measuring_unit(adr, sensor):
    try:
        measuring_unit[4] = adr()
        measuring_unit[-2] = get_fcs(measuring_unit, 4)
        ser.write(bytearray(measuring_unit))
        received = ser.read(16)
        if get_fcs(received, 4) != received[-2]: raise Exception("Checksum is not equal")
        unit = int(received[13])
        units = ["m","mm","μm"]
        try: sensor().values["Measuring Unit"] = units[unit]
        except: pass
        labels["Measuring Unit"]['text'] = units[unit]
        log_text=f'Measuring Unit: {units[unit]}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads measuring range of sensor
def get_measuring_range(adr, sensor):
    try:
        measuring_range[4] = adr()
        measuring_range[-2] = get_fcs(measuring_range, 4)
        ser.write(bytearray(measuring_range))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        range = struct.unpack('f', received[13:17])[0]
        try: sensor().values["Measuring Range"] = range
        except: pass
        labels["Measuring Range"]['text'] = str(range)
        log_text=f'Measuring Range: {range}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#reads measuring offset of sensor
def get_measuring_offset(adr, sensor):
    try:
        measuring_offset[4] = adr()
        measuring_offset[-2] = get_fcs(measuring_offset, 4)
        ser.write(bytearray(measuring_offset))
        received = ser.read(19)
        if get_fcs(received, 4) != received[-2]: raise Exception("checksum is not equal")
        offset = struct.unpack('f', received[13:17])[0]
        try: sensor().values["Measuring Offset"] = offset
        except: pass
        labels["Measuring Offset"]['text'] = str(offset)
        log_text=f'Measuring Offset: {offset}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#returns address if it exists, or if adr=0x7f(broadcast), returns address of single connected sensor
def get_adr(adr):
    broadcast[1] = adr
    broadcast[-2] = get_fcs(broadcast, 1)
    ser.write(bytearray(broadcast))
    received = ser.read(6)
    if get_fcs(received, 1) != received[-2]: raise Exception("Checksum is not equal")
    return received[2]

#saves and prints address
def save_address(adr, sensor):
    try:
        address = get_adr(adr())
        try: sensor().values["Address"] = address
        except: pass
        labels["Address"]['text'] = address
        log_text=f'Address: {address}'
        log_write(log_text)
    except Exception as error:
        log_text=error
        log_write(log_text)

#retrieve all date from sensor
def get_all(adr, sensor):
    txt_log.insert(END, "\n")
    try: log_text=f'Machine: {get_machine()},  Sensor: {get_sensor()}'
    except: log_text="No sensor selected"
    log_write(log_text)
    get_temperature(adr, sensor)
    get_distance(adr, sensor)
    save_serial_number(adr, sensor)
    get_article_number(adr, sensor)
    save_sw_version(adr, sensor)
    get_description(adr, sensor)
    get_measuring_unit(adr, sensor)
    get_measuring_range(adr, sensor)
    get_measuring_offset(adr, sensor)
    save_address(adr, sensor)

#retrieves all data from sensors when there are mulitple sensors connected
def get_all_group():
    sensors_group = get_machine().sensors_group
    sensors_group.clear()
    ser.timeout=0.05
    for i in range(0,127):
        try: 
            adr = get_adr(i)
        except: pass
        else:
            try:
                log_write(f'found adr: {adr}')
                ser.timeout=1
                serial_num = get_serial_number(lambda:adr)
                sensor_found = False
                for sensor in get_machine().sensors:
                    if sensor.values["Serial Number"] == serial_num:
                        sensors_group.append(Sensor(sensor.location, sensor.address, sensor.nom_value, sensor.tolerance))                    
                        get_all(lambda:adr, lambda:sensors_group[-1])
                        sensor_found = True
                        break                
                if not sensor_found: 
                    sensors_group.append(Sensor("Unknown", "Unknown", "Unknown", "Unknown"))                                        
                    log_write(f"Sensor: {serial_num} not found in registry")
                    get_all(lambda:adr, lambda:sensors_group[-1])
                ser.timeout=0.01                
            except Exception as error: 
                log_write(error)
                break   
    combobox_group_sensors['values'] = get_machine().sensors_group
    current_group_sensor.set("")     
    ser.timeout=1
    

#serial write functions
#changes the address of single connected sensor
def set_address(new_adr):
    try:
        try: current_adr=get_adr(get_sensor().values["Address"])
        except: raise Exception("Sensor is not present")
        assign_address[4] = current_adr
        assign_address[9] = new_adr
        assign_address[-2] = get_fcs(assign_address, 4)
        ser.write(bytearray(assign_address))
        received = ser.read(1)
        log_text=f'Received: {received}'
        log_write(log_text)
        messagebox.showinfo("Assign Address", "Restart the sensor then click 'ok'")
        global seconds
        global t_60s
        seconds = 60
        t_60s = time.time() + seconds
        polling_sensor()
    except Exception as error:
        log_text=error
        log_write(log_text)

#looks for sensor after reset follwing address change
def polling_sensor():
    global seconds
    global t_60s
    current_adr = None
    ser.timeout = 0.01
    if ser.in_waiting != 0: ser.reset_input_buffer()
    try:
        if(time.time() > t_60s):
            current_adr = "Sensor not found"                
        else: current_adr = get_adr(0x7f)              
    except: 
        time_left = t_60s - time.time()
        if(time_left < seconds):
            log_write(f'Looking for sensor: {seconds}')
            seconds -= 1
        window.after(100, polling_sensor)
    else:
        try: get_sensor().values["Address"] = current_adr
        except: pass
        labels["Address"]['text'] = str(current_adr)
        log_text=f'current address: {current_adr}'
        log_write(log_text)
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
    window.focus()
    log_text=f'Selected machine: {current_machine.get()}'
    log_write(log_text)
    combobox_sensors['values'] = get_machine().sensors
    combobox_group_sensors['values'] = get_machine().sensors_group
    current_sensor.set("")    
    for key in labels:
        labels[key]['text'] = ""

#function is called when a sensor is selected from the list
def sensor_selected():
    window.focus()
    current_group_sensor.set("")
    sensor = get_sensor()
    txt_log.insert(END, "\n")
    log_text=f'Selected sensor: {current_sensor.get()}'
    lbl_current_sensor['text'] = f"Sensor: {sensor.values['Serial Number']} Location: {sensor.location}"
    log_write(log_text) 
    #log_write(sensor)
    for key in sensor.values:
        if sensor.values[key]: log_write(f'{key}: {sensor.values[key]}')
        labels[key]['text'] = sensor.values[key]

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
def create_button(text, func, padx_btn=(20,8), padx_lbl=(8,20), pady=(8,8)):
    frame = ttk.Frame(frame_right, width=50, height=50)
    btn = ttk.Button(frame, text=text, width=14, command=lambda: func())
    btn.pack(side=tk.LEFT, padx=padx_btn, pady=pady)
    lbl = ttk.Label(frame, text="", width=14, background="white", relief=SOLID)
    lbl.pack(side=tk.RIGHT, padx=padx_lbl, pady=pady)
    frame.pack()
    return lbl

#calculates the fcs checksum of the telegram
def get_fcs(telegram, x):
    sum=0
    for i in range(x, len(telegram)-2):
        sum += telegram[i]
    return sum % 256

#initializes Serial object
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
    return machines[combobox_machines.current()]

#returns the selected Sensor object
def get_sensor():
    return machines[combobox_machines.current()].sensors[combobox_sensors.current()]

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

lbl_current_sensor = ttk.Label(frame_right, text="")
lbl_current_sensor.pack(padx=(8,8), pady=(0,5))

#Creates button for retreiving all data from sensor and a label to display result
create_button("Get All", lambda:get_all(lambda:get_adr(0x7f), get_sensor), pady=(28,8))
#Creates button for retreiving temperature value from sensor and a label to display result
labels["Temperature"] = create_button("Temperature", lambda:get_temperature(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving distance value from sensor and a label to display result
labels["Distance"] = create_button("Distance", lambda:get_distance(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving serial number from sensor and a label to display result
labels["Serial Number"] = create_button("Serial Number", lambda:save_serial_number(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving software version from sensor and a label to display result
labels["SW Version"] = create_button("SW Version", lambda:save_sw_version(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving article number from sensor and a label to display result
labels["Article Number"] = create_button("Article Number", lambda:get_article_number(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving description from sensor and a label to display result
labels["Description"] = create_button("Description", lambda:get_description(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving measuring unit from sensor and a label to display result
labels["Measuring Unit"] = create_button("Measuring Unit", lambda:get_measuring_unit(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving measuring range from sensor and a label to display result
labels["Measuring Range"] = create_button("Measuring Range", lambda:get_measuring_range(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving measuring offset from sensor and a label to display result
labels["Measuring Offset"] = create_button("Measuring Offset", lambda:get_measuring_offset(lambda:get_adr(0x7f), get_sensor))
#Creates button for retreiving address from sensor and a label to display result
labels["Address"] = create_button("Address", lambda:save_address(lambda:get_adr(0x7f), get_sensor))

#creates a button for retreiving all data from group of sensors
create_button("Group Sensors", get_all_group)

#Creates a text box for displaying log
frame_log = ttk.Frame(window)
txt_log = tk.Text(frame_log, height=31, width=45)
lbl_log = ttk.Label(frame_log, text="Log")
lbl_log.pack(anchor=NW)
txt_log.pack(side=LEFT)
scrollbar = ttk.Scrollbar(frame_log, orient=tk.VERTICAL, command=txt_log.yview)
txt_log.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=tk.BOTH)



#Creates a list and button for changing address
frame_assign_address = ttk.Frame(frame_left, width=50, height=50)
lbl_assign_address = ttk.Label(frame_assign_address, text="Change Address")
lbl_assign_address.pack(anchor=NW, padx=(20,5), pady=(50,0))
selected_address = tk.StringVar()
entry_assign_address = ttk.Entry(frame_assign_address, textvariable=selected_address, width=20)
entry_assign_address.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
assign_address_btn = ttk.Button(frame_assign_address, text="Assign Address", command=lambda: set_address(int(selected_address.get())))
assign_address_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))


#Creates a label, dropdown list and refresh button for port selection
frame_ports = ttk.Frame(frame_left, width=50, height=50)
lbl_ports = ttk.Label(frame_ports, text="Available Ports")
lbl_ports.pack(anchor=NW, padx=(20,5), pady=(0,0))
current_port = tk.StringVar()
combobox_ports = ttk.Combobox(frame_ports, textvariable=current_port, width=18)
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

#Creates a list for machine selection
frame_machines = ttk.Frame(frame_left, width=50, height=50)
lbl_machines = ttk.Label(frame_machines, text="Machines")
lbl_machines.pack(anchor=NW, padx=(20,5), pady=(50,0))
current_machine = tk.StringVar()
combobox_machines = ttk.Combobox(frame_machines, textvariable=current_machine, width=18)
combobox_machines['state'] = 'readonly'
combobox_machines.bind("<<ComboboxSelected>>", lambda e: machine_selected())
combobox_machines.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
add_machine_btn = ttk.Button(frame_machines, text="New Machine", command=create_machine)
add_machine_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))

#Creates a list for sensor selection
frame_sensors = ttk.Frame(frame_left, width=50, height=50)
lbl_sensors = ttk.Label(frame_sensors, text="Sensors")
lbl_sensors.pack(anchor=NW, padx=(20,5), pady=(50,0))
current_sensor = tk.StringVar()
combobox_sensors = ttk.Combobox(frame_sensors, textvariable=current_sensor, width=18)
combobox_sensors['state'] = 'readonly'
combobox_sensors.bind("<<ComboboxSelected>>", lambda e: sensor_selected())
combobox_sensors.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))
add_sensor_btn = ttk.Button(frame_sensors, text="New Sensor", command=create_sensor)
add_sensor_btn.pack(side=tk.RIGHT, padx=(5,20), pady=(0,0))

#Creates a list for group sensor selection
frame_group_sensors = ttk.Frame(frame_left, width=50, height=50)
lbl_group_sensors = ttk.Label(frame_group_sensors, text="Group Sensors")
lbl_group_sensors.pack(anchor=NW, padx=(20,5), pady=(50,0))
current_group_sensor = tk.StringVar()
combobox_group_sensors = ttk.Combobox(frame_group_sensors, textvariable=current_group_sensor, width=18)
combobox_group_sensors['state'] = 'readonly'
combobox_group_sensors.bind("<<ComboboxSelected>>", lambda e: group_sensor_selected())
combobox_group_sensors.pack(side=tk.LEFT, padx=(20,5), pady=(0,0))

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
    combobox_machines['values'] = machines
 
frame = ttk.Frame(window)
frame.pack()
 
mainmenu = tk.Menu(frame)
mainmenu.add_command(label = "Save", command= save)  
mainmenu.add_command(label = "Load", command= load)
mainmenu.add_command(label = "Exit", command= window.destroy)
 
window.config(menu = mainmenu)

#Places widgets in window
frame_right.pack(side=RIGHT, anchor=N)
frame_left.pack(side=LEFT, anchor=N)
frame_ports.pack()
frame_machines.pack()
frame_sensors.pack()
frame_group_sensors.pack(anchor=W)
frame_assign_address.pack()
frame_log.pack()

window.mainloop()