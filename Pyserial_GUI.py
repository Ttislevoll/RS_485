import tkinter as tk
from tkinter import BOTTOM, LEFT, NW, SOLID, SUNKEN, TOP, ttk
import ctypes
import serial
import serial.tools.list_ports
from PIL import ImageTk, Image

output : str = ""           
ports = []

def receive_data(address, data):
    try:
        index = int(combobox_ports.current())
        if index < 0:
            raise Exception()
        COM = ports[int(combobox_ports.current())].device
        ser = serial.Serial(COM, 9600, timeout = 1)
        ser.stopbits = serial.STOPBITS_ONE
        ser.parity = serial.PARITY_EVEN
        ser.bytesize = 8
        ser.write(address)
        if data == "distance":
            lbl_distance['text'] = str(ser.read(1))
            log_write("Read distance")
        elif data == "serial_number":
            lbl_serial_number['text'] = str(ser.read(1))
            log_write("Read serial_number")
    except:
        log_write("Invalid port")
        
def refresh_ports():
    global ports
    ports = serial.tools.list_ports.comports()
    combobox_ports['values'] = ports
    current_port.set("")

def log_write(text : str):    
    txt_log.insert(0.0, text + "\n")

def port_selected():
    window.focus()
    log_write(f'Selected port: {current_port.get()}')

ctypes.windll.shcore.SetProcessDpiAwareness(1)
window = tk.Tk()
window.geometry('1000x800')
window.resizable(False,False)

canvas = tk.Canvas(window, width = 700, height = 150)
canvas.pack()
img = ImageTk.PhotoImage(Image.open("onesubsea_logo.png"))
canvas.create_image(20, 20, anchor=NW, image=img)
#---------Valg av port------------------
frame_ports = tk.Frame(window, width=50, height=50)

lbl_ports = tk.Label(frame_ports, text="Available Ports")
lbl_ports.pack()

current_port = tk.StringVar()
combobox_ports = ttk.Combobox(frame_ports, textvariable=current_port)
combobox_ports['state'] = 'readonly'
combobox_ports.bind("<<ComboboxSelected>>", lambda e: port_selected())
combobox_ports.pack(side=tk.LEFT, padx=5, pady=5)

ports = serial.tools.list_ports.comports()
combobox_ports['values'] = ports

refresh_btn = ttk.Button(frame_ports, text="Refresh", command=refresh_ports)
refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)
#------------------------------------------
#----------Hente avstand-------------------
frame_distance = tk.Frame(window, width=50, height=50)

btn_distance = ttk.Button(frame_distance, text="Distance", command=lambda: receive_data(b'\xff', "distance"))
btn_distance.pack(side=tk.LEFT, padx=8, pady=8)

lbl_distance = ttk.Label(frame_distance, text="", width=11, background="white", relief=SOLID)
lbl_distance.pack(side=tk.RIGHT, padx=8, pady=8)
#------------------------------------------
#---------Hente serienummber---------------
frame_serial_number = tk.Frame(window, width=50, height=50)

btn_serial_number = ttk.Button(frame_serial_number, text="Serial Number", command=lambda: receive_data(b'\xff', "serial_number"))
btn_serial_number.pack(side=tk.LEFT, padx=8, pady=8)

lbl_serial_number = ttk.Label(frame_serial_number, text="", width=11, background="white", relief=SOLID)
lbl_serial_number.pack(side=tk.RIGHT, padx=8, pady=8)
#----------Log------------------------------
frame_log = ttk.Frame(window)
txt_log = tk.Text(frame_log, height=10)
lbl_log = ttk.Label(frame_log, text="Log")
lbl_log.pack(anchor=NW)
txt_log.pack()

frame_ports.pack()
frame_distance.pack()
frame_serial_number.pack()
frame_log.pack(side=BOTTOM)

window.mainloop()