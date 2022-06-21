import serial
import serial.tools.list_ports

portList = serial.tools.list_ports.comports()

for port in portList:
    print(port)

ser = serial.Serial("COM2", 9600, timeout = 1)
print (ser.write(b'\xff'))
verdi = ser.read(1)
print(verdi)