import tkinter as tk
from tkinter import BOTTOM, LEFT, RIGHT, ttk, messagebox
from PIL import ImageTk, Image

class New_Machine:
    def __init__(self, parent, msg_list:list):
        self.window = tk.Toplevel(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.grab_set()
        self.window.geometry("400x250+750+300")
        icon = ImageTk.PhotoImage(Image.open("onesubsea_icon.png"))
        self.window.iconphoto(False, icon)
        
        self.cancel = False
        self.entrys = []
        for i in range(0, len(msg_list)):
            self.entrys.append(self.create_entry_box(msg_list[i]))
        btn_frame = ttk.Frame(self.window)
        self.btn_compress = ttk.Button(btn_frame, text='Add Compressor', command=lambda:self.submit("Compressor"))
        self.btn_compress.pack(side=LEFT, pady=(20,0), padx=(0,15))
        self.btn_compress = ttk.Button(btn_frame, text='Add Pump', command=lambda:self.submit("Pump"))
        self.btn_compress.pack(side=RIGHT, pady=(20,0), padx=(15,0))
        btn_frame.pack()

    def create_entry_box(self, msg):
        self.frame = ttk.Frame(self.window)
        self.lbl = ttk.Label(self.frame, text=msg, width=13)
        self.lbl.pack(side=LEFT, padx=10, pady=10)
        self.entry_box = ttk.Entry(self.frame, width=20)
        self.entry_box.pack(side=RIGHT, padx=10, pady=10)
        self.frame.pack()
        return self.entry_box

    def submit(self, machine_type):
        self.inputs = []
        self.machine_type = machine_type
        for i in self.entrys:
            entry = i.get()
            if entry: self.inputs.append(i.get())
            else: return
        self.window.destroy()

    def close(self):
        self.cancel = True
        self.window.destroy()