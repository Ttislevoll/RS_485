import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

output : str = ""           
deviceList = []

def receiveData(address, data):
    if deviceList:
        global output
        for port in deviceList:
            if port.description in port_box.get():
                COM = port.device
            else:
                output += f"\nIngen port funnet"
                print(output)
                return
        ser = serial.Serial(COM, 9600, timeout = 1)
        ser.write(address)
        if data == "Avstand":
            distance_lbl['text'] = str(ser.read(1))
        elif data == "SerialNumber":
            print("serial")
    else:
        output += f"\nIngen port funnet"
        print(output)
        return

def Refresh_Ports():
    global deviceList
    deviceList = serial.tools.list_ports.comports()
    port_box['values'] = deviceList
    current_port.set("")

window = tk.Tk()
window.geometry('800x400')
window.resizable(False,False)
#---------Valg av port------------------
port_frame = tk.Frame(window, width=50, height=50)

port_lbl = tk.Label(port_frame, text="Velg port")
port_lbl.pack()

current_port = tk.StringVar()
port_box = ttk.Combobox(port_frame, textvariable=current_port)
port_box['state'] = 'readonly'
deviceList = serial.tools.list_ports.comports()
port_box['values'] = deviceList
port_box.bind("<<ComboboxSelected>>",lambda e: window.focus())
port_box.pack(side=tk.LEFT, padx=5, pady=5)

refresh_btn = ttk.Button(port_frame, text="Refresh", command=Refresh_Ports)
refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)
#------------------------------------------
#----------Hente avstand-------------------
distance_frame = tk.Frame(window, width=50, height=50)

distance_btn = tk.Button(distance_frame, text="Avstand", command=lambda: receiveData(b'\xff', "Avstand"))
distance_btn.pack(side=tk.LEFT, padx=5, pady=5)

distance_lbl = tk.Label(distance_frame, text=" ", width=10, bg="white")
distance_lbl.pack(side=tk.RIGHT, padx=5, pady=5)
#------------------------------------------

port_frame.pack()
distance_frame.pack()

window.mainloop()