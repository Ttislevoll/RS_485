import tkinter as tk
from tkinter import CENTER, LEFT, RIGHT, ttk, font
from PIL import ImageTk, Image
from Machine import Machine
from compressor import Compressor

class Sensor_Window:
    def __init__(self, parent, machine):
        self.window = tk.Toplevel(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.grab_set()
        self.window.geometry("1000x500+750+300")
        icon = ImageTk.PhotoImage(Image.open("onesubsea_icon.png"))
        self.window.iconphoto(False, icon)
        self.s=ttk.Style()
        self.s.configure('Treeview', rowheight=25)

        self.cancel = False
        self.machine = machine
        self.tree = self.create_treeview(machine.machine_type)
        self.btn = ttk.Button(self.window, text='Done', command=self.submit)
        self.btn.pack(pady=(25,0))

    def create_treeview(self, machine_type):
        columns = ("one", "two", "three", "four")
        frame = ttk.Frame(self.window)
        tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        tree.heading('one', text=machine_type)
        tree.heading('two', text="Address")
        tree.heading('three', text="Nom Value[µm]")
        tree.heading('four', text="Tolerance[±µm]")
        for i in range(1,4): tree.column(column=columns[i], anchor=CENTER)
        if self.machine.machine_type == "Compressor":
            lines = self.get_compressors()
        elif self.machine.machine_type == "Pump":
            lines = self.get_pumps()
        for line in lines:
            tree.insert('', tk.END, values=line.split())
        tree.pack(side=LEFT)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=tk.BOTH)
        frame.pack()
        return tree
        
    def submit(self):
        self.selected_item = self.tree.selection()
        self.values = self.tree.item(self.selected_item)['values']
        if len(self.values) > 0: self.window.destroy()

    def close(self):
        self.cancel = True
        self.window.destroy()

    def get_compressors(self):
        lines = open("compressors.txt").readlines()
        list = []
        for line in lines:
            if line != '\n':
                list.append(line)
        return list

    def get_pumps(self):
        lines = open("pumps.txt").readlines()
        list = []
        for line in lines:
            if line != '\n':
                list.append(line)
        return list

