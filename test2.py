import tkinter as tk
from tkinter import LEFT, RIGHT, ttk
from tkinter.messagebox import showinfo

root = tk.Tk()
root.title('Treeview demo')
root.geometry('900x400')
# define columns
columns = ('first_name', 'last_name', 'emaill')
frame = ttk.Frame(master=root)
tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')

# define headings
tree.heading('first_name', text='First Name')
tree.heading('last_name', text='Last Name')
tree.heading('emaill', text='Email')

def get_compressors():
        lines = open("compressors.txt").readlines()
        list = []
        for line in lines:
            if line != '\n':
                list.append(line)
        return list

def get_pumps():
    lines = open("pumps.txt").readlines()
    list = []
    for line in lines:
        if line != '\n':
            list.append(line)
    return list

# generate sample data
lines = get_compressors()
for line in lines:
    tree.insert('', tk.END, values=line.split())

contacts = []
for n in range(1, 100):
    contacts.append([f'first {n}', f'last {n}', f'email{n}@example.com'])

# add data to the treeview
for contact in contacts:
    tree.insert('', tk.END, values=contact)


def item_selected(event):
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        record = item['values']
        # show a message
        showinfo(title='Information', message=','.join(record))


tree.bind('<<TreeviewSelect>>', item_selected)

tree.pack(side=LEFT)

# add a scrollbar
scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=tk.BOTH)

frame.pack()




# run the app
root.mainloop()
