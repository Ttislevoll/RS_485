import tkinter as tk
from tkinter import LEFT, NW, RIGHT, ttk

window = tk.Tk()
window.title("DT3005 - Serial Communication")
window.geometry('1300x900+300+50')
window.resizable(False,False)

frame_log = ttk.Frame(window)
txt_log = tk.Text(frame_log, height=31, width=60)
lbl_log = ttk.Label(frame_log, text="Log")
lbl_log.pack(anchor=NW)
txt_log.pack(side=LEFT)
scrollbar = ttk.Scrollbar(frame_log, orient=tk.VERTICAL, command=txt_log.yview)
txt_log.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=tk.BOTH)

frame_log.pack()

window.mainloop()
